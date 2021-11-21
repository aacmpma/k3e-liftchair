import RPi.GPIO as GPIO  
import time
GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
presses = 1

def my_callback(channel): 
    global presses
    print "callback called " + str(presses) + " times"
    presses += 1
    

GPIO.add_event_detect(26, GPIO.FALLING, callback=my_callback, bouncetime=100)

print "Waiting"  
while True:
    try:  
        time.sleep(5)
    except KeyboardInterrupt:  
        GPIO.cleanup()
        break
