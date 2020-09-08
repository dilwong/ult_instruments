#Wrapper for GPIB control of SR830 Lock-In amplifier
#
#Available methods:
#set_amplitude(FLOAT), get_amplitude()
#set_frequency(FLOAT), get_frequency()
#set_harmonic(INT), get_harmonic()
#set_phase(FLOAT), get_phase()
#autophase()
#add_to_phase(FLOAT)
#autogain()
#set_timeconstant()
#get_timeconstant()
#set_sensitivity()
#get_sensitivity()

#NOT IMPLEMENTED YET:
# self.read/write("DDEF(?) i,{j,k}") where i=1 for channel 1 & i=2 for channel 2
#                                   where j=0 for X/Y & j=1 for R/THETA
#                                   and k=0
# If a bad read command is sent, lock-in may send junk back in following
# n queries. Need to implement a way to clear read buffer before each
# read command.

import visa
import time
import traceback
import socket
import thread

class lockin:

    #The primary address is assumed to be 8
    def __init__(self, address = 8, gpib_num = 0, start_listening = True):
        self.primary_id = 'GPIB' + str(gpib_num) + '::' +str(address) +'::INSTR'
        if start_listening:
            self.start_listen()

    def write(self, message):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            inst.write(message)
            inst.close()
        rm.close()

    def read(self, message):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            answer = inst.query(message)
            inst.close()
        rm.close()
        return answer

    #Sets amplitude
    def set_amplitude(self, ampl):
        if 0 <= ampl <= 0.005:
            self.write('SLVL 0.004')
        elif 0.005 < ampl <= 5:
            self.write('SLVL ' + str(ampl))
        else:
            print 'ERROR: Amplitude out of bounds.'

    #Gets amplitude
    def get_amplitude(self):
        return float(self.read('SLVL ?'))

    #Sets frequency
    def set_frequency(self, freq):
        if 0.001 < freq <= 102000:
            self.write('FREQ ' + str(freq))
        else:
            print 'ERROR: Frequency out of bounds.'

    #Gets frequency
    def get_frequency(self):
        return float(self.read('FREQ ?'))

    #Sets harmonic
    def set_harmonic(self, harm):
        try:
            harm = int(harm) # Should not overwrite input
        except ValueError:
            'ERROR: Harmonic not an integer.'
            return
        if isinstance(harm,int):
            if 1 <= harm <= 19999:
                self.write('HARM ' + str(harm))
            else:
                print 'ERROR: Harmonic out of bounds.'
        else:
            print 'ERROR: Harmonic not an integer.' # Redundant

    #Gets harmonic
    def get_harmonic(self):
        return int(self.read('HARM ?'))

    #Set phase
    def set_phase(self, phase):
        if -360 <= phase <= 729.99:
            self.write('PHAS ' + str(phase))
        else:
            print 'ERROR: Phase out of bounds.'

    #Gets phase
    def get_phase(self):
        return float(self.read('PHAS ?'))

    #Autophase
    def autophase(self):
        self.write('APHS')

    #Add to phase
    def add_to_phase(self, add):
        if isinstance(add, (int, long, float)):
            new_phase = (self.get_phase() + add) % 360
            self.set_phase(new_phase)

    #Autogain
    def autogain(self):
        self.write('AGAN')

    #Set time constant
    def set_timeconstant(self, value = None):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            if value is None:
                print 'SELECT TIME CONSTANT'
                print '0 : 10us       10 : 1s'
                print '1 : 30us       11 : 3s'
                print '2 : 100us      12 : 10s'
                print '3 : 300us      13 : 30s'
                print '4 : 1ms        14 : 100s'
                print '5 : 3ms        15 : 300s'
                print '6 : 10ms       16 : 1ks'
                print '7 : 30ms       17 : 3ks'
                print '8 : 100ms      18 : 10ks'
                print '9 : 300ms      19 : 30ks'
                time_set = input()
            else:
                try:
                    time_set = int(value)
                except ValueError:
                    print "ERROR: Not an integer"
            if isinstance(time_set,int) and (0 <= time_set <= 19):
                inst = rm.open_resource(self.primary_id)
                inst.write('OFLT ' + str(time_set))
                inst.close()
            else:
                print "Invalid Input: Must be integer between 0 and 19"
        rm.close

    #Get time constant
    def get_timeconstant(self):
        val = None
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            time_constant_map={
                0 : '10us',
                1 : '30us',
                2 : '100us',
                3 : '300us',
                4 : '1ms',
                5 : '3ms',
                6 : '10ms',
                7 : '30ms',
                8 : '100ms',
                9 : '300ms',
                10 : '1s',
                11 : '3s',
                12 : '10s',
                13 : '30s',
                14 : '100s',
                15 : '300s',
                16 : '1ks',
                17 : '3ks',
                18 : '10ks',
                19 : '30ks' }
            inst = rm.open_resource(self.primary_id)
            val = time_constant_map[int(inst.query('OFLT ?'))]
            print val
            inst.close()
        rm.close
        return val

    #Set sensitivity
    def set_sensitivity(self, value = None):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            if value is None:
                print 'SELECT SENSITIVITY'
                print '0  : 2nV        13 : 50uV'
                print '1  : 5nV        14 : 100uV'
                print '2  : 10nV       15 : 200uV'
                print '3  : 20nV       16 : 500uV'
                print '4  : 50nV       17 : 1mV'
                print '5  : 100nV      18 : 2mV'
                print '6  : 200nV      19 : 5mV'
                print '7  : 500nV      20 : 10mV'
                print '8  : 1uV        21 : 20mV'
                print '9  : 2uV        22 : 50mV'
                print '10 : 5uV        23 : 100mV'
                print '11 : 10uV       24 : 200mV'
                print '12 : 20uV       25 : 500mV'
                print '                26 : 1V'
                sens_set = input()
            else:
                try:
                    sens_set = int(value)
                except ValueError:
                    print "ERROR: Not an integer"
            if isinstance(sens_set,int) and (0 <= sens_set <= 26):
                inst = rm.open_resource(self.primary_id)
                inst.write('SENS ' + str(sens_set))
                inst.close()
            else:
                print "Invalid Input: Must be integer between 0 and 26"
        rm.close

    #Get time constant
    def get_sensitivity(self):
        val = None
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            sens_map={
                0 : '2nV',
                1 : '5nV',
                2 : '10nV',
                3 : '20nV',
                4 : '50nV',
                5 : '100nV',
                6 : '200nV',
                7 : '500nV',
                8 : '1uV',
                9 : '2uV',
                10 : '5uV',
                11 : '10uV',
                12 : '20uV',
                13 : '50uV',
                14 : '100uV',
                15 : '200uV',
                16 : '500uV',
                17 : '1mV',
                18 : '2mV',
                19 : '5mV',
                20 : '10mV',
                21 : '20mV',
                22 : '50mV',
                23 : '100mV',
                24 : '200mV',
                25 : '500mV',
                26 : '1V' }
            inst = rm.open_resource(self.primary_id)
            val = sens_map[int(inst.query('SENS ?'))]
            print val
            inst.close()
        rm.close
        return val

    def set_input_A(self):
        self.write('ISRC 0')

    def set_input_AminusB(self):
        self.write('ISRC 1')

    def get_input_setting(self): # A or A-B?
        answer = self.read('ISRC ?')
        if answer == '0\n':
            return 'A'
        elif answer == '1\n':
            return 'A-B'
        else:
            return 'unknown state'

    # TO DO: Eliminate code duplication
    def loop(self):
        host = '127.0.0.1'
        port = 65426
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lis_sock = s
        s.bind((host, port))
        s.listen(0)
        while self.__listen_flag__:
            conn, addr = s.accept()
            listen_string = conn.recv(1024) # Possible rare bug: Needs to loop until \n is received
            if listen_string == 'QUIT\n':
                s.close()
                self.__listen_flag__ = False
            else:
                try:
                    listen_commands = listen_string.split()
                    listen_args = '(' + ','.join(listen_commands[1:]) + ')'
                    if listen_commands[0] in dir(self)[3:]:
                        try:
                            exec('result = self.' + listen_commands[0] + listen_args)
                            if result:
                                conn.sendall(str(result) + '\n')
                            else:
                                conn.sendall('NO DATA\n')
                        except TypeError:
                            conn.sendall('ERROR: TYPE ERROR\n')
                    else:
                        conn.sendall('ERROR: COMMAND ERROR\n')
                except Exception:
                    if len(self.error_list) < 21:
                        err = traceback.format_exc()
                        print 'ERROR in START thread:'
                        print err
                        self.error_list.append(err)
                    time.sleep(0.5)

    def start_listen(self):
        self.error_list = []
        self.__listen_flag__ = True
        thread.start_new_thread(self.loop,())

    def stop_listen(self):
        host = '127.0.0.1'
        port = 65426
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall('QUIT\n')
        s.close()
