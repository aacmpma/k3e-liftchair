import RPi.GPIO as GPIO
import time
import sys

GPP = int(sys.argv[1])
print("set GIOP high:", GPP)

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme

GPIO.setup(GPP, GPIO.OUT) # output rf

# Initial state for LEDs:
print("Testing RF out, Press CTRL+C to exit")

try:
	GPIO.output(GPP, GPIO.HIGH)
	time.sleep(3)               
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
	print("Keyboard interrupt")

except Exception as e:
	print("some error: " + str(e)) 

finally:
	print("clean up") 
	GPIO.cleanup() # cleanup all GPIO 
