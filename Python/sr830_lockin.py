#Wrapper for GPIB control of SR830 Lock-In amplifier
#
#Available functions:
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

import visa

class lockin:

    #The primary address is assumed to be 8
    address = 8
    primary_id = 'GPIB0::'+str(address)+'::INSTR'

    #Sets amplitude
    @classmethod
    def set_amplitude(self,ampl):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            if 0 <= ampl <= 0.005:
                inst.write('SLVL 0.004')
            elif 0.005 < ampl <= 5:
                inst.write('SLVL ' + str(ampl))
            else:
                print 'ERROR: Amplitude out of bounds.'
            inst.close()
        rm.close()

    #Gets amplitude
    @classmethod
    def get_amplitude(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            print float(inst.query('SLVL ?'))
            inst.close()
        rm.close()

    #Sets frequency
    @classmethod
    def set_frequency(self,freq):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            if 0.001 < freq <= 102000:
                inst.write('FREQ ' + str(freq))
            else:
                print 'ERROR: Frequency out of bounds.'
            inst.close()
        rm.close()

    #Gets frequency
    @classmethod
    def get_frequency(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            print float(inst.query('FREQ ?'))
            inst.close()
        rm.close()

    #Sets harmonic
    @classmethod
    def set_harmonic(self,harm):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            if isinstance(harm,int):
                if 1 <= harm <= 19999:
                    inst.write('HARM ' + str(harm))
                else:
                    print 'ERROR: Harmonic out of bounds.'
            else:
                print 'ERROR: Harmonic not an integer.'
            inst.close()
        rm.close()

    #Gets harmonic
    @classmethod
    def get_harmonic(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            print int(inst.query('HARM ?'))
            inst.close()
        rm.close()

    #Set phase
    @classmethod
    def set_phase(self,phase):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            if -360 <= phase <= 729.99:
                inst.write('PHAS ' + str(phase))
            else:
                print 'ERROR: Phase out of bounds.'

            inst.close()
        rm.close()

    #Gets phase
    @classmethod
    def get_phase(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            print float(inst.query('PHAS ?'))
            inst.close()
        rm.close()

    #Autophase
    @classmethod
    def autophase(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            inst.write('APHS')
            inst.close()
        rm.close()

    #Add to phase
    @classmethod
    def add_to_phase(self,add):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            if isinstance(add, (int, long, float)):
                inst = rm.open_resource(self.primary_id)
                new_phase = (float(inst.query('PHAS ?')) + add) % 360
                inst.write('PHAS ' + str(new_phase))
                inst.close()
        rm.close()

    #Autogain
    @classmethod
    def autogain(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            inst.write('AGAN')
            inst.close()
        rm.close()

    #Set time constant
    @classmethod
    def set_timeconstant(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
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
            if isinstance(time_set,int) and (0 <= time_set <= 19):
                inst = rm.open_resource(self.primary_id)
                inst.write('OFLT ' + str(time_set))
                inst.close()
        rm.close

    #Get time constant
    @classmethod
    def get_timeconstant(self):
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
            print time_constant_map[int(inst.query('OFLT ?'))]
            inst.close()
        rm.close

    #Set sensitivity
    @classmethod
    def set_sensitivity(self):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            print 'SELECT SENSITIVITY'
            print '0  : 2nV        13 : 50uV'
            print '1  : 5nV        14 : 100uV'
            print '2  : 10nV       15 : 200uV'
            print '3  : 20nV       16 : 500uV'
            print '4  : 50nV       17 : 1mV'
            print '5  : 100mV      18 : 2mV'
            print '6  : 200nV      19 : 5mV'
            print '7  : 500nV      20 : 10mV'
            print '8  : 1uV        21 : 20mV'
            print '9  : 2uV        22 : 50mV'
            print '10 : 5uV        23 : 100mV'
            print '11 : 10uV       24 : 200mV'
            print '12 : 20uV       25 : 500mV'
            print '                26 : 1V'
            sens_set = input()
            if isinstance(sens_set,int) and (0 <= sens_set <= 26):
                inst = rm.open_resource(self.primary_id)
                inst.write('SENS ' + str(sens_set))
                inst.close()
        rm.close

    #Get time constant
    @classmethod
    def get_sensitivity(self):
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
            print sens_map[int(inst.query('SENS ?'))]
            inst.close()
        rm.close
