#This program monitors the 1K pot, sorb, and needle valve
#temperatures.  If the temperatures are too high, the program
#will shut down the Keithley that controls the fixed impedance
#heater.

#Python 2 only
#TO DO: Python 3 compatibility

import thread
import time
import datetime
import traceback
import socket
#from colorama import Fore
import json
import winsound
import Queue
import atexit

# Not a Singleton
class impedance_heater:

    running = False
    listening = False
    executing = False
    stalled = False

    def __init__(self, triton_monitor, heater_keithley, log_directory):
        self.triton_monitor = triton_monitor
        self.heater_keithley = heater_keithley
        self.log_directory = log_directory
        self.queue = Queue.Queue()
        self.lock = thread.allocate_lock()
        self.exception_list = []
        self.stall_procedure = None
        self.stall_arguments = []
        thread.start_new_thread(self.listen, ())
        thread.start_new_thread(self.execute, ())

    def start(self):
        if self.__class__.running:
            print("ERROR: ALREADY RUNNING")
            return
        self.__class__.running = True
        self.__class__.stalled = False
        self.stop = 0
        self.consecutive_except_num = 0
        self.temp_color_text = ''
        self.onek_limit = float(raw_input('Enter MAXIMUM 1K pot temperature (K): '))
        self.sorb_limit = float(raw_input('Enter MAXIMUM sorb temperature (K): '))
        self.needle_limit = float(raw_input('Enter MAXIMUM needle valve temperature (K): '))
        self.still_limit = float(raw_input('Enter MAXIMUM still pressure (mbar):'))
        self.onek_alarm = 1.8 # T
        self.sorb_alarm = 1.8 # T
        self.condense_alarm = 180 # mbar
        self.stored_heater_voltage = None
        thread.start_new_thread(self.loop, ())

    def loop(self):
        while not self.stop:
            try:
                time.sleep(1)
                self.lock.acquire()
                try:
                    datetime_string = str(datetime.datetime.now())
                    print(self.temp_color_text + datetime_string)
                    onek_pot_temperature = self.triton_monitor.onek_pot_temp
                    time.sleep(1)
                    sorb_temperature = self.triton_monitor.sorb_temp
                    time.sleep(1)
                    needle_valve_temperature = self.triton_monitor.needle_valve_temp
                    time.sleep(1)
                    still_pressure = self.triton_monitor.still_pressure
                    time.sleep(0.05)
                    condense_pressure = self.triton_monitor.condense_pressure
                    print('1K pot: ' + str(onek_pot_temperature) + ' K')
                    print('Sorb: ' + str(sorb_temperature) + ' K')
                    print('Needle valve: ' + str(needle_valve_temperature) + ' K')
                    print('Still: ' + str(still_pressure) + ' mbar')
                    json_log_object = {'time':datetime_string, \
                        'pot_temp':onek_pot_temperature, \
                        'sorb_temp':sorb_temperature, \
                        'needle_valve_temp':needle_valve_temperature, \
                        'still_pressure':still_pressure}
                    json_log_object['heater_not_stalled'] = 1
                    if not self.__class__.stalled:
                        heater_voltage = self.heater_keithley.read_voltage()
                        heater_current = self.heater_keithley.read_current()
                        print('VOLTAGE: ' + str(heater_voltage) + ' V')
                        print('CURRENT: ' + str(heater_current) + ' uA')
                        json_log_object['heater_voltage'] = heater_voltage
                        json_log_object['heater_current'] = heater_current
                        json_log_object['heater_not_stalled'] = 0
                    print('Run "triton_stop()" to QUIT')
                    logpath = self.log_directory + 'triton_' + datetime_string.split(' ')[0].replace('-','')
                    with open(logpath,'a+') as logpathfile:
                        json.dump(json_log_object,logpathfile)
                        logpathfile.write(',\n')
                    if not self.__class__.stalled:
                        if (sorb_temperature > self.sorb_alarm) or \
                                (onek_pot_temperature > self.onek_alarm) or \
                                (condense_pressure > self.condense_alarm): # ALARM
                            self.annoying_sound()
                        if (onek_pot_temperature > self.onek_limit) or \
                                (sorb_temperature > self.sorb_limit) or \
                                (needle_valve_temperature > self.needle_limit) \
                                or (still_pressure > self.still_limit):
                            self.__class__.stalled = True
                            self.annoying_sound()
                            self.stored_heater_voltage = heater_voltage
                            print('WARNING: A TEMPERATURE OR PRESSURE HAS EXCEEDED LIMIT')
                            print('BEGIN EMERGENCY SHUT DOWN OF IMPEDANCE HEATER')
                            off_datetime = str(datetime.datetime.now())
                            self.heater_keithley.run_to_zero()
                            if self.stall_procedure is not None:
                                stall_arguments_tuple = (self, ) + tuple(self.stall_arguments)
                                thread.start_new_thread(self.stall_procedure, stall_arguments_tuple)
                    else:
                        print('IMPEDANCE HEATER IS OFF SINCE ' + off_datetime)
                        self.annoying_sound()
                    print ''
                    time.sleep(1)
                    self.consecutive_except_num = 0
                except:
                    raise
                finally:
                    self.lock.release()
            except:
                self.consecutive_except_num += 1
                if len(self.exception_list) > 10000:
                    self.exception_list = []
                err_detect = traceback.format_exc()
                print('Consecutive exceptions: ' + str(self.consecutive_except_num))
                print(err_detect)
                self.exception_list.append(err_detect)
                if self.consecutive_except_num > 25:
                    self.heater_keithley.run_to_zero()
                    while not self.stop:
                        print('POSSIBLE COMMUNICATIONS FAILURE: TURNED IMPEDANCE HEATER OFF')
                        print('Run "triton_stop()" to QUIT')
                        time.sleep(5)

    def stop_loop(self):
        self.__class__.running = False
        self.stop = 1

    def unstall(self):
        self.__class__.stalled = False

    def listen(self):

        if self.__class__.listening:
            print('ERROR: ALREADY LISTENING')
            return
        self.__class__.listening = True
        self.conn = None
        self.addr = None

        try:
            listen_host = '127.0.0.1'
            listen_port = 65430
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((listen_host, listen_port))

            @atexit.register
            def listen_exit_handler():
                s.close()

            s.listen(0)

            while True:
                self.conn, self.addr = s.accept()
                listen_string = self.conn.recv(1024)
                if listen_string == 'QUIT':
                    self.conn.sendall('Quitting...\n')
                    s.close()
                    self.__class__.listening = False
                    return
                else:
                    self.queue.put(listen_string)
        except Exception:
            print(traceback.format_exc())
            self.__class__.listening = False

    def execute(self):
        if self.__class__.executing:
            print('ERROR: ALREADY EXECUTING')
            return
        self.__class__.executing = True
        while True:
            listen_string = self.queue.get()
            self.lock.acquire()
            try:
                print('RUNNING COMMAND: ' + listen_string)
                arg_command, arg_numeric = listen_string.split()
                arg_numeric = float(arg_numeric)
                if arg_command == 'Set_Heater_Voltage':
                    # self.lock.acquire() should probably be here instead of above to
                    # not lock for temperature reads
                    self.heater_keithley.output_on()
                    self.heater_keithley.set_voltage(arg_numeric, 0.1)
                    self.conn.sendall('Done\n')
                elif arg_command == 'Read_Heater_Voltage': # What causes Error ID code -113 and -110
                    self.heater_keithley.output_on()
                    volt = str(self.heater_keithley.read_voltage())
                    self.conn.sendall(volt + '\n')
                elif arg_command == 'Read_Heater_Current':
                    self.heater_keithley.output_on()
                    curr = str(self.heater_keithley.read_current())
                    self.conn.sendall(curr + '\n')
                elif arg_command == 'Read_1K_Pot_Temperature':
                    temp = str(self.triton_monitor.onek_pot_temp)
                    self.conn.sendall(temp + '\n')
                elif arg_command == 'Read_IVC_Sorb_Temperature':
                    temp = str(self.triton_monitor.sorb_temp)
                    self.conn.sendall(temp + '\n')
                elif arg_command == 'Read_Needle_Valve_Temperature':
                    temp = str(self.triton_monitor.needle_valve_temp)
                    self.conn.sendall(temp + '\n')
                elif arg_command == 'Read_Still_Pressure':
                    press = str(self.triton_monitor.still_pressure)
                    self.conn.sendall(press + '\n')
                elif arg_command == 'Read_Mixing_Chamber_Temperature':
                    press = str(self.triton_monitor.mix_chamber_temp)
                    self.conn.sendall(press + '\n')
                elif arg_command == 'Read_STM_RX_Temperature':
                    press = str(self.triton_monitor.stm_rx_temp)
                    self.conn.sendall(press + '\n')
                elif arg_command == 'Read_STM_CX_Temperature':
                    press = str(self.triton_monitor.stm_cx_temp)
                    self.conn.sendall(press + '\n')
                elif arg_command == 'Unstall_Triton_Loop':
                    self.heater_keithley.output_on()
                    self.unstall()
                    self.conn.sendall('Done\n')
                elif arg_command == 'Triton_Stop':
                    self.conn.sendall('Done\n')
                    self.stop_loop()
                elif arg_command == 'Triton_Stall_Status':
                    if not self.__class__.stalled:
                        self.conn.sendall('NOT_STALLED\n')
                    else:
                        self.conn.sendall('STALLED\n')
                else:
                    self.conn.sendall('Invalid Command\n')
                print('COMMAND COMPLETE')
            except:
                print(traceback.format_exc())
                raise
            finally:
                self.lock.release()

    def annoying_sound(self):
        soundC=523
        soundD=587
        soundE=659
        soundF=698
        soundG=784
        winsound.Beep(soundD,200)
        winsound.Beep(soundC,100)
        time.sleep(0.1)
        winsound.Beep(soundD,200)
        winsound.Beep(soundC,50)
        winsound.Beep(soundD,200)
        winsound.Beep(soundC,50)
        winsound.Beep(soundF,300)

# Example of a stall procedure
# Needs to be tested extensively!!!
def restart_heater(impedance_heater):
    # STAGE 1
    print("'RESTART HEATER' STAGE 1")
    first_stage_wait_minutes = 10
    time.sleep(first_stage_wait_minutes * 60)
    if impedance_heater.__class__.running == False:
        print("TRITON MONITOR NOT RUNNING.  RUNNING TO ZERO AND TERMINATING 'RESTART HEATER'")
        impedance_heater.heater_keithley.run_to_zero()
        return
    if impedance_heater.__class__.stalled == False:
        print("TRITON MONITOR NOT STALLED.  TERMINATING 'RESTART HEATER'")
        return
    impedance_heater.heater_keithley.set_voltage(4)
    # STAGE 2
    print("'RESTART HEATER' STAGE 2")
    second_stage_wait_minutes = 2
    second_stage_seconds_accumulator = 0
    while float(second_stage_seconds_accumulator)/60.0 <= second_stage_wait_minutes:
        second_stage_seconds_accumulator += 5
        onek_pot_temperature = impedance_heater.triton_monitor.onek_pot_temp
        sorb_temperature = impedance_heater.triton_monitor.sorb_temp
        needle_valve_temperature = impedance_heater.triton_monitor.needle_valve_temp
        still_pressure = impedance_heater.triton_monitor.still_pressure
        if (onek_pot_temperature > impedance_heater.onek_limit) or \
                (sorb_temperature > impedance_heater.sorb_limit) or \
                (needle_valve_temperature > impedance_heater.needle_limit) or \
                (still_pressure > impedance_heater.still_limit):
            print('POT DRY.  RUNNING HEATER TO ZERO')
            impedance_heater.heater_keithley.run_to_zero()
            return
        if impedance_heater.__class__.stalled == False:
            print("TRITON MONITOR NOT STALLED.  TERMINATING 'RESTART HEATER'")
            return
        time.sleep(5)
    if impedance_heater.__class__.running == False:
        print("TRITON MONITOR NOT RUNNING.  RUNNING TO ZERO AND TERMINATING 'RESTART HEATER'")
        impedance_heater.heater_keithley.run_to_zero()
        return
    impedance_heater.heater_keithley.set_voltage(5.5)
    # STAGE 3
    print("'RESTART HEATER' STAGE 3")
    third_stage_wait_minutes = 2
    third_stage_seconds_accumulator = 0
    while float(third_stage_seconds_accumulator)/60.0 <= third_stage_wait_minutes:
        third_stage_seconds_accumulator += 5
        onek_pot_temperature = impedance_heater.triton_monitor.onek_pot_temp
        sorb_temperature = impedance_heater.triton_monitor.sorb_temp
        needle_valve_temperature = impedance_heater.triton_monitor.needle_valve_temp
        still_pressure = impedance_heater.triton_monitor.still_pressure
        if (onek_pot_temperature > impedance_heater.onek_limit) or \
                (sorb_temperature > impedance_heater.sorb_limit) or \
                (needle_valve_temperature > impedance_heater.needle_limit) or \
                (still_pressure > impedance_heater.still_limit):
            print('POT DRY.  RUNNING HEATER TO ZERO')
            impedance_heater.heater_keithley.run_to_zero()
            return
        if impedance_heater.__class__.stalled == False:
            print("TRITON MONITOR NOT STALLED.  TERMINATING 'RESTART HEATER'")
            return
        time.sleep(5)
    if impedance_heater.__class__.running == False:
        print("TRITON MONITOR NOT RUNNING.  RUNNING TO ZERO AND TERMINATING 'RESTART HEATER'")
        impedance_heater.heater_keithley.run_to_zero()
        return
    impedance_heater.heater_keithley.set_voltage(6.5)
    print("UNSTALLING TRITON LOOP")
    impedance_heater.__class__.stalled = False
