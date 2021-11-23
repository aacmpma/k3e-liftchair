import os
import sys
import time 
import board
import signal
import mariadb
import logging
import threading
import RPi.GPIO as GPIO
from datetime import datetime
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

# CONS BEEP TYPES
B_MOT = 1

# CONS EVENTS
E_SIG = 'KILL'
E_KEY = 'CTRL+C'
E_END = 'END'
E_INI = 'INIT'

E_LOW = 'LOW'
E_HIGH = 'HIGH'
E_RISING = "RISING"
E_FALLING = "FALLING"

E_CURRENT = "CURRENT"
E_CHARGING = "CHARGING"
E_NOCURRENT = "NO CURRENT"

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

# level=logging.DEBUG or logging.INFO or logging.WARNING or logging.ERROR or logging.CRITICAL
logging.basicConfig(filename=os.path.splitext(os.path.basename(__file__))[0]+".log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s (%(funcName)s::%(threadName)s[%(lineno)d]): %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info("")
logging.info("************************* " + E_INI + " *************************")

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
            pool_size=4,
            connect_timeout=30
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
    if type == B_MOT:
        GPIO.output(P_BU1, GPIO.HIGH)
        logging.debug("Beep in channel %s type: %s", channel, type)
        time.sleep(0.250)
        GPIO.output(P_BU1, GPIO.LOW)
        logging.debug("Beep in channel %s off", channel)

# Insert into the table the event
def add_event(device, type, channel=0):
    try: 
        cur = pconn.cursor()
        cur.execute("INSERT INTO tb_events VALUES (NULL, now(3), ?, ?, ?)", (device, type, channel))
        logging.debug("SQL: %s %s, %s, %s", cur.statement, device, type, channel)
        pconn.close()
        logging.debug("DB pool close")
    except mariadb.Error as e: 
        logging.error(f"DB: {e}")
    except mariadb.PoolError as e:
        logging.error(f"DB pool: {e}")

# Insert into the table the charging values
def add_charging(device, vin, vout, sv, sc, pw, pr):
    try: 
        cur = pconn.cursor()
        cur.execute("INSERT INTO tb_charging VALUES (NULL, now(3), ?, ?, ?, ?, ?, ?, ?)", (device, vin, vout, sv, sc, pw, pr))
        logging.debug("SQL: %s %s, %s, %s, %s %s, %s, %s", cur.statement, device, vin, vout, sv, sc, pw, pr)
        pconn.close()
        logging.debug("DB pool close")
    except mariadb.Error as e: 
        logging.error(f"DB: {e}")
    except mariadb.PoolError as e:
        logging.error(f"DB pool: {e}")

# Move Motor
def move_motor(channel):
    if channel == P_SWU:
        pin = P_LPW
        pin_name = "P_LPW"
    elif channel == P_SWD:
        pin = P_RPW
        pin_name = "P_RPW"

    beep(P_BU1, B_MOT)

    logging.debug(E_RISING + ' Channel: %s', channel)
    logging.debug("Values pins enable R: %s - L: %s", GPIO.input(P_REN), GPIO.input(P_LEN))
    add_event(pin_name, E_RISING, channel)

    while GPIO.input(channel):
        GPIO.output(pin, True)    
        time.sleep(0.1)
    else:
        GPIO.output(pin, False)
        logging.debug(E_LOW + ' Channel: %s', channel)
        add_event(pin_name, E_LOW, channel)

# Check Battery
def check_battery():
    pin = P_SCH
    pin_name = "P_SCH"
    i2c_bus = board.I2C()
    logging.debug("I2C BUS: %s", board.I2C())

    ina219 = INA219(i2c_bus)
    ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S

    while True:
        bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
        shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
        current = ina219.current/1000  # current in mA
        power = ina219.power  # power in watts

        # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
        logging.debug(
            "VIN+:{:6.3f}V".format(bus_voltage+shunt_voltage) + 
            " | VIN-:{:6.3f}V".format(bus_voltage) + 
            " | SV:{:8.5f}V".format(shunt_voltage) +
            " | SC:{:7.4f}A".format(current) +
            " | PW:{:8.5f}W".format(bus_voltage*current) +
            " | PR:{:6.3f}W".format(power)
            )
        event = "NO VALUE"
        if bus_voltage+shunt_voltage >= 30 and current <= 0.01:
            event = E_CURRENT
        elif bus_voltage+shunt_voltage <= 30 and current <= 0.01:
            event = E_NOCURRENT
        elif bus_voltage+shunt_voltage <= 30 and current > 0.5:
            event = E_CHARGING
        add_event(pin_name, event, pin)
        logging.debug(pin_name + " Charging state: " + event)

        # Add charging record
        add_charging(pin_name, bus_voltage+shunt_voltage, bus_voltage, shunt_voltage, current, bus_voltage*current, power)

        # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
        if ina219.overflow:
            logging.error("I2C Internal Math Overflow")

        time.sleep(5)

# ============== MAIN ==============
if __name__ == "__main__":
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
        logging.debug("Adding GPIO event detection")
        GPIO.add_event_detect(P_SWD, GPIO.RISING, callback = move_motor, bouncetime = 200)
        GPIO.add_event_detect(P_SWU, GPIO.RISING, callback = move_motor, bouncetime = 200)

        logging.debug("Start thead check battery")
        tcb = threading.Thread(target=check_battery, args=())
        tcb.start()

        GPIO.output(P_REN, True)
        GPIO.output(P_LEN, True)

        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current Time:", current_time)
            time.sleep(5)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        logging.info(E_KEY)
        add_event("K3E Lift Chair", E_KEY)
        print("Keyboard interrupt")

    finally:
        cleanup()
