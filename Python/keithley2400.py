#keithley2400.py
#Controls Keithley 2400 SourceMeter through RS232
#Assumes COM3, 9600 Baud, line feed as termination character
#Uses pyserial
#Dillon Wong 11/03/2018

import serial
#import time
keithley = serial.Serial('COM3', 9600, timeout = 1)

def set_voltage(num):
    if -15 <= num <= 15:
        keithley.write(':SOUR:VOLT:LEV ' + str(num) + '\n')
    else:
        print 'For safety, I cannot allow voltages greater than 15 V.'

def set_voltage_gradual(num):
    if -15 <= num <= 15:
        loop_flag = 1
        while loop_flag:
            keithley.write(':READ?\n')
            meas_array = keithley.readline()
            voltage = float(meas_array.split(',')[0])
            if abs(num - voltage) < 1:
                set_voltage(num)
                read_voltage()
                read_current()
                print 'DONE'
                loop_flag = 0
            elif voltage > num:
                set_voltage(voltage - 0.1)
                read_voltage()
                read_current()
                #time.sleep(0.01)
            elif voltage < num:
                set_voltage(voltage + 0.1)
                read_voltage()
                read_current()
                #time.sleep(0.01)
    else:
        print 'For safety, I cannot allow voltages greater than 15 V.'

def read_voltage():
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    voltage = float(meas_array.split(',')[0])
    print 'VOLTAGE: ' + str(voltage) + ' V'

def read_current():
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    current = float(meas_array.split(',')[1])*1E6
    print 'CURRENT: ' + str(current) + ' uA'

def run_to_zero():
    keithley.write(':READ?\n')
    meas_array = keithley.readline()
    voltage = float(meas_array.split(',')[0])
    while not (-0.00001 < voltage < 0.00001):
        if -1 < voltage < 1:
            set_voltage(0)
        elif voltage >= 1:
            set_voltage(voltage - 0.1)
            #time.sleep(0.01)
        elif voltage <= -1:
            set_voltage(voltage + 0.1)
            #time.sleep(0.01)
        keithley.write(':READ?\n')
        meas_array = keithley.readline()
        voltage = float(meas_array.split(',')[0])
    print 'Run to 0 V complete.'
