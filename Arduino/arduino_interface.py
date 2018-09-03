#arduino_interface.py
#Python-Arduino Interface
#Assumes Arduino on COM3
#Dillon Wong 04/08/2018

import serial
arduino = serial.Serial('COM3', 9600)

#Sets Arduino digital PIN to HIGH or LOW
#HIGH = 1
#LOW = 0
def arduino_write(pin, high_or_low):
    #arduino = serial.Serial('COM3', 9600)
    #There appears to be a time delay between
    #calling serial.Serial and being able
    #to communicate with Arduino.
    if 2 <= pin <= 13:
        if high_or_low == 1:
            arduino.write(chr(128+pin))
        elif high_or_low == 0:
            arduino.write(chr(pin))
        else:
            print 'ERROR: Unacceptable HIGH or LOW state'
    else:
        print 'ERROR: Unacceptable PIN'
    #arduino.close()

#Determines if Arduino digital PIN is HIGH or LOW
#HIGH = 1
#LOW = 0
#This program does not measure the voltage at the PIN!
#It only reads the register on the ATMEGA328 to determine
#whether PIN is set to output HIGH or LOW.
def arduino_read(pin):
    #arduino = serial.Serial('COM3', 9600)
    if 2 <= pin <= 13:
        arduino.write(chr(64+pin))
        print arduino.read()
    else:
        print 'ERROR: Unacceptable PIN'
    #arduino.close()
