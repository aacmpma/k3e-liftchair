import os
import sys
import time 
import mariadb
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
    print("NEW***2")
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
    #os.system("clear")
    conn = mariadb.connect(user="k3e_liftchair1", password="2de9ll3", host="192.0.1.32", port=3306, database="K3E_LIFTCHAIR")
    print("Connected...", flush=True)
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time   :", current_time)
        print("Value          :", GPIO.input(GPP), flush=True)
        time.sleep(0.5)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

finally:
    print("System clean up...")
    GPIO.cleanup() # cleanup all GPIO
