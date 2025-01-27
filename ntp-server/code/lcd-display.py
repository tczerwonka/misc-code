#!/usr/bin/python
################################################################################
#sudo pip3 install RPLCD smbus2

################################################################################
from datetime import datetime
from time import sleep, mktime
from RPLCD.i2c import CharLCD
from gps import *

################################################################################
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

################################################################################
#now = datetime.now()
#timestring = '%0#2d:%0#2d:%0#2d' % (now.hour, now.minute, now.second)
#lcd.write_string(timestring,LCD_LINE_1)

################################################################################
def getPositionData(gps):
    nx = gpsd.next()
    #print(nx)
    #if nx['class'] == 'TPV':
    #    latitude = getattr(nx, 'lat', "Unknown")
    #    longitude = getattr(nx, 'lon', "Unknown")
    #    print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
    if nx['class'] == 'SKY':
        uSat = getattr(nx, 'uSat', "Unknown")
        lcd.cursor_pos = (1,0)
        satstring = 'SV%0#2d' % (uSat)
        #satstring = str("SV" + str(uSat))
        lcd.write_string(satstring)
################################################################################



dti = mktime(datetime.now().timetuple())
while 1:
    ndti = mktime(datetime.now().timetuple())
    if dti < ndti:
        dti = ndti
        #lcd.clear()
        lcd.home()
        lcd.cursor_pos = (0,0)
        lcd.write_string(datetime.now().strftime('%b %d  %H:%M:%S\n'))
        getPositionData(gpsd)
        sleep(0.95)
    else:
        sleep(0.01)


