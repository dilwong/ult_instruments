#Controls KEPCO BHK 2000-0.1MG high voltage power supply
#For now, it only reads. It does not set voltage/current.

try:
    import visa
except ModuleNotFoundError:
    import pyvisa as visa

class kepco:

    #The primary address is assumed to be 6
    def __init__(self, address = 6, gpib_num = 1):
        self.primary_id = 'GPIB' + str(gpib_num) + '::' +str(address) +'::INSTR'

    #Measures voltage
    def query(self, message):
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            inst = rm.open_resource(self.primary_id)
            answer = inst.query(message)
            inst.control_ren(6)
            inst.close()
        rm.close()
        return answer

    #Measures volgage
    def read_voltage(self):
        return float(self.query('MEAS:SCAL:VOLT?'))

    #Measures current
    def read_current(self):
        return float(self.query('MEAS:SCAL:CURR?'))
