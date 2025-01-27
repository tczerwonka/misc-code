#!/usr/bin/python3

################################################################################
## 17 Jan 2025
## gpsdo-1wtemp.py
##  Client to read pi 1w temp and crap to graphite
################################################################################
#cat /sys/bus/w1/devices/10-0000003660b3/temperature 
#18929
################################################################################

import sys
import time
import os
import re
import platform 
import subprocess
import serial
from array import array
from socket import socket

WAITING = 0
READING = 1
DONE = 2
stream_state = WAITING
location = "gpsdo"


CARBON_SERVER = '192.168.1.101'
CARBON_PORT = 2003


sock = socket()
try:
    sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
    print("Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT })
    sys.exit(1)



#open serial port for reading
ser = serial.Serial('/dev/ttyAMA0', 4800, timeout=None)
#ser = serial.Serial('/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0', 9600, timeout=None)
line = []
carbondata = []
blank = ''
#reset the arduino -- the internal program waits two seconds
#ser.setDTR(False)
#time.sleep(1)
#ser.flushInput()
#ser.setDTR(True)

onewirefile = open("/sys/bus/w1/devices/10-0000003660b3/temperature", "r")
tempc = onewirefile.read()
tempc = float(tempc) / 1000
tempf = (tempc * 1.8 ) +32
now = int( time.time() )
foo = ''.join(('house.gpsdo.temperature ', str(tempf)))
carbondata.append("%s %d" % (foo,now))

message = '\n'.join(carbondata) + '\n' #all lines must end in a newline
#print("sending message\n %s" % message)
sock.sendall(message.encode())

sys.exit(0)
