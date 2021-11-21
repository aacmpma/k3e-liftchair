import os
import sys
import time 
import mariadb
import RPi.GPIO as GPIO
from datetime import datetime


# CONS 
DB_TIMEOUT = 60

# CONS EVENTS
E_RISING = "RISING"

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

def create_connection_pool():
    # Create Connection Pool
    pool = mariadb.ConnectionPool(
       user="k3e_liftchair",
       password="2de9ll3",
       host="192.168.1.32",
       port=3306,
       database="K3E_LIFTCHAIR",
       pool_name="k3e_liftchair-app",
       pool_size=13,
       connect_timeout=DB_TIMEOUT
    )
    # Return Connection Pool
    return pool

pool = create_connection_pool()
pconn = pool.get_connection()    

def add_event(device, type, gpio=0):
    try: 
        cur = pconn.cursor()
        cur.execute("INSERT INTO tb_events VALUES (NULL, now(), ?, ?, ?)", (device, type, gpio))
        pconn.close()
    except mariadb.Error as e: 
        print(f"DB Error: {e}")

def motor_fw(channel):
    print("NEW***")
    add_event("FW", E_RISING, channel)
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
    print("Connected pool...")
    add_event("FW", E_RISING, 23)
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #print("Current Time   :", current_time)
        #print("Value          :", GPIO.input(GPP))
        time.sleep(0.5)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

except mariadb.PoolError as e:
    print(f"Error opening connection from pool: {e}")
    sys.exit(1)

finally:
    print("Closing and System clean up:")
    try:
        pool.close()                        # close DB connection
        print("   ...DB closed")
    except:
        print("   ***")
    GPIO.cleanup()                          # cleanup all GPIO
    print("   ...GPIO cleanup")
