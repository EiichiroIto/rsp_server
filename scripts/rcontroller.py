from threading import Thread
import time

class RobotController(object):
    def __init__(self, server=None):
        self.movingTime = 500 # parameter (ms)
        self.turningTime = 300 # parameter (ms)
        self.threadInterval = 200 # parameter (ms)
        self.server = server # private
        if server is not None:
            server.setController(self)
        self.thread = None # private
        self.moveTimeout = 0 # private
        self.lastMove = 'stop' # private
        self.sensors = {} # private
        self.leftPower = 100 # parameter (-100..100)
        self.rightPower = 100 # parameter (-100..100)
        self.turnRatio = 100 # parameter (0..100)
        self.balance = 50 # parameter (0..100)
        self.cameraFormat = "jpg" # "jpg" or "gif" or "png"
        self.quitLoop = False

    def start(self):
        if self.thread is not None:
            return
        self.thread = Thread(target=self.timer_thread)
        self.thread.daemon = False #True
        self.thread.start()

    def stop(self):
        self.thread = None
        time.sleep(self.threadInterval/1000.0)
        self.quitLoop = True

    def timer_thread(self):
        while self.thread is not None:
            now = int(time.time()*1000)
            if self.moveTimeout > 0 and now > self.moveTimeout:
                self.updateMove('stop')
            self.updateSensors()
            self.sendSensors()
            time.sleep(self.threadInterval/1000.0)

    def sensorUpdate(self, dic):
        for k in dic:
            key = k.encode('utf-8').lower()
            if type(dic[k]) is unicode:
                val = dic[k].encode('utf-8')
            else:
                val = str(dic[k])
            self.setVariable(key, val)

    def broadcast(self, m):
        message = m.encode('utf-8').replace(' ','').lower()
        if message == 'forward':
            self.updateMove('forward')
            self.forward()
        elif message == 'back':
            self.updateMove('back')
            self.back()
        elif message == 'left':
            self.updateMove('left')
            self.left()
        elif message == 'right':
            self.updateMove('right')
            self.right()
        elif message == 'stop':
            self.updateMove('stop')
        elif message == 'quit':
            self.stop()
            quit()
        else:
            print "broadcast(unknown):"+message

    def setVariable(self, key, val):
        key = key.replace(' ','').lower()
        if key == 'movingtime':
            self.movingTime = int(val)
        elif key == 'turningtime':
            self.turningTime = int(val)
        elif key == 'threadinterval':
            self.threadInterval = int(val)
        elif key == 'leftpower':
            self.leftPower = min(max(int(val),-100),100)
        elif key == 'rightpower':
            self.rightPower = min(max(int(val),-100),100)
        elif key == 'power':
            self.leftPower = self.rightPower = min(max(int(val),-100),100)
        elif key == 'turnRatio':
            self.turnRatio = min(max(int(val),0),100)
        elif key == 'balance':
            self.balance = min(max(int(val),0),100)
        elif key == 'cameraformat':
            if val == 'jpg' or val == 'gif' or val == 'png':
                self.cameraFormat = val
        else:
            print "setVariable(unknown):"+key+"="+val

    def updateMove(self, move):
        if move == 'stop':
            self.moveTimeout = 0
        elif move == 'forward' or move == 'back':
            self.moveTimeout = int(time.time()*1000) + self.movingTime
        elif move == 'right' or move == 'left':
            self.moveTimeout = int(time.time()*1000) + self.turningTime
        if self.lastMove != 'stop' and self.lastMove != move:
            self.stopMove()
        self.lastMove = move

    def forward(self):
        print "forward"
 
    def back(self):
        print "back"

    def left(self):
        print "left"
 
    def right(self):
        print "right"

    def stopMove(self):
        print "stop"

    def setupSensors(self, lis):
        for x in lis:
            self.sensors[x] = None

    def updateSensors(self):
        pass

    def updateSensor(self, key, val):
        self.sensors[key] = val

    def sendSensors(self):
        if self.server is None:
            return
        dic = {}
        for x in self.sensors:
            v = self.sensors[x]
            if v is not None:
                dic[x] = v
        self.server.sensorUpdate(dic)

    def testLoop(self):
        try:
            self.start()
            if self.server is not None:
                self.server.start()
            while not self.quitLoop:
		time.sleep(1)
        finally:
            if self.server is not None:
                self.server.stop()
            self.stop()

if __name__ == '__main__':
    c = RobotController(None)
    c.movingTime = 1500
    try:
        c.start()
        for x in range(20):
            print x
            if x == 0:
                c.broadcast('forward')
            elif x == 3:
                c.sensorUpdate({'movingTime': 5000})
                c.broadcast('right')
            elif x == 6:
                c.broadcast('right')
            elif x == 9:
                c.broadcast('left')
            time.sleep(1)
    finally:
        c.stop()
