# Monitors the status of the dilution refrigerator

#TO DO: Message boundaries for recv over TCP

import socket
import time
import traceback
try:
    import thread
except ModuleNotFoundError:
    import _thread as thread

# This class is not a Singleton, so multiple instances check temperature and pressure independently.
class triton_monitor:
    
    def __init__(self, IP_address, port):

        self.IP_address = IP_address
        self.port = port
        self.function_array = [ \
            self._onek_pot_temp, \
            self._sorb_temp, \
            self._needle_valve_temp, \
            self._still_temp, \
            self._cold_plate_temp, \
            self._mix_chamber_temp, \
            self._stm_rx_temp, \
            self._stm_cx_temp, \
            self._tank_press, \
            self._condense_press, \
            self._still_press, \
            self._turbo_back_press, \
            self._n2_trap_press]
        self.exception_list = []
        self.consecutive_exceptions = 0
        for func in self.function_array:
            func()
            time.sleep(0.02)
        self.stop = 0
        thread.start_new_thread(self.loop,())
        
    def loop(self):
        while not self.stop:
            try:
                for func in self.function_array:
                    func()
                    time.sleep(0.25)
                self.consecutive_exceptions = 0
            except:
                err_detect = traceback.format_exc()
                self.exception_list.append(err_detect)
                self.consecutive_exceptions += 1
                if self.consecutive_exceptions > 25:
                    self.stop = 1
                    self.onek_pot_temp = 99999
                    self.sorb_temp = 99999
                    self.needle_valve_temp = 99999
                    self.still_temp = 99999
                    self.cold_plate_temp = 99999
                    self.mix_chamber_temp = 99999
                    self.stm_rx_temp = 99999
                    self.stm_cx_temp = 99999
                    self.tank_pressure = 99999
                    self.condense_pressure = 99999
                    self.still_pressure = 99999
                    self.turbo_back_pressure = 99999
                    self.n2_trap_pressure = 99999
                time.sleep(1)

    def _onek_pot_temp(self):
        message = 'READ:DEV:T2:TEMP:SIG:TEMP\n'
        self.onek_pot_temp = self.read_triton(message)

    def _sorb_temp(self):
        message = 'READ:DEV:T1:TEMP:SIG:TEMP\n'
        self.sorb_temp = self.read_triton(message)

    def _needle_valve_temp(self):
        message = 'READ:DEV:T8:TEMP:SIG:TEMP\n'
        self.needle_valve_temp = self.read_triton(message)

    def _still_temp(self):
        message = 'READ:DEV:T3:TEMP:SIG:TEMP\n'
        self.still_temp = self.read_triton(message)

    def _cold_plate_temp(self):
        message = 'READ:DEV:T4:TEMP:SIG:TEMP\n'
        self.cold_plate_temp = self.read_triton(message)

    def _mix_chamber_temp(self):
        message = 'READ:DEV:T5:TEMP:SIG:TEMP\n'
        self.mix_chamber_temp = self.read_triton(message)

    def _stm_rx_temp(self):
        message = 'READ:DEV:T6:TEMP:SIG:TEMP\n'
        self.stm_rx_temp = self.read_triton(message)

    def _stm_cx_temp(self):
        message = 'READ:DEV:T7:TEMP:SIG:TEMP\n'
        self.stm_cx_temp = self.read_triton(message)

    def _tank_press(self):
        message = 'READ:DEV:P1:PRES:SIG:PRES\n'
        self.tank_pressure = self.read_triton(message)

    def _condense_press(self):
        message = 'READ:DEV:P2:PRES:SIG:PRES\n'
        self.condense_pressure = self.read_triton(message)

    def _still_press(self):
        message = 'READ:DEV:P3:PRES:SIG:PRES\n'
        self.still_pressure = self.read_triton(message)

    def _turbo_back_press(self):
        message = 'READ:DEV:P4:PRES:SIG:PRES\n'
        self.turbo_back_pressure = self.read_triton(message)

    def _n2_trap_press(self):
        message = 'READ:DEV:P5:PRES:SIG:PRES\n'
        self.n2_trap_pressure = self.read_triton(message)

    def read_triton(self, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IP_address, self.port))
        s.send(message.encode())
        response = str(s.recv(4096).decode())
        s.close()
        if message[-5:-1] == 'TEMP':
            response_slice = -2
        elif message[-5:-1] == 'PRES':
            response_slice = -3
        else:
            return 0
        return float(response.split(':')[6][:response_slice])