import os
import logging

# CONS MOTOR
M_INISPEED = 10


# CONS BEEP TYPES
B_MOT = 1
B_EDG = 2


# CONS EVENTS
E_SIG = 'KILL'
E_KEY = 'CTRL+C'
E_END = 'END'
E_INI = 'INIT'

E_LOW = 'LOW'
E_HIGH = 'HIGH'
E_RISING = 'RISING'
E_FALLING = 'FALLING'

E_CURRENT = 'CURRENT'
E_CHARGING = 'CHARGING'
E_NOCURRENT = 'NO CURRENT'


# CONS GPIO DEVICES
P_IRS = 4
P_RPW = 12
P_SFO = 13
P_SED = 17
P_BU1 = 18
P_SWD = 19
P_SCH = 21
P_SEU = 22
P_LEN = 23
P_LPW = 24
P_REN = 25
P_SWU = 26
P_SEC = 27


# VARS
global pool
global pconn
global exit_thread_check_battery


# Logging - level=logging.DEBUG or logging.INFO or logging.WARNING or logging.ERROR or logging.CRITICAL
def log(level_log):
    logging.basicConfig(filename=os.path.splitext(os.path.basename(__file__))[0]+".log", level=level_log, format='%(asctime)s - %(levelname)s (%(filename)s::%(funcName)s::%(threadName)s[%(lineno)d]): %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    logging.info("")
    logging.info("************************* " + E_INI + " *************************")
