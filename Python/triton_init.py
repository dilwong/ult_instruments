#This program monitors the 1K pot, sorb, and needle valve
#temperatures.  If the temperatures are too high, the program
#will shut down the Keithley that controls the fixed impedance
#heater.

import ult_instruments.Python.keithley2400 as keithley
import ult_instruments.Python.triton_temperature as triton
import thread
import time
import datetime

#Ask user for Triton IP address and port.
#Should change to scrub inputs.
IP_address = raw_input('Enter TRITON IP address:')
port = raw_input('Enter port number:')
port = int(port)

t_limit = 4
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
        keithley.read_voltage()
        keithley.read_current()
        print 'Set triton_flag to 0 to QUIT'
        if off_flag == 1:
            if (onek_pot_temperature > t_limit) or (sorb_temperature > t_limit) or (needle_valve_temperature > t_limit):
                print 'WARNING: TEMPERATURES HAVE EXCEEDED LIMIT'
                print 'BEGIN EMERGENCY SHUT DOWN OF IMPEDANCE HEATER'
                keithley.run_to_zero()
                off_flag = 0
        elif off_flag == 0:
            print 'IMPEDANCE HEATER IS OFF'
        print ''
        time.sleep(5)

thread.start_new_thread(triton_temperature_loop,(IP_address, port))
