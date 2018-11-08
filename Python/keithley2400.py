#keithley2400.py
#Controls Keithley 2400 SourceMeter through RS232
#Assumes COM3, 9600 Baud, line feed as termination character
#Uses pyserial
#Dillon Wong 11/03/2018

import serial
import time
keithley = serial.Serial('COM3', 9600, timeout = 1)
keithley_lock = 0
keithley_emergency_lock = 0

def set_voltage(num):
    global keithley_lock
    if keithley_lock == 1:
        print 'Keithley SourceMeter is LOCKED.'
        return
    keithley_lock = 1
    force_set_voltage(num)
    keithley_lock = 0

def force_set_voltage(num):
    if -15 <= num <= 15:
        keithley.write(':SOUR:VOLT:LEV ' + str(num) + '\n')
        keithley.write(':SYST:KEY 23\n')
    else:
        print 'For safety, I cannot allow voltages greater than 15 V.'

def set_voltage_gradual(num, increment):
    global keithley_lock
    if (keithley_lock == 1):
        print 'Keithley SourceMeter is LOCKED.'
        return
    if (num < -15) or (num > 15):
        print 'For safety, I cannot allow voltages greater than 15 V.'
    elif (increment < 0.000095):
        print 'Please choose a larger increment value.'
    else:
        loop_flag = 1
        keithley_lock = 1
        while loop_flag:
            if keithley_emergency_lock == 1:
                return
            voltage = force_read_voltage()
            if abs(num - voltage) < 1.1*increment:
                force_set_voltage(num)
                print 'VOLTAGE: ' + str(force_read_voltage()) + ' V'
                print 'CURRENT: ' + str(force_read_current()) + 'uA'
                print 'DONE'
                keithley.write(':SYST:KEY 23\n')
                loop_flag = 0
                keithley_lock = 0
            elif voltage > num:
                force_set_voltage(voltage - increment)
                print 'VOLTAGE: ' + str(force_read_voltage()) + ' V'
                print 'CURRENT: ' + str(force_read_current()) + 'uA'
                time.sleep(0.01)
            elif voltage < num:
                force_set_voltage(voltage + increment)
                print 'VOLTAGE: ' + str(force_read_voltage()) + ' V'
                print 'CURRENT: ' + str(force_read_current()) + ' V'
                time.sleep(0.01)

def force_read_voltage():
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    voltage = float(meas_array.split(',')[0])
    keithley.write(':SYST:KEY 23\n')
    return voltage

def read_voltage():
    global keithley_lock
    if keithley_lock == 1:
        print 'Keithley SourceMeter is LOCKED.'
        return 'NaN'
    keithley_lock = 1
    voltage = force_read_voltage()
    keithley_lock = 0
    return voltage

def force_read_current():
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    current = float(meas_array.split(',')[1])*1E6
    keithley.write(':SYST:KEY 23\n')
    return current

def read_current():
    global keithley_lock
    if keithley_lock == 1:
        print 'Keithley SourceMeter is LOCKED.'
        return 'NaN'
    keithley_lock = 1
    current = force_read_current()
    keithley_lock = 0
    return current

#Run voltage to 0 V in the event of an emergency.
def run_to_zero():
    global keithley_emergency_lock
    global keithley_lock
    keithley_emergency_lock = 1
    keithley_lock = 1
    time.sleep(1)
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    voltage = float(meas_array.split(',')[0])
    while not (-0.00001 < voltage < 0.00001):
        if -1 < voltage < 1:
            force_set_voltage(0)
        elif voltage >= 1:
            force_set_voltage(voltage - 0.1)
            time.sleep(0.01)
        elif voltage <= -1:
            force_set_voltage(voltage + 0.1)
            time.sleep(0.01)
        keithley.write(':READ?\n')
        meas_array = keithley.readline()
        voltage = float(meas_array.split(',')[0])
    keithley.write('OUTPUT OFF\n')
    #keithley.write(':SYST:KEY 24\n')
    keithley.write(':SYST:KEY 23\n')
    print 'Run to 0 V complete.'
    print 'Keithley SourceMeter output is now off.'

def unlock():
    global keithley_emergency_lock
    global keithley_lock
    keithley_emergency_lock = 0
    keithley_lock = 0
    keithley.write('OUTPUT ON\n')
    keithley.write(':SYST:KEY 23\n')
