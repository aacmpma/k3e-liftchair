import os
import RPi.GPIO as GPIO  
from time import sleep     # this lets us have a time delay (see line 15)  

GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  

GPSW1=22
GPSW2=27
GPSW3=17
GPBTU=19
GPBTD=26
GPCH1=13
GPCH2=21

GPIO.setup(GPSW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPSW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPSW3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPBTU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPBTD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPCH1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPCH2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
#GPIO.setup(GPSW1, GPIO.IN)
#GPIO.setup(GPSW2, GPIO.IN)
#GPIO.setup(GPSW3, GPIO.IN)
#GPIO.setup(GPBTU, GPIO.IN)
#GPIO.setup(GPBTD, GPIO.IN)
#GPIO.setup(GPCH1, GPIO.IN)
#GPIO.setup(GPCH2, GPIO.IN)

try:  
   while True:            # this will carry on until you hit CTRL+C  
        os.system('clear')
        print("**** STATUS GPIO ****")
        print("")
        print("")
        print("GPSW1 MAS ARRIBA - 22 --> " + str(GPIO.input(GPSW1)))
        print("GPSW2 MEDIO - 27 --> " + str(GPIO.input(GPSW2)))
        print("GPSW3 MAS ABAJO - 17 --> " + str(GPIO.input(GPSW3)))
        print("")
        print("GPBTU BAJAR - 19 --> " + str(GPIO.input(GPBTU)))
        print("GPBTD SUBIR - 26 --> " + str(GPIO.input(GPBTD)))
        print("")
        print("GPCH1 PIE - 13 --> " + str(GPIO.input(GPCH1)))
        print("GPCH2 SILLA - 21 --> " + str(GPIO.input(GPCH2)))
        sleep(0.050)           
  
finally:                   # this block will run no matter how the try block exits  
    GPIO.cleanup()         # clean up after yourself  
