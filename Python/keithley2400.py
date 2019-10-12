#keithley2400.py
#Controls Keithley 2400 SourceMeter through RS232
#Python 2.7 compatible
#Unsure if this module works in Python 3

import serial
import time
try:
    import thread
except:
    import _thread

class keithley2400:

    def __init__(self, com_port = 'COM3'):
        self.keithley = serial.Serial(com_port, 9600, timeout = 1)
        self.lock = thread.allocate_lock()
        self.emergency_lock = 0

    def force_set_voltage(self, num):
        if -15 <= num <= 15:
            self.keithley.write(':SOUR:VOLT:LEV ' + str(num) + '\n')
            self.keithley.write(':SYST:KEY 23\n')
        else:
            print('For safety, I cannot allow voltages greater than 15 V.')

    def set_voltage(self, num, increment = 0.1):
        if (num < -15) or (num > 15):
            print('For safety, I cannot allow voltages greater than 15 V.')
            return
        if (increment < 0.000095):
            print('Please choose a larger increment value.')
            return
        self.lock.acquire()
        try:
            loop_flag = 1
            while loop_flag:
                if self.emergency_lock:
                    return
                voltage = self.force_read_voltage()
                if abs(num - voltage) < 1.1*increment:
                    self.force_set_voltage(num)
                    print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                    print('CURRENT: ' + str(self.force_read_current()) + 'uA')
                    print('DONE')
                    self.keithley.write(':SYST:KEY 23\n')
                    loop_flag = 0
                elif voltage > num:
                    self.force_set_voltage(voltage - increment)
                    print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                    print('CURRENT: ' + str(self.force_read_current()) + 'uA')
                    time.sleep(0.01)
                elif voltage < num:
                    self.force_set_voltage(voltage + increment)
                    print('VOLTAGE: ' + str(self.force_read_voltage()) + ' V')
                    print('CURRENT: ' + str(self.force_read_current()) + ' V')
                    time.sleep(0.01)
        except:
            raise
        finally:
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
                time.sleep(1)
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
                time.sleep(1)
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