#!/usr/bin/python2

#Thu 16 Jun 15:55:01 CDT 2022
## T. Czerwonka tczerwonka@gmail.com
##
#* * * * * /home/pi-star/airthings-2950-client.py                  

import sys
import time
import os
import platform 
#import subprocess
from subprocess import Popen, PIPE
from array import array
from socket import socket

CARBON_SERVER = '192.168.1.101'
CARBON_PORT = 2003

AIRTHINGS_SERIAL="2950039162"
READER_BIN="/home/pi-star/read_wave2.py"


sock = socket()
try:
  sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
  sys.exit(1)

line = []
carbondata = []



process = Popen([READER_BIN, AIRTHINGS_SERIAL], stdout=PIPE)
(output, err) = process.communicate()
exit_code = process.wait()

#./read_wave2.py 2950039162
#Humidity: 39.0 %rH, Temperature: 23.42 *C, Radon STA: 0 Bq/m3, Radon LTA: 0 Bq/m3

hum = output.split()[1]
tmpC = output.split()[4]
RnSTA = output.split()[8]
RnLTA = output.split()[12]

now = int( time.time() )
foo = 'airthings.humidity'
foo = ''.join(('house.environment.',foo))
carbondata.append("%s %s %d" % (foo,hum,now))

foo = 'airthings.tempF'
foo = ''.join(('house.environment.',foo))
tmpF = (float(tmpC) * 1.8) + 32
carbondata.append("%s %s %d" % (foo,tmpF,now))

now = int( time.time() )
foo = 'airthings.RnSTA'
foo = ''.join(('house.environment.',foo))
#one pCi/L equals 37 Bq/m3
RnSTA = (float(RnSTA) / 37)
carbondata.append("%s %s %d" % (foo,RnSTA,now))

now = int( time.time() )
foo = 'airthings.RnLTA'
foo = ''.join(('house.environment.',foo))
RnLTA = (float(RnLTA) / 37)
carbondata.append("%s %s %d" % (foo,RnLTA,now))


message = '\n'.join(carbondata) + '\n' #all lines must end in a newline
#print "sending message"
#print message
sock.sendall(message)

sys.exit(0)
