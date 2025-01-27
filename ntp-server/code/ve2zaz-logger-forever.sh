#!/bin/sh
#run this forever, if exits, restart
while true
do
    date
    /home/timc/ve2zaz-logger.py
    sleep 30
done
