import serial
import struct
import time
import doctest

def getChVal(h, l):
    """
    >>> getChVal(0,127)
    (0, 127)
    >>> getChVal(10,64)
    (1, 320)
    >>> getChVal(40,50)
    (5, 50)
    >>> getChVal(127,127)
    (15, 1023)
    """
    ch = (h & 0x78) >> 3
    val = ((h & 0x07) << 7) | (l & 0x7F)
    return ch, val

def toGeneric(rawValue):
    """
    >>> toGeneric(0)
    0
    >>> toGeneric(1023)
    100
    >>> toGeneric(500)
    49
    """
    return int(round(rawValue * 100.0 / 1023.0))

def toLight(rawValue):
    """
    >>> toLight(0)
    100
    >>> toLight(20)
    80
    >>> toLight(100)
    69
    >>> toLight(660)
    27
    >>> toLight(800)
    17
    >>> toLight(1023)
    0
    """
    if rawValue < 25:
        return 100 - rawValue
    else:
        return int(round((1023 - rawValue) * 75.0 / 998.0))

def toSound(rawValue):
    """
    >>> toSound(0)
    0
    >>> toSound(18)
    0
    >>> toSound(20)
    1
    >>> toSound(60)
    21
    >>> toSound(80)
    27
    >>> toSound(500)
    81
    >>> toSound(780)
    100
    >>> toSound(1023)
    100
    """
    v = max(0, rawValue - 18)
    if v < 50:
        return int(round(v / 2.0))
    else:
        return 25 + int(round(min(75, (v - 50) * 75.0 / 580.0)))

def getSensors(buf):
    """
    >>> getSensors([0,0])
    {'resistanceD': 0}
    >>> getSensors([10,64])
    {'resistanceC': 31}
    >>> getSensors([40,50])
    {'light': 73}
    >>> getSensors([0,0,10,64])
    {'resistanceC': 31, 'resistanceD': 0}
    """
    sensors = {}
    for i in range(len(buf) / 2):
        ch, val = getChVal(buf[i*2], buf[i*2+1])
        if ch == 0:
            sensors['resistanceD'] = toGeneric(val)
        elif ch == 1:
            sensors['resistanceC'] = toGeneric(val)
        elif ch == 2:
            sensors['resistanceB'] = toGeneric(val)
        elif ch == 3:
            sensors['button'] = toGeneric(val)
        elif ch == 4:
            sensors['resistanceA'] = toGeneric(val)
        elif ch == 5:
            sensors['light'] = toLight(val)
        elif ch == 6:
            sensors['sound'] = toSound(val)
        elif ch == 7:
            sensors['slider'] = toGeneric(val)
        elif ch == 15:
            sensors['firmwareId'] = val
    return sensors

def toMotor(power):
    """
    >>> toMotor(0)
    0
    >>> toMotor(40)
    3
    >>> toMotor(50)
    4
    >>> toMotor(100)
    7
    """
    return int(round(max(7.0 / 100 * min(abs(power), 100), 0)))

class ScratchSensorBoard():
    def __init__(self, device='', baudrate=38400):
        self.setDevice(device)
        self.setBaudrate(baudrate)
        self.ser = None
        self.command = 0

    def setDevice(self, device):
        self.device = device

    def setBaudrate(self, baudrate):
        self.baudrate = baudrate

    def start(self):
        if self.ser is not None:
            return
        try:
            self.ser = serial.Serial(self.device, self.baudrate, timeout=0.1)
        except:
            print "serial open error:"+self.device
            quit()

    def stop(self):
        if self.ser is None:
            return
        self.ser.close()
        self.ser = None

    def poll(self):
        if self.ser is None:
            return {}
        self.ser.write(struct.pack("B"*1, self.command))
        l = self.ser.inWaiting()
        if l == 0:
            return {}
        buf = self.ser.read(l)
        buf = struct.unpack("b"*l, buf)
        return getSensors(buf)

    def powerMotorA(self, power):
        self.command &= 0x0F
        self.command |= toMotor(power)<<4
        self.command |= (0x80 if power > 0 else 0)

    def powerMotorB(self, power):
        self.command &= 0xF0
        self.command |= toMotor(power)
        self.command |= (0x08 if power > 0 else 0)

if __name__ == "__main__":
    doctest.testmod()
