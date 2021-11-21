import os
import sys
import time 
import signal
import mariadb
import logging
import RPi.GPIO as GPIO
from datetime import datetime

# CONS EVENTS
E_SIG = 'KILL'
E_KEY = 'CTRL+C'
E_END = 'END'
E_INI = 'INIT'

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

# level=logging.DEBUG or logging.INFO or logging.WARNING or logging.ERROR or logging.CRITICAL
logging.basicConfig(filename=os.path.splitext(os.path.basename(__file__))[0]+".log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s (%(funcName)s::%(threadName)s[%(lineno)d]): %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info(E_INI)

# Database creation pool and global variable
def create_connection_pool():
    try:
        logging.debug("DB create pool connection")
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
        logging.debug("DB pool name: %s", pool.pool_name)
        return pool
    except Exception as e:
        logging.error(f"DB Error: {e}")
        sys.exit(1)

pool = create_connection_pool()
pconn = pool.get_connection()

# ************************************************ Functions ************************************************

# Setup GPIO in the Raspberry
def setup():
    logging.debug("Setup GPIO")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location

    # Input GPIO
    logging.debug("Setup GPIO IN")
    GPIO.setup(P_IRS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SEU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SEC, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SWU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SWD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(P_SFO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Output GPIO
    logging.debug("Setup GPIO OUT")
    GPIO.setup(P_BU1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_RPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_LPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_REN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(P_LEN, GPIO.OUT, initial=GPIO.LOW)

# Cleanup GPIO and DB connection
def cleanup():
    logging.info(E_END)
    logging.debug("Closing and System clean up:")
    GPIO.cleanup()                          # cleanup all GPIO
    logging.debug("GPIO cleanup")    
    try:
        pool.close()                        # close DB connection
        logging.debug("DB closed")
    except:
        logging.debug("***")

# Catch kill signal
def signal_term_handler(signal, frame):
    logging.info(E_SIG)
    add_event("K3E Lift Chair", E_SIG)
    cleanup()
    sys.exit(1)

# Beep types
def beep(channel, type):
    if type == B_RPW:
        GPIO.output(P_BU1, GPIO.HIGH)
        logging.debug("Beep in channel %s type: %s", channel, type)
        time.sleep(0.250)
        GPIO.output(P_BU1, GPIO.LOW)
        logging.debug("Beep in channel %s off")

# Insert into the table the event
def add_event(device, type, channel=0):
    try: 
        cur = pconn.cursor()
        cur.execute("INSERT INTO tb_events VALUES (NULL, now(3), ?, ?, ?)", (device, type, channel))
        logging.debug("SQL: %s %s, %s, %s", cur.statement, device, type, channel)
        pconn.close()
        logging.debug("DB pool close")
    except mariadb.Error as e: 
        logging.error(f"DB Error: {e}")

# Motor Forward (right)
def motor_fw(channel):
    beep(P_BU1, B_RPW)
    logging.debug(E_RISING + ' Channel: %s', channel)
    logging.debug("Values pins enable R: %s - L: %s", GPIO.input(P_REN), GPIO.input(P_LEN))
    add_event("P_RPW", E_RISING, channel)
    while GPIO.input(channel):
        GPIO.output(P_RPW, True)    
        time.sleep(0.1)
    else:
        GPIO.output(P_RPW, False)    
        logging.debug(E_LOW + ' Channel: %s', channel)
        add_event("P_RPW", E_LOW, channel)

try:
    # Catch Kill Signal
    signal.signal(signal.SIGTERM, signal_term_handler)

    add_event("K3E Lift Chair", E_INI)
    os.system("clear")
    print("================================")
    print("        K3E Lift Chair          ")
    print("================================")

    # Setup GPIO
    setup()

    # Add event detection
    GPIO.add_event_detect(P_SWD, GPIO.RISING, callback = motor_fw, bouncetime = 200)

    GPIO.output(P_REN, True)
    GPIO.output(P_LEN, True)

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time   :", current_time)
        time.sleep(5)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    logging.info(E_KEY)
    add_event("K3E Lift Chair", E_KEY)
    print("Keyboard interrupt")

except mariadb.Error as e:
    logging.error(f"Error connecting to MariaDB Platform: {e}")

except mariadb.PoolError as e:
    logging.error(f"Error opening connection from pool: {e}")

finally:
    cleanup()
