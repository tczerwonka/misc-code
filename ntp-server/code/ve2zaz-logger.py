#!/usr/bin/python3

################################################################################
## 17 Jan 2025
## ve2zaz-logger.py
##  Client to read VE2ZAZ GPSDO output and log stats to grafana
##  Based on arduino-client.py and tuf2000-logger-client.py
################################################################################
#U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
#FLL status -- L/U/H/D
#alarm latch -- U/B/T/H/.
#dac value -- 14 bits 0 - 03FFF (0-16383)
#frq adjust -- +/-/=/.
#fine/coarse adjust -- C/F/.
#frq readout -- nominal 6800
#sample counter
#accumulated frequence diff
#timestamp
#holdover counter
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

################################################################################
#import mmap
#define filepath
#filepath="/tmp/gpsdo-output.txt"
 
#create file object using open function call
#file_object= open(filepath,mode="r+",encoding="utf8")
#print("Initial data in the file is:")
#print(file_object.read())
 
#create an mmap object using mmap function call
#mmap_object= mmap.mmap(file_object.fileno(),length=0,access=mmap.ACCESS_WRITE,offset=0 )
 
#write something into file
#text="Aditya is writing this text to file  "
#mmap_object.write(bytes(text,encoding="utf8"))

################################################################################

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

#the output from the TUF2000 has \r\n at the end so readline is OK here
while True:
    #turn the bytestream to a str object right away
    current_line = ser.readline().decode("utf-8")
    params=current_line.split('|')
    #print(params)

    now = int( time.time() )

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #FLL status -- L/U/H/D
    match params[0]:
        case 'L':
            value = 1
        case 'U':
            value = 2
        case 'H':
            value = 3
        case 'D':
            value = 4
        case _:
            value = 0
    foo = ''.join(('house.gpsdo.fllstatus ', str(value)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #alarm latch -- U/B/T/H/.
    match params[1]:
        case 'U':
            value = 1
        case 'B':
            value = 2
        case 'T':
            value = 3
        case 'H':
            value = 4
        case '.':
            value = 5
        case _:
            value = 0
    foo = ''.join(('house.gpsdo.alarmlatch ', str(value)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #dac value -- 14 bits 0 - 03FFF (0-16383)
    dac_value = int(params[2], 16)
    foo = ''.join(('house.gpsdo.dac_value ', str(dac_value)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #frq adjust -- +/-/=/.
    match params[3]:
        case '+':
            value = 1
        case '-':
            value = 2
        case '=':
            value = 3
        case '.':
            value = 4
        case _:
            value = 0
    foo = ''.join(('house.gpsdo.frequencyadjust ', str(value)))
    carbondata.append("%s %d" % (foo,now))



    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #fine/coarse adjust -- C/F/.
    match params[4]:
        case 'C':
            value = 1
        case 'F':
            value = 2
        case '.':
            value = 3
        case _:
            value = 0
    foo = ''.join(('house.gpsdo.adjust_fine_coarse ', str(value)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #frq readout -- nominal 6800
    tmp = int(params[5], 16)
    foo = ''.join(('house.gpsdo.frequency_readout ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #sample counter
    tmp = int(params[6], 16)
    foo = ''.join(('house.gpsdo.sample_counter ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #accumulated frequence diff
    tmp = int(params[7], 16)
    foo = ''.join(('house.gpsdo.accum_frq_diff ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))
    #but this is 2SC
    #0002 -> 2
    #FFFE -> -1
    if tmp > 32767:
        tmp = -65535 + tmp
    foo = ''.join(('house.gpsdo.accum_frq_diff_2sc ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #timestamp 
    tmp = int(params[8], 16)
    foo = ''.join(('house.gpsdo.timestamp ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))

    ########################################
    #U|U|02013|.|.|67F4|0002|FFE8|00FF|0D
    #holdover counter
    tmp = int(params[9], 16)
    foo = ''.join(('house.gpsdo.holdover_counter ', str(tmp)))
    carbondata.append("%s %d" % (foo,now))



    ########################################
    #write mmap data
    #voltage = (int(params[5],16) * 0.00048831)
    #voltagestr = '%0#5d' % voltage
    #text = params[0] + params[4]
    #print(voltage)
    #print(voltagestr)
    #print(text)
    ##text="Aditya is writing this text to file  "
    #mmap_object.write(bytes(text,encoding="utf8"))
    

    message = '\n'.join(carbondata) + '\n' #all lines must end in a newline
    #print("sending message\n %s" % message)
    sock.sendall(message.encode())
    carbondata = []
    #forever...
