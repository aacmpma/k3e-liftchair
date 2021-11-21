import os
import sys
import time 
import RPi.GPIO as GPIO
from datetime import datetime

BUZ = 18
GPP = 26
GFW = 12
GFWE = 25
GBW = 24
GBWE = 23

GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
GPIO.setup(GPP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZ, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GFW, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GFWE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GBW, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GBWE, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(GFWE, 1)
GPIO.output(GBWE, 1)

GPIO.setwarnings(True)

def motor_fw(channel):
    print("NEWWWWW")
    GPIO.output(BUZ, GPIO.HIGH)
    time.sleep(0.250)
    GPIO.output(BUZ, GPIO.LOW)
    while GPIO.input(channel):
        print("LOOP")
        GPIO.output(GFW,True)    
        time.sleep(0.1)
    else:
        GPIO.output(GFW,False)    

GPIO.add_event_detect(GPP, GPIO.RISING, callback = motor_fw, bouncetime = 200)

try:
    os.system("clear")
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #print("Current Time   :", current_time)
        #print("Value          :", GPIO.input(GPP))
        time.sleep(0.5)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

finally:
    print("clean up")
    GPIO.cleanup() # cleanup all GPIO
