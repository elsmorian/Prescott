import os
import serial
import struct
import re

POLL_CMD = chr(0x02)
COARSE_CMD = chr(0x04)
FINE_CMD = chr(0x03)
ADAPT_CMD = chr(0x05)
CLEAR_CMD = chr(0x07)
SUSPEND_ENABLE_CMD = chr(0x08)
SUSPEND_DISABLE_CMD = chr(0x09)
SET_SERIAL_CMD = chr(0x2a)

CONST_VOLTAGE = 240
CONST_POWER_FACTOR = 0.98

CLAMP_TTY = '^ttyACM[0-9]{1,4}$'

class Clamp:

    Name = "Clamp"
    Version = "0.2 Dev"
    
    def __init__(self, arg1, arg2):
        if os.path.exists(arg1):
            self.clamp_rating = arg2
            self.serial_port = arg1
            self.ser = serial.Serial(self.serial_port,115200,timeout=5)
            self.ser.nonblocking()
            self.serial_number = self.get_serial_number()
        #else:
        #   print "Clamp not found"
    
    def __str__(self):
            return "Clamp "+self.serial_number+" at "+str(self.serial_port)

    def send_raw(self, cmd):
        self.open_clamp()
        self.ser.write(cmd)
        rtn = self.ser.read(36)
        self.close_clamp()
        if len(rtn) > 2:
            return rtn
        else:
            print "RX data not long enough, retrying.."
            #self.close_clamp()
            #self.open_clamp()
            #return self.send_raw(cmd)

    def close_clamp(self):
        #print "clamp closed!"
        self.ser.close()

    def open_clamp(self):
        #print "clamp opened!"
        self.ser.open()

    def get_current_last_second(self):
        out = self.send_raw(POLL_CMD)
        if hex(ord(out[0])) == '0xfe':
            return struct.unpack("<i", out[8:12])[0]

    def get_power_last_second(self):
        cur = self.get_current_last_second()
        #print str(cur)
        cura = cur / float(10**6)
        #print str(cura)
        curaa = cura * CONST_VOLTAGE * CONST_POWER_FACTOR
        if (self.clamp_rating == 50):
            curaa = curaa * 2
        return curaa

    def get_kwh(self):
        power_secs = self.get_accumulated_current_seconds() * CONST_VOLTAGE * CONST_POWER_FACTOR
        return power_secs / float(3600 * 1000 * 10**6)

    def get_accumulated_current_seconds(self):
        out = self.send_raw(POLL_CMD)
        if hex(ord(out[0])) == '0xfe':
            return struct.unpack("<q", out[16:24])[0]

    def get_serial_number(self):
        out = self.send_raw(POLL_CMD)
        if hex(ord(out[0])) == '0xfe':
            return str(out[4:8])

    def poll(self):
        out = self.send_raw(POLL_CMD)
        print "OK (0xfe): "+hex(ord(out[0]))
        if hex(ord(out[0])) == '0xfe':
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
        if hex(ord(out[0])) == '(0xf9)':
            return 1

    def set_suspend_enable(self):
        out = self.send_raw(SUSPEND_ENABLE_CMD)
        print "OK (0xf8): "+hex(ord(out[0]))

    def set_suspend_disable(self):
        out = self.send_raw(SUSPEND_DISABLE_CMD)
        print "OK (0xf7): "+hex(ord(out[0]))

    #def set_serial_number(self):
    #   out = self.send_raw(SET_SERIAL_CMD,transid,4byteASCIIserial)
    #   print "OK (0xd6): "+hex(ord(out[0]))


class ClampArray:

    Name = "ClampArray"
    Version = "0.1 Dev"
    
    def __init__(self, method, search_dir, rating):
        self.clamp_rating = rating
        self.clamp_array = []
        if method == "auto":
            clamp_re = re.compile(CLAMP_TTY)
            self.clamp_ports = []
            for root, dirnames, filenames in os.walk(search_dir):
                for filename in filenames:
                    if clamp_re.match(filename):
                        self.clamp_ports.append(search_dir+filename)
            #print self.clamp_ports
            for port in self.clamp_ports:
                clamp = Clamp(port, self.clamp_rating)
                self.clamp_array.append(clamp)
            self.it_current = 0
            self.it_max = len(self.clamp_array)-1
        else:
            print "Auto not used"
        
    def __iter__(self):
        return self

    def next(self):
        if self.it_current > self.it_max:
            self.it_current = 0
            raise StopIteration
        else:
            self.it_current += 1
            #print "iterated!"
            return self.clamp_array[self.it_current-1]

    def __str__(self):
        mystr = ""
        for clamp in self:
            mystr += ", "+str(clamp)
        return "An array of "+str(self.clamp_rating)+"A clamp meters"+mystr

    def __len__(self):
        return len(self.clamp_array)
