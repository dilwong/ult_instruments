#This program monitors the 1K pot, sorb, and needle valve
#temperatures.  If the temperatures are too high, the program
#will shut down the Keithley that controls the fixed impedance
#heater.

import thread
import time
import datetime

import ult_instruments.Python.triton_temperature as triton
import ult_instruments.Python.triton_pressure as dilution_pressure

import ult_instruments.Python.keithley2400
try:
    keithley
except NameError:
    keithley = ult_instruments.Python.keithley2400.keithley()

#Ask user for Triton IP address and port.
#Should change to scrub inputs.
try:
    IP_address
except NameError:
    IP_address = raw_input('Enter TRITON IP address:')
try:
    port
except NameError:
    port = int(raw_input('Enter port number:'))

#Set maximum temperatures
onek_limit = float(raw_input('Enter MAXIMUM 1K pot temperature: '))
sorb_limit = float(raw_input('Enter MAXIMUM sorb temperature: '))
needle_limit = float(raw_input('Enter MAXIMUM needle valve temperature: '))

triton_flag = 1
def triton_temperature_loop(IP_address, port):
    off_flag = 1
    while triton_flag:
        print datetime.datetime.now()
        onek_pot_temperature = triton.onek_pot(IP_address, port)
        sorb_temperature = triton.sorb(IP_address, port)
        needle_valve_temperature = triton.needle_valve(IP_address, port)
        print '1K pot: ' + str(onek_pot_temperature) + ' K'
        print 'Sorb: ' + str(sorb_temperature) + ' K'
        print 'Needle valve: ' + str(needle_valve_temperature) + ' K'
        if off_flag != 0:
            print 'VOLTAGE: ' + str(keithley.read_voltage()) + ' V'
            print 'CURRENT: ' + str(keithley.read_current()) + ' uA'
        print 'Run "triton_stop()" to QUIT'
        if off_flag == 1:
            #Needs to also check pressure.
            #Also need physical fail-safe to kill Keithley power if program crashes.
            if (onek_pot_temperature > onek_limit) or (sorb_temperature > sorb_limit) or (needle_valve_temperature > needle_limit):
                print 'WARNING: TEMPERATURES HAVE EXCEEDED LIMIT'
                print 'BEGIN EMERGENCY SHUT DOWN OF IMPEDANCE HEATER'
                print '\a'
                keithley.run_to_zero()
                off_datetime = str(datetime.datetime.now())
                off_flag = 0
        elif off_flag == 0:
            print 'IMPEDANCE HEATER IS OFF SINCE ' + off_datetime
            print '\a'
        print ''
        time.sleep(5)

def triton_stop():
    global triton_flag
    keithley.keithley_emergency_lock = 0
    keithley.keithley_lock = 0
    triton_flag = 0

thread.start_new_thread(triton_temperature_loop,(IP_address, port))
