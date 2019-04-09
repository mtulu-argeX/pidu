
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

import time
import subprocess
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from defaults import *

# Load default font.
font = ImageFont.load_default()


#SPI or IIC
USER_I2C = 0
if  USER_I2C == 1:
    GPIO.setup(RST_PIN,GPIO.OUT)
    GPIO.output(RST_PIN,GPIO.HIGH)
    
    serial = i2c(port=1, address=0x3c)
else:
    serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
device = sh1106(serial, rotate=2) #sh1106

hexFolder='/home/pi/Desktop/HexFiles/'

uploadCmd = '/opt/arduino-1.8.7/hardware/tools/avr/bin/avrdude -C/opt/arduino-1.8.7/hardware/tools/avr/etc/avrdude.conf -v -patmega32u4 -cavr109 -P/dev/ttyACM0 -b57600 -D -Uflash:w:'
raspiDevfile = "/dev/ttyACM0"

def resetArdu():
    import serial
    ser = serial.Serial("/dev/ttyACM0", 1200)
    ser.close()
    ser.open()
    ser.close()

selecty = 0
files = os.listdir(hexFolder)
maxline = 8
maxfile = len (files)

if __name__ == "__main__":
    while True:
        curtop = top - 8 
        if not GPIO.input(KEY3_PIN):
            curentTime = time.time()
            while not GPIO.input(KEY3_PIN):
                passtime = time.time() - curentTime
                with canvas(device) as draw:
                    draw.text((1, 15), "shutting down in ",  font=font, fill=1)
                    draw.text((50, 32), "%.1f"%(3-passtime),  font=font, fill=1)
                time.sleep(0.5)
                print ("shutting Down in %f" % (3 - passtime) ) 
                if time.time() - curentTime > 3 : 
                    print("shuttingDown")
                    subprocess.check_output("shutdown -h now", shell=True)

        if not GPIO.input(KEY_DOWN_PIN): 
            selecty = ( maxfile + selecty + 1 ) % maxfile 
            time.sleep(0.2)
        if not GPIO.input(KEY_UP_PIN): 
            selecty = ( maxfile + selecty - 1 ) % maxfile 
            time.sleep(0.2)
        if not GPIO.input(KEY2_PIN):
                try:
                    with canvas(device) as draw:
                        draw.rectangle((0, 0, 128, 64), outline=255, fill=255)
                        draw.text((10, 24), "Uploading!",  font=font, fill=0)
                    resetArdu()
                    time.sleep(1.100)
                    tmpcmd = uploadCmd + hexFolder + files[selecty] + ':i'
                    subprocess.check_output(tmpcmd, shell = True )
                    with canvas(device) as draw:
                        draw.rectangle((0, 0, 128, 64), outline=255, fill=255)
                        draw.text((10, 32), "Upload Success!",  font=font, fill=0)
                    time.sleep(1.5)
                    continue 
                except:
                    with canvas(device) as draw:
                        draw.rectangle((0, 0, 128, 64), outline=255, fill=255)
                        draw.text((10, 24), "Could not upload!",  font=font, fill=0)
                        draw.text((10, 32), "Try Again!",  font=font, fill=0)
                    time.sleep(1.5)
                    continue
                    pass
            
        with canvas(device) as draw:
            if not os.path.exists(raspiDevfile):
                draw.ellipse((118,0,126,8), outline=255, fill=1)
            draw.rectangle((0, 3*8, 128, 4*8), outline=255, fill=255)
            for i in range(selecty-3,selecty+4):
                curtop = curtop + 8
                if i >= maxfile: i = i % maxfile
                if (i==selecty): 
                    draw.text((x+1, curtop), files[i].split(".")[0],  font=font, fill=0)
                else:
                    draw.text((x+1, curtop), files[i].split(".")[0],  font=font, fill=255)
    GPIO.cleanup()

