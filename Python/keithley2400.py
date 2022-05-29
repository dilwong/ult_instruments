# keithley2400.py
# Controls Keithley 2400 SourceMeter through RS232
# Python 2.7 compatible
# Unsure if this module works in Python 3
#
# TO DO: Message boundaries for recv over TCP.

from inspect import trace
import serial
import time
try:
    import thread
except:
    import _thread as thread
try:
    import Queue
except:
    import queue as Queue
import atexit
import socket
import traceback

class keithley2400:

    def __init__(self, com_port = 'COM3', max_voltage = 100, listen_port = None, increment = None):
        self.keithley = serial.Serial(com_port, 9600, timeout = 1)
        self.lock = thread.allocate_lock()
        self.emergency_lock = 0
        self.MAXVOLTAGE = abs(max_voltage)
        self.listen_port = listen_port
        self.error_list = []
        self._halt = False
        
        self._default_increment = 0.1 if increment is None else increment
        self._default_increment_time = 0.01
        self.increment = increment
        self.increment_time = self._default_increment_time
        
        self._header_error_time = 1
        self._exception_time = 0.5
        self._print = True
        
        if self.listen_port is not None:
            self._listen_flag = True
            self.queue = Queue.Queue()
            thread.start_new_thread(self._listen,())
            thread.start_new_thread(self._execute,())

        @atexit.register
        def exit_handler():
            self.keithley.close()
            if self.listen_port is not None:
                try:
                    self._listen_flag = False
                    self.lis_sock.close()
                except:
                    pass

    def _listen(self):
        try:
            host = '127.0.0.1'
            port = self.listen_port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lis_sock = s
            s.bind((host, port))
            s.listen(0)
        except Exception:
            err = traceback.format_exc()
            print('ERROR in LISTEN thread:')
            print(err)
            self.error_list.append(err)
        while self._listen_flag:
            try:
                self._conn, self._addr = s.accept()
                listen_string = self._conn.recv(1024).decode()
                if 'QUIT' in listen_string:
                    self._conn.sendall('OK\n'.encode())
                    s.close()
                    self._listen_flag = False
                    break
                elif 'HALT' in listen_string:
                    self._conn.sendall('OK\n'.encode())
                    time.sleep(0.05)
                    self._halt = True
                else:
                    self.queue.put(listen_string)
            except Exception:
                err = traceback.format_exc()
                print('ERROR in LISTEN thread:')
                print(err)
                self.error_list.append(err)
                while len(self.error_list) > 20:
                    self.error_list.pop(0)
                time.sleep(self._exception_time)
    
    def _execute(self):
        while self._listen_flag:
            try:
                listen_string = self.queue.get()
                listen_commands = listen_string.split()
                listen_args = '(' + ','.join(listen_commands[1:]) + ')'
                if listen_commands[0] in dir(self)[3:]:
                    try:
                        result = None
                        exec('result = self.' + listen_commands[0] + listen_args)
                        if result is not None:
                            send_string = str(result) + '\n'
                            self._conn.sendall(send_string.encode())
                        else:
                            self._conn.sendall('NO DATA\n'.encode())
                    except TypeError:
                        self._conn.sendall('ERROR: TYPE ERROR\n'.encode())
                else:
                    self._conn.sendall('ERROR: COMMAND ERROR\n'.encode())
            except Exception:
                err = traceback.format_exc()
                print('ERROR in EXECUTE thread:')
                print(err)
                self.error_list.append(err)
                while len(self.error_list) > 20:
                    self.error_list.pop(0)
                time.sleep(self._exception_time)

    def set_increment(self, increment):
        if increment == 0:
            self.increment = self._default_increment
        else:
            self.increment = increment

    def set_increment_time(self, increment_time):
        if increment_time == 0:
            self.increment_time = self._default_increment_time
        else:
            self.increment_time = increment_time

    def _stop_listen(self):
        self._listen_flag = False
        host = '127.0.0.1'
        port = self.listen_port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall('QUIT'.encode())
        s.close()
    
    def force_set_voltage(self, num):
        if -self.MAXVOLTAGE <= num <= self.MAXVOLTAGE:
            self.keithley.write(':SOUR:VOLT:LEV ' + str(num) + '\n')
            self.keithley.write(':SYST:KEY 23\n')
        else:
            print('For safety, I cannot allow voltages greater than ' + str(self.MAXVOLTAGE) + ' V.')

    def set_voltage(self, num, increment = None):
        self._halt = False
        if increment is None:
            increment = self.increment
            if increment is None:
                increment = 0.1
        if (num < -self.MAXVOLTAGE) or (num > self.MAXVOLTAGE):
            print('For safety, I cannot allow voltages greater than ' + str(self.MAXVOLTAGE) + ' V.')
            return
        if (increment < 0.000095):
            print('Please choose a larger increment value.')
            return
        self.lock.acquire()
        try:
            while not self._halt:
                if self.emergency_lock:
                    return
                voltage = self.force_read_voltage()
                if abs(num - voltage) < 1.1*increment:
                    self.force_set_voltage(num)
                    if self._print:
                        print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                        print('CURRENT: ' + str(self.force_read_current()) + ' uA')
                        print('DONE')
                    break
                elif voltage > num:
                    self.force_set_voltage(voltage - increment)
                    if self._print:
                        print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                        print('CURRENT: ' + str(self.force_read_current()) + ' uA')
                    time.sleep(self.increment_time)
                elif voltage < num:
                    self.force_set_voltage(voltage + increment)
                    if self._print:
                        print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                        print('CURRENT: ' + str(self.force_read_current()) + ' uA')
                    time.sleep(self.increment_time)
        except:
            raise
        finally:
            try:
                self.keithley.write(':SYST:KEY 23\n')
            except:
                pass
            finally:
                self._halt = False
                self.lock.release()

    def force_read_voltage(self):
        counter = 0
        while True:
            try:
                self.keithley.write('\n')
                self.keithley.write(':READ?\n')
                meas_array = self.keithley.readline()
                voltage = float(meas_array.split(',')[0])
                self.keithley.write(':SYST:KEY 23\n')
                break
            except (ValueError, IndexError):
                print('HEADER ERROR DETECTED: ' + meas_array)
                if counter > 100:
                    self.force_set_voltage(0)
                    print('EMERGENCY SET VOLTAGE TO 0 V')
                    break
                counter += 1
                time.sleep(self._header_error_time)
        return voltage

    def read_voltage(self):
        self.lock.acquire()
        try:
            return self.force_read_voltage()
        except:
            raise
        finally:
            self.lock.release()

    def force_read_current(self):
        counter = 0
        while True:
            try:
                self.keithley.write('\n')
                self.keithley.write(':READ?\n')
                meas_array = self.keithley.readline()
                current = float(meas_array.split(',')[1])*1E6
                self.keithley.write(':SYST:KEY 23\n')
                break
            except (ValueError, IndexError):
                print('HEADER ERROR DETECTED: ' + meas_array)
                if counter > 100:
                    self.force_set_voltage(0)
                    print('EMERGENCY SET VOLTAGE TO 0 V')
                    break
                counter += 1
                time.sleep(self._header_error_time)
        return current

    def read_current(self):
        self.lock.acquire()
        try:
            return self.force_read_current()
        except:
            raise
        finally:
            self.lock.release()

    #Run voltage to 0 V in the event of an emergency.
    def run_to_zero(self):
        self.emergency_lock = 1
        self.lock.acquire()
        try:
            time.sleep(0.1)
            voltage = self.force_read_voltage()
            while not (-0.00001 < voltage < 0.00001):
                if -1 < voltage < 1:
                    self.force_set_voltage(0)
                elif voltage >= 1:
                    self.force_set_voltage(voltage - 0.1)
                    time.sleep(0.01)
                elif voltage <= -1:
                    self.force_set_voltage(voltage + 0.1)
                    time.sleep(0.01)
                voltage = self.force_read_voltage()
            self.keithley.write(':SYST:KEY 23\n')
            print('Run to 0 V complete.')
            print('Keithley SourceMeter output is now 0 V.')
        except:
            raise
        finally:
            self.lock.release()
            self.emergency_lock = 0

    def output_on(self):
        self.lock.acquire()
        try:
            self.keithley.write('OUTPUT ON\n')
            self.keithley.write(':SYST:KEY 23\n')
        except:
            raise
        finally:
            self.lock.release()

    def output_off(self):
        self.lock.acquire()
        try:
            self.keithley.write('OUTPUT OFF\n')
            self.keithley.write(':SYST:KEY 23\n')
        except:
            raise
        finally:
            self.lock.release()