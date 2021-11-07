import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT)

def cont():
    print("---- Continuo ---")
    GPIO.output(24,True)
    time.sleep(5)

def step1():
    p=GPIO.PWM(24,100)
    print("---- Paso a Paso #1 ---")
    p.start(1) 
    while True:
        for i in range(100,-1,-1):
            p.ChangeDutyCycle(100 - i)
            time.sleep(0.1)
            print("Ciclo %",100-i)
        print("Ciclo completo")
        p.ChangeDutyCycle(100) 
        time.sleep(5)

def step2():
    p=GPIO.PWM(24,100)
    print("---- Paso a Paso #2 ---")
    while True:
        p.start(100) 
        time.sleep(3)
        p.ChangeDutyCycle(50) 
        time.sleep(3)
        print("Ciclo completo")

try:
    cont() 
    step1()
    step2()

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

except Exception as e:
    print("some error: " + str(e))

finally:
    print("clean up")
    GPIO.cleanup() # cleanup all GPIO
