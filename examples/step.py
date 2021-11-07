import RPi.GPIO as GPIO
import time

GFW = 20
GBW = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(GFW,GPIO.OUT)
GPIO.setup(GBW,GPIO.OUT)

def cont():
    print("---- Continuo ---")
    GPIO.output(GFW,True)
    time.sleep(3)
    GPIO.output(GFW,False)
    time.sleep(10)
    GPIO.output(GFW,True)
    time.sleep(3)
    GPIO.output(GFW,False)
    time.sleep(2)

def step1():
    dir = 0
    print("---- Paso a Paso #1 ---")
    while True:
        print("Inicia Ciclo")
        if(dir == 0):
            dir = 1
            p=GPIO.PWM(GFW,100)
        else:
            dir = 0
            p=GPIO.PWM(GBW,100)
        p.start(1) 
        for i in range(1,100,1):
            p.ChangeDutyCycle(abs((100*dir)-i))
            time.sleep(0.1)
            print("Ciclo %",abs((100*dir)-i))
        print("Ciclo completo",dir)
        time.sleep(5)

def step2():
    p=GPIO.PWM(GFW,100)
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
