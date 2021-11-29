import sys
import time
import mariadb
import logging
import RPi.GPIO as GPIO
#  *** IMPORTS LOCALS ***
import k3e_liftchair_settings as set


# Database connection and creation pool
def create_connection_pool():
    try:
        logging.debug("DB create pool connection")
        set.pool = mariadb.ConnectionPool(
            user="k3e_liftchair",
            password="2de9ll3",
            host="192.168.1.32",
            port=3306,
            database="K3E_LIFTCHAIR",
            pool_name="pool_k3e_liftchair",
            pool_size=4,
            connect_timeout=30
        )
        logging.debug("DB pool name: %s", set.pool.pool_name)
    except Exception as e:
        logging.error(f"DB Error: {e}")
        sys.exit(1)


# Setup GPIO in the Raspberry
def setupGPIO():
    logging.debug("Setup GPIO")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location

    # Input GPIO
    logging.debug("Setup GPIO IN")
    GPIO.setup(set.P_IRS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SEU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SEC, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SWU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SWD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SFO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Output GPIO
    logging.debug("Setup GPIO OUT")
    GPIO.setup(set.P_BU1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(set.P_RPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(set.P_LPW, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(set.P_REN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(set.P_LEN, GPIO.OUT, initial=GPIO.LOW)

    # Enable/Disable Motor
    GPIO.output(set.P_REN, True)
    GPIO.output(set.P_LEN, True)


# Cleanup GPIO and DB connection
def cleanup():
    logging.debug("Closing and system clean up")
    GPIO.cleanup()                          # cleanup all GPIO
    logging.debug("GPIO cleanup")    
    try:
        set.pool.close()                        # close DB connection
        logging.debug("DB closed")
    except:
        logging.debug("***")
    logging.info(set.E_END)


# Control-C
def ctrl_c(tcb):
    print("Keyboard interrupt... Closing...")
    logging.info(set.E_KEY)
    add_event("K3E Lift Chair", set.E_KEY)
    set.exit_thread_check_battery = True
    tcb.join()


# Catch kill signal
def signal_term_handler(signal, frame):
    logging.info(set.E_SIG)
    add_event("K3E Lift Chair", set.E_SIG)
    cleanup()
    sys.exit(1)


# Beep types
def beep(channel, type):
    wait_on1 = 0
    wait_off1 = 0
    wait_on2 = 0
    wait_off2 = 0
    wait_on3 = 0

    if type == set.B_MOT:
        wait_on1 = 0.250
    if type == set.B_EDG:
        wait_on1 = 0.250
        wait_off1 = 0.250
        wait_on2 = 0.125
        wait_off2 = 0.125
        wait_on3 = 0.125

    logging.debug("Beep in channel %s type: %s", channel, type)
    GPIO.output(channel, GPIO.HIGH)
    time.sleep(wait_on1)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(wait_off1)
    GPIO.output(channel, GPIO.HIGH)
    time.sleep(wait_on2)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(wait_off2)
    GPIO.output(channel, GPIO.HIGH)
    time.sleep(wait_on3)
    GPIO.output(channel, GPIO.LOW)
    logging.debug("Beep in channel %s off", channel)


# Insert into the table the event
def add_event(device, type, channel=0):
    try: 
        cur = set.pconn.cursor()
        cur.execute("INSERT INTO tb_events VALUES (NULL, now(3), ?, ?, ?)", (device, type, channel))
        logging.debug("SQL: %s %s, %s, %s", cur.statement, device, type, channel)
        set.pconn.close()
        logging.debug("DB pool close")
    except mariadb.Error as e: 
        logging.error(f"DB: {e}")
    except mariadb.PoolError as e:
        logging.error(f"DB pool: {e}")


# Insert into the table the charging values
def add_charging(device, vin, vout, sv, sc, pw, pr):
    try: 
        cur = set.pconn.cursor()
        cur.execute("INSERT INTO tb_charging VALUES (NULL, now(3), ?, ?, ?, ?, ?, ?, ?)", (device, vin, vout, sv, sc, pw, pr))
        logging.debug("SQL: %s %s, %s, %s, %s %s, %s, %s", cur.statement, device, vin, vout, sv, sc, pw, pr)
        set.pconn.close()
        logging.debug("DB pool close")
    except mariadb.Error as e: 
        logging.error(f"DB: {e}")
    except mariadb.PoolError as e:
        logging.error(f"DB pool: {e}")


# Edge switch
def edge_switch(channel):
    pin_name = None
    if channel == set.P_SEU:
        pin_name == "P_SEU"
    elif channel == set.P_SEC:
        pin_name == "P_SEC"
    elif channel == set.P_SED:
        pin_name == "P_SED"
    logging.debug(set.E_RISING + " Channel: %s", channel)
    add_event(pin_name, set.E_RISING, channel)


# Move Motor
def move_motor(channel):
    pin_ena = set.P_LEN
    if channel == set.P_SWU:
        pin = set.P_LPW
        pin_name = "P_LPW"
    elif channel == set.P_SWD:
        pin = set.P_RPW
        pin_name = "P_RPW"

    logging.debug(set.E_RISING + " Channel: %s", channel)
    logging.debug("Values pins enable >> R: %s - L: %s", GPIO.input(set.P_REN), GPIO.input(set.P_LEN))
    logging.debug("Values pins switch edge >> U: %s - C: %s - D: %s", GPIO.input(set.P_SEU), GPIO.input(set.P_SEC), GPIO.input(set.P_SED))
    add_event(pin_name, set.E_RISING, channel)

    beep(set.P_BU1, set.B_MOT)

    GPIO.output(pin_ena, True)
    motor=GPIO.PWM(pin, set.M_INISPEED)

    while GPIO.input(channel):
        # if GPIO.input(P_SEU) and channel == P_SWU:
        #     logging.debug(E_HIGH + " SW EDGE UP")
        #     add_event("P_SEU", E_HIGH, P_SEU)
        #     beep(P_BU1, B_EDG)
        #     slow_stop(M_INISPEED, motor)
        #     break
        # if GPIO.input(P_SED) and channel == P_SWD:
        #     logging.debug(E_HIGH + " SW EDGE DOWN")
        #     add_event("P_SED", E_HIGH, P_SED)
        #     beep(P_BU1, B_EDG)
        #     slow_stop(M_INISPEED, motor)
        #     break
        motor.start(set.M_INISPEED)
        time.sleep(0.1)

    GPIO.output(pin, False)
    logging.debug(set.E_LOW + " Channel: %s", channel)
    add_event(pin_name, set.E_LOW, channel)


# Slow stop
def slow_stop(vel, motor):
    logging.debug("SLOW DOWN STOP - INI SPEED %s", vel)
    for i in range(vel, 0, -1):
        motor.ChangeDutyCycle(i)
        time.sleep(0.008)