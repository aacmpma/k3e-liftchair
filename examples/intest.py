import RPi.GPIO as GPIO  
GPP = 18
from time import sleep     # this lets us have a time delay (see line 15)  
GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(GPP, GPIO.IN)    # set GPIO25 as input (button)  
GPIO.setup(GPP, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.OUT)   # set GPIO24 as an output (LED)  
  
try:  
   while True:            # this will carry on until you hit CTRL+C  
        if GPIO.input(GPP): # if port 25 == 1  
            print "Port GPP is 1/HIGH/True - LED ON"  
            GPIO.output(24, 1)         # set port/pin value to 1/HIGH/True  
        else:  
            print "Port GPP is 0/LOW/False - LED OFF"  
            GPIO.output(24, 0)         # set port/pin value to 0/LOW/False  
        sleep(0.1)         # wait 0.1 seconds  
  
finally:                   # this block will run no matter how the try block exits  
    GPIO.cleanup()         # clean up after yourself  
