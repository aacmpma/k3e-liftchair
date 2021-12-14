#!/usr/bin/python3

import os
import time
import signal
import logging
import threading
import RPi.GPIO as GPIO
from datetime import datetime
#  *** IMPORTS LOCALS ***
import k3e_liftchair_settings as set
import k3e_liftchair_func as fun
import k3e_liftchair_check_battery as tcb

# ============== MAIN ==============
if __name__ == "__main__":
    try:
        os.system("clear")
        file = os.path.dirname(__file__)+"/"+os.path.splitext(os.path.basename(__file__))[0]+".log"

        print("============================================================")
        print("                       K3E Lift Chair                       ")
        print("============================================================")
        print("Log:", file)
        print("============================================================")

        # Enable logging
        set.log(file, logging.DEBUG)

        # Create database connection
        fun.create_connection_pool()
        set.pconn = set.pool.get_connection()

        # Catch Kill Signal
        signal.signal(signal.SIGTERM, fun.signal_term_handler)

        # Init event 
        fun.add_event("K3E Lift Chair", set.E_INI)

        # Setup GPIO
        fun.setupGPIO()

        # Add event detection
        logging.debug("Adding GPIO event detection")
        GPIO.add_event_detect(set.P_SWU, GPIO.RISING, callback = fun.move_motor_up, bouncetime = 100)
        GPIO.add_event_detect(set.P_SWD, GPIO.RISING, callback = fun.move_motor_down, bouncetime = 100)
        GPIO.add_event_detect(set.P_SEC, GPIO.RISING, callback = fun.edge_switch_center, bouncetime = 100)

        # Start Thread check_battery
        logging.debug("Start thread check battery")
        set.exit_thread_check_battery = False
        thread_cb = threading.Thread(target=tcb.check_battery, args=())
        thread_cb.start()

        while True:
            if set.exit_thread_check_battery:
                break
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            #print("Current Time:", current_time)
            time.sleep(5)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        fun.ctrl_c(thread_cb)

    finally:
        fun.cleanup()
