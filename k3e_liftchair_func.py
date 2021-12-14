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
    GPIO.cleanup()          # cleanup all GPIO
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location

    # Input GPIO
    logging.debug("Setup GPIO IN")
    GPIO.setup(set.P_IRS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SWU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SWD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SEU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SEC, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(set.P_SCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
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
        wait_on1 = 0.5
    if type == set.B_EDG:
        wait_on1 = 0.250
        wait_off1 = 0.125
        wait_on2 = 0.250
        wait_off2 = 0.125
        wait_on3 = 0.250

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
        logging.debug("DB session close")
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
        logging.debug("DB session close")
    except mariadb.Error as e: 
        logging.error(f"DB: {e}")
    except mariadb.PoolError as e:
        logging.error(f"DB pool: {e}")


# Edge switch center
def edge_switch_center(channel):
    # Desactiva el motor
    GPIO.output(set.P_ENA, False)    

    pin_name = "P_SEC"
    logging.warning(set.E_RISING + " Channel: %s", channel)
    add_event(pin_name, set.E_RISING, channel)

def move_motor_up(channel):
    print("BOTON ARRIBA")
    if GPIO.input(channel) == False:
        return
    print("BOTON ARRIBA 11111")
    time.sleep(0.1)
    move_motor(channel)

def move_motor_down(channel):
    print("BOTON ABAJO")
    if GPIO.input(channel) == False:
        return
    print("BOTON ABAJO 11111")
    time.sleep(0.1)
    move_motor(channel)

# Move Motor
def move_motor(channel):
    # Return if the button is not pressed
    if GPIO.input(channel) == False:
        return

    ban = True    
    type_exit = 0
    type_exit_name = "---"
    
    if channel == set.P_SWU:
        pin = set.P_LPW
        pin_name = "P_LPW"
    elif channel == set.P_SWD:
        pin = set.P_RPW
        pin_name = "P_RPW"

    # Init motor     
    motor = GPIO.PWM(pin, set.M_INISPEED)

    print("*****>>>> %s", channel)
    while GPIO.input(channel):
        # Check if edge sw up/down is high and the up/down switch is press
        if GPIO.input(set.P_SEU) and channel == set.P_SWU:
            GPIO.output(set.P_ENA, False)
            type_exit = set.P_SEU
            type_exit_name = "P_SEU"
            print(">>>> 1.1")
            break
        elif GPIO.input(set.P_SED) and channel == set.P_SWD:
            motor.ChangeDutyCycle(75)
            time.sleep(0.05)
            motor.ChangeDutyCycle(50)
            time.sleep(0.05)
            motor.ChangeDutyCycle(25) 
            time.sleep(0.05)
            motor.ChangeDutyCycle(0) 
            type_exit = set.P_SED
            type_exit_name = "P_SED"
            print(">>>> 1.2")
            break
        elif GPIO.input(set.P_SCH) == False:
            motor.ChangeDutyCycle(0) 
            type_exit = set.P_SCH
            type_exit_name = "P_SCH"
            print(">>>> 1.3")
            break
        elif GPIO.input(set.P_SFO) == False:
            motor.ChangeDutyCycle(0) 
            type_exit = set.P_SFO
            type_exit_name = "P_SFO"
            print(">>>> 1.4")
            break
        else:
            GPIO.output(set.P_ENA, True)

        # Logging, event and beep start (just once)
        if ban:
            print(">>>> 2")
            ban = False
            logging.debug(set.E_RISING + " Channel: %s", channel)
            logging.debug("Values pins enable >> R: %s - L: %s", GPIO.input(set.P_REN), GPIO.input(set.P_LEN))
            logging.debug("Values pins switch edge >> U: %s - C: %s - D: %s", GPIO.input(set.P_SEU), GPIO.input(set.P_SEC), GPIO.input(set.P_SED))
            add_event(pin_name, set.E_RISING, channel)
            beep(set.P_BU1, set.B_MOT)
            motor.start(set.M_INISPEED)
            motor.ChangeDutyCycle(100) 

        # Wait
        time.sleep(0.05)

    if ban ==  False:
        # Logging, event and beep if edge sw is reached
        if type_exit != 0:
            print(">>>> 3")
            logging.debug(str(GPIO.input(type_exit)) + " " + type_exit_name)
            add_event(type_exit_name, GPIO.input(type_exit), type_exit)
            beep(set.P_BU1, set.B_EDG)
 
        # Logging and event stop
        motor.ChangeDutyCycle(0) 
        logging.debug(set.E_LOW + " Channel: %s", channel)
        add_event(pin_name, set.E_LOW, channel)
    else:
        if type_exit != 0:        
            beep(set.P_BU1, set.B_EDG)
