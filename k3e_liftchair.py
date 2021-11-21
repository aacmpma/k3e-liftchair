import os
import sys
import time 
import signal
import mariadb
import RPi.GPIO as GPIO
from datetime import datetime

# CONS EVENTS
E_SIG = 'KILL'
E_KEY = 'CTRL+C'
E_END = 'END'
E_INIT = 'INIT'

E_LOW = 'LOW'
E_HIGH = 'HIGH'
E_RISING = "RISING"
E_FALLING = "FALLING"

# CONS GPIO DEVICES
P_IRS = 4
P_RPW = 12
P_SCH = 13
P_SED = 17
P_SWU = 19
P_BU1 = 18
P_SFO = 21
P_SEU = 22
P_LEN = 23
P_LPW = 24
P_REN = 25
P_SWD = 26
P_SEC = 27

# CONS BEEP TYPES
B_RPW = 1

# Database creation pool and global variable
def create_connection_pool():
    pool = mariadb.ConnectionPool(
       user="k3e_liftchair",
       password="2de9ll3",
       host="192.168.1.32",
       port=3306,
       database="K3E_LIFTCHAIR",
       pool_name="k3e_liftchair-app",
       pool_size=13,
       connect_timeout=60
    )
    return pool

pool = create_connection_pool()
pconn = pool.get_connection()    

# ******** Functions ********

# Setup GPIO in the Raspberry
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location

    # Input GPIO
    GPIO.setup(P_IRS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SEU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SEC, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SWU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SWD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SFO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Output GPIO
    GPIO.setup(P_BU1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_RPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_LPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_REN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_LEN, GPIO.OUT, initial=GPIO.LOW)

def cleanup():
    print("Closing and System clean up:")
    GPIO.cleanup()                          # cleanup all GPIO
    print("   ...GPIO cleanup")    
    try:
        pool.close()                        # close DB connection
        print("   ...DB closed")
    except:
        print("   ***")

def signal_term_handler(signal, frame):
    add_event("K3E Lift Chair", E_SIG)
    cleanup()
    sys.exit(1)

# Beep types
def beep(channel, type):
    if type == B_RPW:
        GPIO.output(P_BU1, GPIO.HIGH)
        time.sleep(0.250)
        GPIO.output(P_BU1, GPIO.LOW)

# Insert into the table the event
def add_event(device, type, channel=0):
    try: 
        cur = pconn.cursor()
        cur.execute("INSERT INTO tb_events VALUES (NULL, now(3), ?, ?, ?)", (device, type, channel))
        pconn.close()
    except mariadb.Error as e: 
        print(f"DB Error: {e}")

# Motor Forward (right)
def motor_fw(channel):
    beep(P_BU1, B_RPW)
    add_event("P_RPW", E_RISING, channel)
    while GPIO.input(channel):
        GPIO.output(P_RPW, True)    
        time.sleep(0.1)
    else:
        GPIO.output(P_RPW, False)    
        add_event("P_RPW", E_LOW, channel)

try:
    # Catch Kill Signal
    signal.signal(signal.SIGTERM, signal_term_handler)

    os.system("clear")
    print("================================")
    print("        K3E Lift Chair          ")
    print("================================")
    add_event("K3E Lift Chair", E_INIT)

    # Setup GPIO
    setup()

    # Add event detection
    GPIO.add_event_detect(P_SWD, GPIO.RISING, callback = motor_fw, bouncetime = 200)

    #GPIO.output(P_REN, True)
    GPIO.output(P_LEN, True)

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time   :", current_time)
        time.sleep(5)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    add_event("K3E Lift Chair", E_KEY)
    print("Keyboard interrupt")

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")

except mariadb.PoolError as e:
    print(f"Error opening connection from pool: {e}")

finally:
    cleanup()

