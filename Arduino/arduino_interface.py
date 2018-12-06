#arduino_interface.py
#Python-Arduino Interface
#Assumes Arduino on COM4
#Dillon Wong 04/08/2018

#TODO: Wrapper to switch X-Y capacitance meter
#TODO: Wrapper to activate voltage divider relays

import serial

class arduino:

    def __init__(self, com_port = 'COM4'):
        self.arduino = serial.Serial('COM4', 9600)

    #Sets Arduino digital PIN to HIGH or LOW
    #HIGH = 1
    #LOW = 0
    def write(self, pin, high_or_low):
        #There appears to be a time delay between
        #calling serial.Serial and being able
        #to communicate with Arduino.
        if 2 <= pin <= 13:
            if high_or_low == 1:
                self.arduino.write(chr(128+pin))
            elif high_or_low == 0:
                self.arduino.write(chr(pin))
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
    def read(self, pin):
        if 2 <= pin <= 13:
            self.arduino.write(chr(64+pin))
            print self.arduino.read()
        else:
            print 'ERROR: Unacceptable PIN'
        #arduino.close()
