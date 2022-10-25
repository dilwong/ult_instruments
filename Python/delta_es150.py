#Controls a Delta Elektronika Programmable Power Supply
#ES150 Series (e.g. ES030-5)
#Uses PSC-232 module

import serial
import time

class delta_es150:

    def __init__(self, com_port ='COM6', channel = 1):
        self.instr = serial.Serial(com_port, 9600, timeout = 1)
        self.write('CH 1\n')
        self.absolute_voltage_limit = self.read('SO:VO:MAX?\n')
        self.absolute_current_limit = self.read('SO:CU:MAX?\n')
        self.voltage_limit = self.absolute_voltage_limit
        self.current_limit = self.absolute_current_limit

    def write(self, message):
        self.instr.write(message.encode())
    
    def read(self, message):
        self.write(message)
        temp_string = ''
        reply_string = ''
        while temp_string != '\x04':
            temp_string = self.instr.read().decode()
            if (temp_string != '\n') and (temp_string != '\r') and (temp_string != '\x04'):
                reply_string += temp_string
        #TODO: Detect reply_string begins with 'ER'
        return float(reply_string)

    def set_voltage_limit(self, num):
        if abs(num) <= self.absolute_voltage_limit:
            self.voltage_limit = abs(num)
        else:
            print('ERROR: VOLTAGE LIMIT TOO HIGH')

    def set_current_limit(self, num):
        if abs(num) <= self. absolute_current_limit:
            self.current_limit = abs(num)
        else:
            print('ERROR: CURRENT LIMIT TOO HIGH')

    def measure_voltage(self):
        value = self.read('ME:VO?\n')
        time.sleep(0.01)
        return value

    def measure_current(self):
        value = self.read('ME:CU?\n')
        time.sleep(0.01)
        return value

    def read_voltage_setpoint(self):
        return self.read('SO:VO?\n')

    def read_current_setpoint(self):
        return self.read('SO:CU?\n')

    #TODO: Sanitize inputs
    def set_voltage(self, num):
        if abs(num) <= self.voltage_limit:
            self.write('SOUR:VOLT ' + str(abs(num)) + '\n')
        else:
            print('ERROR: VOLTAGE SETPOINT ABOVE LIMIT')
            print('       VOLTAGE VALUE UNCHANGED')

    def set_current(self, num):
        if abs(num) <= self.current_limit:
            self.write('SOUR:CURR ' + str(abs(num)) + '\n')
        else:
            print('ERROR: CURRENT SETPOINT ABOVE LIMIT')
            print('       CURRENT VALUE UNCHANGED')
