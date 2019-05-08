#keithley2400.py
#Controls Keithley 2400 SourceMeter through RS232
#Assumes COM3, 9600 Baud, line feed as termination character
#Uses pyserial
#Dillon Wong 11/03/2018

import serial
import time

class keithley2400:

    def __init__(self, com_port = 'COM3'):
        self.keithley = serial.Serial(com_port, 9600, timeout = 1)
        self.keithley_lock = 0
        self.keithley_emergency_lock = 0

    #Make decorator?
    def set_voltage(self, num):
        if self.keithley_lock == 1:
            print 'Keithley SourceMeter is LOCKED.'
            return
        self.keithley_lock = 1
        self.force_set_voltage(num)
        self.keithley_lock = 0

    def force_set_voltage(self, num):
        if -15 <= num <= 15:
            self.keithley.write(':SOUR:VOLT:LEV ' + str(num) + '\n')
            self.keithley.write(':SYST:KEY 23\n')
        else:
            print 'For safety, I cannot allow voltages greater than 15 V.'

    def set_voltage_gradual(self, num, increment):
        if (self.keithley_lock == 1):
            print 'Keithley SourceMeter is LOCKED.'
            return
        if (num < -15) or (num > 15):
            print 'For safety, I cannot allow voltages greater than 15 V.'
        elif (increment < 0.000095):
            print 'Please choose a larger increment value.'
        else:
            loop_flag = 1
            self.keithley_lock = 1
            while loop_flag:
                if self.keithley_emergency_lock == 1:
                    return
                voltage = self.force_read_voltage()
                if abs(num - voltage) < 1.1*increment:
                    self.force_set_voltage(num)
                    print 'VOLTAGE: ' + str(self.force_read_voltage()) + ' V'
                    print 'CURRENT: ' + str(self.force_read_current()) + 'uA'
                    print 'DONE'
                    self.keithley.write(':SYST:KEY 23\n')
                    loop_flag = 0
                    self.keithley_lock = 0
                elif voltage > num:
                    self.force_set_voltage(voltage - increment)
                    print 'VOLTAGE: ' + str(self.force_read_voltage()) + ' V'
                    print 'CURRENT: ' + str(self.force_read_current()) + 'uA'
                    time.sleep(0.01)
                elif voltage < num:
                    self.force_set_voltage(voltage + increment)
                    print 'VOLTAGE: ' + str(self.force_read_voltage()) + ' V'
                    print 'CURRENT: ' + str(self.force_read_current()) + ' V'
                    time.sleep(0.01)

    def force_read_voltage(self):
        while True:
            try:
                self.keithley.write('\n')
                self.keithley.write(':READ?\n')
                meas_array = self.keithley.readline()
                voltage = float(meas_array.split(',')[0])
                self.keithley.write(':SYST:KEY 23\n')
                break
            except (ValueError, IndexError):
                print 'HEADER ERROR DETECTED: ' + meas_array
                time.sleep(1)
        return voltage

    def read_voltage(self):
        if self.keithley_lock == 1:
            print 'Keithley SourceMeter is LOCKED.'
            return 'NaN'
        self.keithley_lock = 1
        voltage = self.force_read_voltage()
        self.keithley_lock = 0
        return voltage

    def force_read_current(self):
        while True:
            try:
                self.keithley.write('\n')
                self.keithley.write(':READ?\n')
                meas_array = self.keithley.readline()
                current = float(meas_array.split(',')[1])*1E6
                self.keithley.write(':SYST:KEY 23\n')
                break
            except (ValueError, IndexError):
                print 'HEADER ERROR DETECTED: ' + meas_array
                time.sleep(1)
        return current

    def read_current(self):
        if self.keithley_lock == 1:
            print 'Keithley SourceMeter is LOCKED.'
            return 'NaN'
        self.keithley_lock = 1
        current = self.force_read_current()
        self.keithley_lock = 0
        return current

    #Run voltage to 0 V in the event of an emergency.
    def run_to_zero(self):
        self.keithley_emergency_lock = 1
        self.keithley_lock = 1
        time.sleep(1)
        self.keithley.write(':READ?\n')
        meas_array = self.keithley.readline()
        voltage = float(meas_array.split(',')[0])
        while not (-0.00001 < voltage < 0.00001):
            if -1 < voltage < 1:
                self.force_set_voltage(0)
            elif voltage >= 1:
                self.force_set_voltage(voltage - 0.1)
                time.sleep(0.01)
            elif voltage <= -1:
                self.force_set_voltage(voltage + 0.1)
                time.sleep(0.01)
            self.keithley.write(':READ?\n')
            meas_array = self.keithley.readline()
            voltage = float(meas_array.split(',')[0])
        self.keithley.write('OUTPUT OFF\n')
        #self.keithley.write(':SYST:KEY 24\n')
        self.keithley.write(':SYST:KEY 23\n')
        print 'Run to 0 V complete.'
        print 'Keithley SourceMeter output is now off.'

    def unlock(self):
        self.keithley_emergency_lock = 0
        self.keithley_lock = 0
        self.keithley.write('OUTPUT ON\n')
        self.keithley.write(':SYST:KEY 23\n')
