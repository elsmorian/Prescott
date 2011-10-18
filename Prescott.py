import os.path
import serial
import struct

POLL_CMD = chr(0x02)
COARSE_CMD = chr(0x04)
FINE_CMD = chr(0x03)
ADAPT_CMD = chr(0x05)
CLEAR_CMD = chr(0x07)
SUSPEND_ENABLE_CMD = chr(0x08)
SUSPEND_DISABLE_CMD = chr(0x09)
SET_SERIAL_CMD = chr(0x2a)


class Clamp:

    Name = "Clamp"
    Version = "0.1 Dev"
    
    def __init__(self, arg1):
        if os.path.exists(arg1):
            self.serial_port = arg1
            self.ser = serial.Serial(self.serial_port,9600,timeout=5)
    
    def __str__(self):
            return "Clamp object at "+str(self.serial_port)

    def send_raw(self, cmd):
        self.ser.write(cmd)
        return self.ser.read(36)

    def poll(self):
        out = self.send_raw(POLL_CMD)
        print "OK (0xfe): "+hex(ord(out[0]))
        print "2nd Byte: "+hex(ord(out[1]))
        print "Coarse(0) / Fine(1): "+str(int(ord(out[2])))
        print "Adapting: "+str(int(ord(out[3])))
        print "Serial No: "+str(out[4:8])
        print "RMS current last second (uA): "+str(struct.unpack("<i", out[8:12])[0])
        print "Number of 1 second samples: "+str(struct.unpack("<i", out[12:16])[0])
        print "Accumulated uA-Seconds: "+str(struct.unpack("<q", out[16:24])[0])

    def set_fine(self):
        out = self.send_raw(FINE_CMD)
        print "OK (0xfd): "+hex(ord(out[0]))

    def set_coarse(self):
        out = self.send_raw(COARSE_CMD)
        print "OK (0xfc): "+hex(ord(out[0]))

    def set_adapt(self):
        out = self.send_raw(ADAPT_CMD)
        print "OK (0xfb): "+hex(ord(out[0]))

    def clear(self):
        out = self.send_raw(CLEAR_CMD)
        print "OK (0xf9): "+hex(ord(out[0]))

    def set_suspend_enable(self):
        out = self.send_raw(SUSPEND_ENABLE_CMD)
        print "OK (0xf8): "+hex(ord(out[0]))

    def set_suspend_disable(self):
        out = self.send_raw(SUSPEND_DISABLE_CMD)
        print "OK (0xf7): "+hex(ord(out[0]))

    #def set_serial_number(self):
    #   out = self.send_raw(SET_SERIAL_CMD,transid,4byteASCIIserial)
    #   print "OK (0xd6): "+hex(ord(out[0]))