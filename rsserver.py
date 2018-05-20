import socket
import select
import struct
from threading import Thread
import time
import rsparse
import doctest
import base64

def makeSensorDict(lis):
  """
  >>> makeSensorDict(['a', 1, 'b', 2])
  {'a': 1, 'b': 2}
  """
  dic = {}
  for i in range(len(lis)/2):
    dic[lis[i*2]] = lis[i*2+1]
  return dic

def makeHeader(message):
  size = len(message)
  a3 = size % 256
  a2 = (size >> 8) % 256
  a1 = (size >> 16) % 256
  a0 = (size >> 24) % 256
  return struct.pack("B"*4, a0, a1, a2, a3)

class RemoteSensorServer:
  def __init__(self, host='127.0.0.1', port=42001):
    self.host = host
    self.port = port
    self.sensors = {}
    self.socket = None
    self.controller = None

  def setController(self, controller):
    self.controller = controller

  def start(self):
    if self.socket is not None:
      return
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.clients = set([self.socket])
    self.thread = Thread(target=self.server_thread)
    self.thread.daemon = True
    self.thread.start()

  def server_thread(self):
    print "server_thread"
    backlog = 10
    bufsize = 4096
    try:
      self.socket.bind((self.host, self.port))
      self.socket.listen(backlog)
      print "Start select"
      while self.socket is not None:
        rready, wready, xready = select.select(self.clients, [], [], 1)
        for sock in rready:
          if sock is self.socket:
            conn, address = self.socket.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.clients.add(conn)
            message = self.makeSensorUpdate(self.sensors, True)
            if message != "":
              conn.send(message)
          else:
            msg = sock.recv(4)
            if len(msg) == 0:
              self.detachClient(sock)
            else:
              a = struct.unpack("B"*4, msg)
              sz = a[3]+(a[2]<<8)+(a[1]<<16)+(a[0]<<24)
              print sz
              msg = sock.recv(sz)
              if len(msg) == 0:
                self.detachClient(sock)
              else:
                print msg+"!"
                self.dispatchMessage(msg)
    finally:
      self.stop()

  def detachClient(self, socket):
    print "detachClient"
    socket.close()
    self.clients.remove(socket)

  def stop(self):
    print "RemoteSensorServer stop"
    if self.socket is None:
      return
    self.socket = None
    for socket in self.clients:
      socket.close()
    self.clients = set()

  def isRunning(self):
    return self.socket is not None

  def dispatchMessage(self, message):
    if self.controller is None:
      return
    text = unicode(message, 'utf-8')
    command, lis = rsparse.parseMessage(text)
    if command == 'sensor-update':
      dic = makeSensorDict(lis)
      self.controller.sensorUpdate(dic)
    elif command == 'broadcast':
      self.controller.broadcast(lis[0])

  def makeSensorUpdate(self, dic, forceAll=False):
    message = ""
    for x in dic:
      v = dic[x]
      if not (x in self.sensors) or (v != self.sensors[x]) or forceAll:
        if type(v) is str:
          v = '"'+v+'"'
        message += ' '+x+' '+str(v)+''
      self.sensors[x] = v
    if message == "":
      return ""
    message = "sensor-update"+message
    message = message.encode('utf-8')
    return makeHeader(message)+message

  def send(self, message):
    if message != "":
      for socket in self.clients:
        if socket is not self.socket:
          socket.send(message)
#          print "sent message:"+message

  def sensorUpdate(self, dic):
    message = self.makeSensorUpdate(dic)
    self.send(message)

  def makeCamera(self, image):
    message = self.controller.cameraFormat+" "+base64.b64encode(image)
    message = message.encode('utf-8')
    return makeHeader(message)+message

  def camera(self, image):
    message = self.makeCamera(image)
    self.send(message)

  def test(self):
    # To test, enter following code in python shell.
    # % python
    # >>> import rsserver
    # >>> s = rsserver.RemoteSensorServer('')
    # >>> s.test()
    # Then start mesh-enabled Scratch and connect to this machine
    # using Share-Join Mesh menu.
    self.start()
    ret = ""
    while ret != "q":
      ret = raw_input("'q' to quit>")
    self.stop()
    quit()

if __name__ == "__main__":
    doctest.testmod()
