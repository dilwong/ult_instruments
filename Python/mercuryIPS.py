# Controls Mercury IPS magnet power supply

import serial
import time
try:
    import thread
except:
    import _thread
import atexit

class mercuryIPS:

    def __init__(self, com_port = 'COM6'):
        self.__power_supply__ = serial.Serial(com_port, 9600, timeout = 1)
        self.x = vectorDirection(self, 'X')
        self.y = vectorDirection(self, 'Y')
        self.z = vectorDirection(self, 'Z')

    @atexit.register
    def exit_handler():
        self.close()

    def query(self, command):
        self.__power_supply__.write(command)
        return self.__power_supply__.readline()

    def set(self, direction, command_abbrev):
        if direction.upper() not in ['X', 'Y', 'Z']: # direction is a string
            raise magnetException('Direction is not X, Y, or Z')
        reply = self.query('SET:DEV:GRP' + direction.upper() + ':PSU:' + command_abbrev + '\r\n')
        result = reply.strip().split(':')[-1]
        if result == 'INVALID':
            print('ERROR: INVALID QUERY')
        return result

    def read(self, direction, command_abbrev):
        if direction.upper() not in ['X', 'Y', 'Z']: # direction is a string
            raise magnetException('Direction is not X, Y, or Z')
        reply = self.query('READ:DEV:GRP' + direction.upper() + ':PSU:' + command_abbrev + '\r\n')
        result = reply.strip().split(':')[-1]
        if result == 'INVALID':
            print('ERROR: INVALID QUERY')
        return result

    def str_to_num(self, input, base_unit):
        un_len = len(base_unit)
        unit = input[-un_len:]
        if unit == base_unit:
            # Assuming the power supply returns SI unit without prefix
            # TO DO: Use regular expression to extract proper unit conversion
            return float(input[:-un_len])
        else:
            raise magnetException('Incorrect unit')

    def close(self):
        self.__power_supply__.close()

    def read_state(self, direction):
        return self.read(direction, 'ACTN?')

    def hold(self, direction):
        return self.set(direction, 'ACTN:HOLD')

    def ramp_to_set(self, direction):
        print('ERROR: NOT IMPLEMENTED YET')
        # return = self.set(direction, 'ACTN:RTOS')
        return 'NULL'

    def ramp_to_zero(self, direction):
        print('ERROR: NOT IMPLEMENTED YET')
        # return = self.set(direction, 'ACTN:RTOZ')
        return 'NULL'

    def read_switch_heater(self, direction):
        return self.read(direction, 'SIG:SWHT?')

    def switch_heater_on(self, direction):
        return self.set(direction, 'SIG:SWHT:ON')

    def switch_heater_off(self, direction):
        return self.set(direction, 'SIG:SWHT:OFF')

    def read_voltage(self, direction):
        result = self.read(direction, 'SIG:VOLT?')
        return self.str_to_num(result, 'V')

    def read_current(self, direction):
        result = self.read(direction, 'SIG:CURR?')
        return self.str_to_num(result, 'A')

    def read_field(self, direction):
        result = self.read(direction, 'SIG:FLD?')
        return self.str_to_num(result, 'T')

    def read_persistent_field(self, direction):
        result = self.read(direction, 'SIG:PFLD?')
        return self.str_to_num(result, 'T')

    def read_target_field(self, direction): # Set Point (T)
        result = self.read(direction, 'SIG:FSET?')
        return self.str_to_num(result, 'T')

    def set_target_field(self, direction, value): # Set Point (T)
        return self.set(direction, 'SIG:FSET:' + str(value) + 'T') # If no unit, assumne 'T'

    def read_ramp_rate(self, direction): # Set Rate (T/min)
        result = self.read(direction, 'SIG:RFST?')
        return self.str_to_num(result, 'T/m')

    def set_ramp_rate(self, direction, value): # Set Rate (T/min)
        return self.set(direction, 'SIG:RFST:' + str(value) + 'T/m') # If no unit, assumne 'T/m'

class vectorDirection:

    def __init__(self, IPS_instance, direction):
        self.__IPS_instance__ = IPS_instance
        self.__direction__ = direction

    def read_state(self):
        return self.__IPS_instance__.read_state(self.__direction__)

    def hold(self):
        return self.__IPS_instance__.hold(self.__direction__)

    def ramp_to_set(self):
        return self.__IPS_instance__.ramp_to_set(self.__direction__)

    def ramp_to_zero(self):
        return self.__IPS_instance__.ramp_to_zero(self.__direction__)

    def read_switch_heater(self):
        return self.__IPS_instance__.read_switch_heater(self.__direction__)

    def switch_heater_on(self):
        return self.__IPS_instance__.switch_heater_on(self.__direction__)

    def switch_heater_off(self):
        return self.__IPS_instance__.switch_heater_off(self.__direction__)

    def read_voltage(self):
        return self.__IPS_instance__.read_voltage(self.__direction__)

    def read_current(self):
        return self.__IPS_instance__.read_current(self.__direction__)

    def read_field(self):
        return self.__IPS_instance__.read_field(self.__direction__)

    def read_persistent_field(self):
        return self.__IPS_instance__.read_persistent_field(self.__direction__)

    def read_target_field(self):
        return self.__IPS_instance__.read_target_field(self.__direction__)

    def set_target_field(self, value):
        if (self.__direction__ == 'X') or (self.__direction__ == 'X'):
            if abs(value) > 1:
                raise magnetException('Exceeds field limit')
        if self.__direction__ == 'Z':
            if abs(value) > 9:
                raise magnetException('Exceeds field limit for Z for 9-1-1 T magnet')
        return self.__IPS_instance__.set_target_field(self.__direction__, value)

    def read_ramp_rate(self):
        return self.__IPS_instance__.read_ramp_rate(self.__direction__)

    def set_ramp_rate(self, value):
        if value < 0:
            raise magnetException('Do not set a negative ramp rate')
        if value > 0.5:
            raise magnetException('Ramp rate too high')
        else:
            if value > 0.1:
                print('WARNING: RAMP RATE SET > 0.1 T/min')
        return self.__IPS_instance__.set_ramp_rate(self.__direction__, value)

class magnetException(Exception):

    def __init__(self, message):
        super(magnetException, self).__init__(message)
