#!/usr/bin/env python

from Prescott import Clamp, ClampArray
import time
import os
import serial
import struct
import re
import sys

CONST_CLAMP_RATING = 50
#ideal NOTIFY_DIFF seems to be half device rated wattage for old-style lightbulbs
NOTIFY_DIFF = 30
LOOP_TIME = 1


def poll_clamps(clamparray):
    clamplist = []
    for clamp in clamparray:
        tmpdict = {
                'port':clamp.serial_port,
                'serial':clamp.serial_number,
                'power':clamp.get_power_last_second()
                }
        clamplist.append(tmpdict)
    return clamplist

def diff(arg1, arg2):
    return abs(arg1-arg2)


clamps = ClampArray("auto", "/dev/", CONST_CLAMP_RATING)
print str(clamps)

firstloop = True
oldlist = []
newlist = []

while (True):
    if firstloop:
        newlist = oldlist = poll_clamps(clamps)
        firstloop = False
    else:
        oldlist = newlist
        newlist = poll_clamps(clamps)
    for i in range(0, len(newlist)):
        oldpow = oldlist[i]['power']
        newpow = newlist[i]['power']
        powdiff = diff(oldpow, newpow)
        if (powdiff >= NOTIFY_DIFF):
            print "Sensor "+oldlist[i]['serial']+" on "+oldlist[i]['port']+" changed by: "+str(powdiff)+"W!"
            print "Sensor "+oldlist[i]['serial']+" was: "+str(oldpow)+"W, now: "+str(newpow)+"W."
    time.sleep(LOOP_TIME)
    

sys.exit()