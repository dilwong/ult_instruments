# HP 3562A DYNAMIC SIGNAL ANALYZER
# GPIB VISA control

try:
    import visa
except ModuleNotFoundError:
    import pyvisa as visa
    
import time
import numpy as np

class SpectrumAnalyzer:

    def __init__(self, address = 7, gpib_num = 0):
        self.primary_id = 'GPIB' + str(gpib_num) + '::' +str(address) +'::INSTR'
        rm = visa.ResourceManager()
        if self.primary_id in rm.list_resources():
            self.inst = rm.open_resource(self.primary_id)

    def write(self, message):
        self.inst.write(message)

    def read(self, message):
        return self.inst.query(message)
    
    def close(self):
        self.inst.close()

    def setup(self, frequencySpan = 400, nAverages = 1): # Same setup procedure as Yazdani vibration.m
        self.write("AU1;") # AUTORANGE
        self.write("MGDB;")
        self.write("LINX;")
        self.write("FLT1;") # FLOAT INPUT instead of GROUND INPUT
        self.write("C1AC 1;")
        self.write("LNRS;")
        self.write("PSPC;")
        self.write("PSP1;")
        self.write("FRS 0," + str(frequencySpan) + "HZ;")
        self.write("PSUN;")
        self.write("VLTS;")
        self.write("VHZ;")
        self.write("PSUN;")
        self.write("VTRM;")
        self.write("FLAT;")
        self.write("AU1U;") # AUTORANGE
        self.write("NAVG " + str(nAverages) + ";")
        self.write("STBL;")
        self.write("XASC;")
        self.write("YASC;")

    def get_ascii(self, queryTime = 0.1):
        self.write("STRT;")
        measDone = ""
        while True:
            measDone = self.read("SMSD;")
            if measDone == "1\r\n":
                break
            time.sleep(queryTime)
        return self.read("DDAS;")

    def ascii_to_num(self, asciiValues):
        asciiList = asciiValues[2:].split()
        numericList = [float(elem) for elem in asciiList]
        return np.array(numericList[67:])

    def get_binary(self, queryTime = 0.1):
        self.write("STRT;")
        measDone = ""
        while True:
            measDone = self.read("SMSD;")
            if measDone == "1\r\n":
                break
            time.sleep(queryTime)
        self.write("DDBN;")
        return self.inst.read_raw()

    def binary_to_num(self, binaryValues):
        binData = binaryValues[168+4:]
        nElems = int(len(binData)/4)
        data = np.zeros(nElems)
        for idx in range(nElems):
            mantissa = (binData[4*idx] << 16) + (binData[4*idx+1] << 8) + (binData[4*idx+2])
            mantissa *= (2**-23)
            if (binData[4*idx] & 128) == 0:
                pass
            elif (binData[4*idx] & 128) == 128:
                mantissa = -1 + mantissa # Is this correct?
            else:
                raise Exception("Unknown error calculating mantissa in binary_to_num")
            exponent = binData[4*idx + 3]
            if (exponent & 128) == 128:
                exponent -= 256
            elif (exponent & 128) == 0:
                pass
            else:
                raise Exception("Unknown error calculating exponent in binary_to_num")
            data[idx] = mantissa * (2**exponent)
        return data