#!/bin/sh
#run this forever, if exits, restart
while true
do
    date
    /home/timc/lcd-display.py
    sleep 30
done
