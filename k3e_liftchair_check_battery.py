import time 
import board
import logging
from adafruit_ina219 import ADCResolution, INA219
#  *** IMPORTS LOCALS ***
import k3e_liftchair_settings as set
import k3e_liftchair_func as fun


# Check Battery
def check_battery():
    num = 0                 # Veces que recorre el loop
    wait = 5                # Espera en segundos
    interval = 5            # Tiempo transcurrido en seg para agregar registro con datos de carga 

    event = None
    last_event = None

    pin = set.P_SCH
    pin_name = "P_SCH"

    i2c_bus = board.I2C()
    ina219 = INA219(i2c_bus)
    ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
    logging.debug("I2C BUS: %s", board.I2C())

    while True:
        ++num
        bus_voltage = ina219.bus_voltage            # voltage on V- (load side)
        shunt_voltage = ina219.shunt_voltage        # voltage between V+ and V- across the shunt
        current = ina219.current/1000               # current in mA
        power = ina219.power                        # power in watts

        # Verifica el estado (contacto, cargando, sin contacto)
        if bus_voltage+shunt_voltage >= 30 and current <= 0.01:
            event = set.E_CURRENT
        elif bus_voltage+shunt_voltage <= 30 and current <= 0.01:
            event = set.E_NOCURRENT
        elif bus_voltage+shunt_voltage <= 30 and current > 0.5:
            event = set.E_CHARGING

        # Revisa el estado y agrega evento
        if event != last_event:
            num = 0
            last_event = event
            logging.debug(pin_name + " State change: " + event)
            # Add event record
            fun.add_event(pin_name, event, pin)
            # Add charging record
            fun.add_charging(pin_name, bus_voltage+shunt_voltage, bus_voltage, shunt_voltage, current, bus_voltage*current, power)
        elif event == last_event and event != set.E_CURRENT and interval <= wait*num:
            num = 0
            # Add charging record
            fun.add_charging(pin_name, bus_voltage+shunt_voltage, bus_voltage, shunt_voltage, current, bus_voltage*current, power)

        # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
        # logging.debug(
        #     "VIN+:{:6.3f}V".format(bus_voltage+shunt_voltage) + 
        #     " | VIN-:{:6.3f}V".format(bus_voltage) + 
        #     " | SV:{:8.5f}V".format(shunt_voltage) +
        #     " | SC:{:7.4f}A".format(current) +
        #     " | PW:{:8.5f}W".format(bus_voltage*current) +
        #     " | PR:{:6.3f}W".format(power)
        #     )

        # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
        if ina219.overflow:
            logging.error("I2C Internal Math Overflow")

        # Loop wait
        time.sleep(wait)

        # Check exit thread variable
        if set.exit_thread_check_battery:
            logging.debug("Closing check_battery thread")
            break
