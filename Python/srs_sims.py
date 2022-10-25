"""
Interface with SRS Small Instrumentation Modules:
SIM900 Mainframe
SIM980 Summing Amplifier
SIM925 Octal 4-Wire Multiplexer

NOT FULLY IMPLEMENTED YET!!!
"""

try:
    import pyvisa as visa
except ModuleNotFoundError:
    import visa

try:
    long
except NameError:
    long = int

import atexit

from numpy import isin

# Interface for the SRS SIM900 Mainframe
class Mainframe:

    # The primary address is assumed to be 2
    def __init__(self, address = 2, gpib_num = 1):
        self.primary_id = 'GPIB' + str(gpib_num) + '::' +str(address) +'::INSTR'
        self._rm = visa.ResourceManager()
        self.instrument = self._rm.open_resource(self.primary_id)
        self.ports = dict()
        
        @atexit.register
        def exit_handler():
            self.close()

    def close(self):
        self.instrument.close()
        self._rm.close()
    
    def write(self, message):
        self.instrument.write(message)

    def read(self, message):
        return self.instrument.query(message)

# Abstract base class for a Small Instrumentation Module
class SIMModule(object):

    def __init__(self, mainframe, port):
        self.mainframe = mainframe
        if isinstance(port, str):
            pass
        elif isinstance(port, (int, long)):
            port = str(port)
        else:
            raise TypeError('port in SIMModule needs to be an integer or a string.')
        self.port = port
        self.mainframe.ports[port] = self

    def write(self, message):
        self.mainframe.write('SEND {}, "{}\n"'.format(self.port, message))

#  Interface for the SRS SIM980 Summing Amplifier
class SummingAmplifier(SIMModule):

    def __init__(self, mainframe, port):
        super(SummingAmplifier, self).__init__(mainframe, port)

    def set_state(self, channel_number, state):
        assert isinstance(state, (int, long, str)), 'Invalid state!'
        if isinstance(state, str):
            # state = state.lower()
            # if state == 'on':
            #     state = 1
            # elif state == 'off':
            #     state = 0
            # elif ('invert' in state) and ('non' not in state):
            #     state = -1
            raise NotImplementedError('strings not yet accepted in set_state.')
        assert state in [-1, 0, 1], 'Invalid state!'
        self.write('CHAN {},{}'.format(channel_number, state))

# Interface for the SIM925 Octal 4-Wire Multiplexer
class Multiplexter(SIMModule):

    def __init__(self, mainframe, port):
        super(Multiplexter, self).__init__(mainframe, port)

    def set_channel(self, channel_number):
        self.write('CHAN {}'.format(channel_number))