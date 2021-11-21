import sys
import RPi.GPIO as GPIO
from time import time

GPP=26
GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
GPIO.setup(GPP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("Hello -- antes de presionar")
    GPIO.wait_for_edge(GPP, GPIO.FALLING)
    print("Hello -- despues de presionar")
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")
finally:
    print("clean up")
    GPIO.cleanup() # cleanup all GPIO
