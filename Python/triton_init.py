#This program monitors the 1K pot, sorb, and needle valve
#temperatures.  If the temperatures are too high, the program
#will shut down the Keithley that controls the fixed impedance
#heater.

#TO DO: Get rid of global variables.

import thread
import time
import datetime
import traceback
import socket

import ult_instruments.Python.triton_temperature as dilution_temperature
import ult_instruments.Python.triton_pressure as dilution_pressure

import ult_instruments.Python.keithley2400
try:
    heater_keithley
except NameError:
    heater_keithley = ult_instruments.Python.keithley2400.keithley2400()

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
onek_limit = float(raw_input('Enter MAXIMUM 1K pot temperature (K): '))
sorb_limit = float(raw_input('Enter MAXIMUM sorb temperature (K): '))
needle_limit = float(raw_input('Enter MAXIMUM needle valve temperature (K): '))
still_limit = float(raw_input('Enter MAXIMUM still pressure (mbar):'))

exception_list = []

triton_command_ready = 0
conn = None
listen_string = '_ 0'
def triton_listen(IP_address, port):
    try:
        global triton_command_ready
        global conn
        global listen_string
        listen_host = '127.0.0.1'
        listen_port = 65430
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((listen_host, listen_port))
        s.listen(0)
        while triton_flag:
            conn, addr = s.accept()
            listen_string = conn.recv(1024)
            if listen_string == 'QUIT':
                conn.sendall('Quitting...\n')
                s.close()
            else:
                triton_command_ready = 1
                while triton_command_ready:
                    time.sleep(1)
    except Exception:
        print traceback.format_exc()

triton_flag = 1
def triton_temperature_loop(IP_address, port):
    global exception_list
    global triton_command_ready
    global conn
    global listen_string
    thread.start_new_thread(triton_listen,(IP_address, port))
    try:
        off_flag = 1
        except_num = 0
        while triton_flag:
            if triton_command_ready:
                print 'RUNNING COMMAND: ' + listen_string
                arg_command, arg_numeric = listen_string.split()
                arg_numeric = float(arg_numeric)
                if arg_command == 'Set_Heater_Voltage':
                    heater_keithley.unlock()
                    heater_keithley.set_voltage_gradual(arg_numeric, 0.1)
                    conn.sendall('Done\n')
                elif arg_command == 'Read_Heater_Voltage':
                    heater_keithley.unlock()
                    volt = str(heater_keithley.read_voltage())
                    conn.sendall(volt + '\n')
                elif arg_command == 'Read_Heater_Current':
                    heater_keithley.unlock()
                    curr = str(heater_keithley.read_current())
                    conn.sendall(curr + '\n')
                elif arg_command == 'Read_1K_Pot_Temperature':
                    temp = str(dilution_temperature.onek_pot(IP_address, port))
                    conn.sendall(temp + '\n')
                elif arg_command == 'Read_IVC_Sorb_Temperature':
                    temp = str(dilution_temperature.sorb(IP_address, port))
                    conn.sendall(temp + '\n')
                elif arg_command == 'Read_Needle_Valve_Temperature':
                    temp = str(dilution_temperature.needle_valve(IP_address, port))
                    conn.sendall(temp + '\n')
                elif arg_command == 'Read_Still_Pressure':
                    press = str(dilution_pressure.still(IP_address, port))
                    conn.sendall(press + '\n')
                elif arg_command == 'Restart_Triton_Loop':
                    heater_keithley.unlock()
                    off_flag = 1
                    conn.sendall('Done\n')
                elif arg_command == 'Triton_Stop':
                    conn.sendall('Done\n')
                    triton_stop()
                elif arg_command == 'Triton_Status':
                    if off_flag == 1:
                        conn.sendall('RUNNING\n')
                    elif off_flag == 0:
                        conn.sendall('STOPPED\n')
                else:
                    conn.sendall('Invalid Command\n')
                listen_string = '_ 0'
                conn = None
                triton_command_ready = 0
                print 'COMMAND COMPLETE'
            try:
                time.sleep(1)
                print datetime.datetime.now()
                onek_pot_temperature = dilution_temperature.onek_pot(IP_address, port)
                time.sleep(1)
                sorb_temperature = dilution_temperature.sorb(IP_address, port)
                time.sleep(1)
                needle_valve_temperature = dilution_temperature.needle_valve(IP_address, port)
                time.sleep(1)
                still_pressure = dilution_pressure.still(IP_address, port)
                print '1K pot: ' + str(onek_pot_temperature) + ' K'
                print 'Sorb: ' + str(sorb_temperature) + ' K'
                print 'Needle valve: ' + str(needle_valve_temperature) + ' K'
                print 'Still: ' + str(still_pressure) + ' mbar'
                if off_flag != 0:
                    print 'VOLTAGE: ' + str(heater_keithley.read_voltage()) + ' V'
                    print 'CURRENT: ' + str(heater_keithley.read_current()) + ' uA'
                print 'Run "triton_stop()" to QUIT'
                if off_flag == 1:
                    #Also need physical fail-safe to kill Keithley power if program crashes.
                    if (sorb_temperature > 1.8): #SORB ALARM
                        print '\a'
                    if (onek_pot_temperature > onek_limit) or (sorb_temperature > sorb_limit) or (needle_valve_temperature > needle_limit) or (still_pressure > still_limit):
                        print 'WARNING: A TEMPERATURE OR PRESSURE HAS EXCEEDED LIMIT'
                        print 'BEGIN EMERGENCY SHUT DOWN OF IMPEDANCE HEATER'
                        print '\a'
                        heater_keithley.run_to_zero()
                        off_datetime = str(datetime.datetime.now())
                        off_flag = 0
                elif off_flag == 0:
                    print 'IMPEDANCE HEATER IS OFF SINCE ' + off_datetime
                    print '\a'
                print ''
                time.sleep(1)
                except_num = 0
            except Exception:
                except_num += 1
                if len(exception_list) > 10000:
                    exception_list = []
                err_detect = traceback.format_exc()
                print 'Consecutive exceptions: ' + str(except_num)
                print err_detect
                exception_list.append(err_detect)
                if except_num > 25:
                    heater_keithley.run_to_zero()
                    while triton_flag:
                        print 'POSSIBLE COMMUNICATIONS FAILURE: TURNED IMPEDANCE HEATER OFF'
                        print 'Run "triton_stop()" to QUIT'
                        time.sleep(5)
    except:
        print traceback.format_exc()

def triton_stop():
    global triton_flag
    heater_keithley.keithley_emergency_lock = 0
    heater_keithley.keithley_lock = 0
    triton_flag = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 65430))
    s.sendall('QUIT')
    s.close()
    print 'TRITON LOOP NOW STOPPED'

thread.start_new_thread(triton_temperature_loop,(IP_address, port))
