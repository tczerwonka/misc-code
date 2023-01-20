#!/usr/bin/python3
################################################################################
#program to check radon values and turn on/off fan
#have a minimum on time -- no short cycling -- once it's on -- it's on for N hrs.

#check radon value
#if value > 2 (arbitrary)

#   check if fan is on
#       if fan on exit
#   else
#       turn on fan
#       set turnon time

#if value < 2 (arbitrary)
#   check if fan is off
#       if fan off exit
#   else
#       if on for < 6hrs (arbitrary)
#           exit
#       else
#       turn off fan
################################################################################
#goes in crontab
#* * * * * /home/timc/misc-code/radon-control/radon-control.py
################################################################################
#2022 T Czerwonka tczerwonka@gmail.com
################################################################################
import sys
import os
import time
from socket import socket
import requests

statshost='192.168.1.101:8080'
metric='house.environment.airthings.RnSTA'
radon_trigger=2       #if 2 or over turn on fan

fan_control_url='http://192.168.1.41/cm?cmnd='
fan_relay='POWER1'
#for testing, POWER2 is the aux, POWER1 is the radon system

fan_on_file='/home/timc/radon_fan_ontime'
#fan_on_file='/home/timc/radon_fan_ontime2'
fan_minimum_duration=21600

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003
fan_status_metric = 'house.environment.radonfan.status'

sock = socket()
try:
    sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
    print("Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT })



################################################################################
#report fan status
################################################################################
def report_fan_status(status):
    now = str(int( time.time() ))
    message = fan_status_metric + ' ' + str(status) + ' ' + now
    message = ''.join(message) + '\n' #all lines must end in a newline
    #print("sending message")
    #print(message)
    sock.sendall(message.encode())







################################################################################
#get the latest radon stats
#curl -X GET 192.168.1.101:8080/render?target=house.environment.airthings.RnSTA\&from=-1min\&format=json
#[{'target': 'house.environment.airthings.RnSTA', 'tags': {'name': 'house.environment.airthings.RnSTA'}, 'datapoints': [[1.13513513514, 1655941200]]}]
################################################################################
def check_radon_value():
    base_url='http://'
    base_url= ''.join([base_url, statshost])
    base_url= ''.join([base_url, '/render?target='])
    base_url= ''.join([base_url, metric])
    base_url= ''.join([base_url, '&from=-2min&format=json'])
    r = requests.get(base_url)
    data = r.json()[0]
    radon_level = data['datapoints'][0][0]

    if (radon_level >= radon_trigger):
        print("Rn value %s exceeds %s" % ( radon_level, radon_trigger))
        return 1
    else:
        return 0



################################################################################
#check the current power state of the fan
################################################################################
def check_fan_state():
    base_url= ''.join([fan_control_url, fan_relay])
    r = requests.get(base_url)
    data = r.json()
    if (data[fan_relay] == 'ON'):
        return(1)
    else:
        return(0)




################################################################################
#set the current power state of the fan
################################################################################
def set_fan_state(state):
    base_url= ''.join([fan_control_url, fan_relay])
    base_url= ''.join([base_url, '%20'])
    base_url= ''.join([base_url, state])
    r = requests.get(base_url)
    print("\tset fan %s" % (state))



################################################################################
#write current time in file
################################################################################
def write_fan_state_file():
    now = str(int(( time.time() )))
    f = open(fan_on_file, "w")
    f.write(now)
    f.close()



################################################################################
#read current time in file
################################################################################
def read_fan_state_file():
    f = open(fan_on_file, "r")
    return(int(f.read()))



################################################################################
#fan_status:
#   0 - off
#   1 - on
#   2 - holdoff
################################################################################
def main():
    if (check_radon_value()):
        #radon is high, check fan state
        if (check_fan_state() == 1):
            #state is high, exit
            print("\tfan already on, exiting.")
            report_fan_status(1)
            #fan status file being updated because turn off needs to happen
            #N minutes AFTER the value drops
            write_fan_state_file()
            sys.exit(0)
        else:
            #radon high - turn fan on
            report_fan_status(1)
            set_fan_state('on')
            write_fan_state_file()
    else:
        #radon is low, check fan state
        if (check_fan_state() == 0):
            print("Rn low, fan off, exiting.")
            #fan off, radon low, do nothing
            report_fan_status(0)
            sys.exit(0)
        else:
            #fan on, radon low, turn off fan IFF on for at least holdoff
            now = int(( time.time() ))
            fan_on_time = (now - read_fan_state_file())
            if (fan_on_time < fan_minimum_duration):
                print("Rn below threshhold, fan on for %ss, %ss remaining, exiting." % (fan_on_time, (fan_minimum_duration - fan_on_time)))
                report_fan_status(2)
                sys.exit(0)
            else:
                print("Rn below threshhold, turning fan off.")
                report_fan_status(0)
                set_fan_state('off')
                sys.exit(0)

    sys.exit(0)




if __name__ == "__main__":
    main()
