# Monitors the status of the dilution refrigerator

#TO DO: Message boundaries for recv over TCP

import socket
import time
import traceback
import atexit
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
        self.__port_list__ = []
        self.consecutive_exceptions = 0
        for func in self.function_array:
            func()
            time.sleep(0.02)
        self.stop = 0
        self.__loop_state__ = 0
        self.terminate = 0
        self.lock = thread.allocate_lock()
        self.thread_counter = 1
        
        @atexit.register
        def exit_handler():
            self.terminate = 1
            self.lock.acquire()
            listen_port_list = self.__port_list__
            self.lock.release()
            for pt in listen_port_list:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect(('127.0.0.1', pt))
                    s.sendall('QUIT\n'.encode())
                    _ = s.recv(4096)
                except Exception:
                    pass
                finally:
                    s.close()
            while True:
                self.lock.acquire()
                nThreads = self.thread_counter
                self.lock.release()
                if nThreads == 1:
                    break
                else:
                    time.sleep(0.25)
            while True:
                if self.__loop_state__ == 0:
                    break
                else:
                    time.sleep(0.25)
        
        thread.start_new_thread(self.loop,())
        
    def loop(self):
        self.__loop_state__ = 1
        while not self.stop:
            try:
                for func in self.function_array:
                    func()
                    if self.terminate == 1:
                        break
                    time.sleep(0.25)
                self.consecutive_exceptions = 0
                if self.terminate == 1:
                    break
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
        self.__loop_state__ = 0

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
        while True:
            try:
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
            except Exception:
                print('Error detected in triton_monitor.__read_triton__')
                err = traceback.format_exc()
                print(err)
                time.sleep(5)
            finally:
                s.close()

    def log(self, filename, wait_time):
        thread.start_new_thread(self.__log__,(filename, wait_time))

    def __log__(self, filename, wait_time):

        import json
        import datetime

        self.lock.acquire()
        self.thread_counter += 1
        self.lock.release()

        try:
            while(self.terminate == 0):

                time.sleep(wait_time)

                datetime_string = str(datetime.datetime.now())

                json_log_object = {'time': datetime_string, \
                                'pot_temp': self.onek_pot_temp, \
                                'sorb_temp': self.sorb_temp, \
                                'needle_valve_temp': self.needle_valve_temp, \
                                'still_temp': self.still_temp, \
                                'mix_chamber_temp': self.mix_chamber_temp, \
                                'stm_rx_temp': self.stm_rx_temp, \
                                'stm_cx_temp': self.stm_cx_temp, \
                                'tank_pressure': self.tank_pressure, \
                                'condense_pressure': self.condense_pressure, \
                                'still_pressure': self.still_pressure, \
                                'turbo_back_pressure': self.turbo_back_pressure, \
                                'n2_trap_pressure': self.n2_trap_pressure}

                with open(filename,'a+') as logpathfile:
                    json.dump(json_log_object, logpathfile)
                    logpathfile.write(',\n')
        except Exception:
            print('Error detected in triton_monitor.__log__')
            err = traceback.format_exc()
            print(err)
            print('Stopping log...')
        finally:
            self.lock.acquire()
            self.thread_counter -= 1
            self.lock.release()

    def listen(self, port):
        thread.start_new_thread(self.__listen__,(port, ))
    
    def __listen__(self, port):
        
        self.lock.acquire()
        if port in self.__port_list__:
            print('ERROR: PORT ALREADY BEING USED')
            self.lock.release()
            return
        else:
            self.__port_list__.append(port)
            self.thread_counter += 1
            self.lock.release()
        
        host = '127.0.0.1'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(0)
        
        try:
            while self.terminate == 0:
                conn, _ = s.accept()
                query = conn.recv(1024).decode()
                if query == 'pot_temp\n':
                    reply = self.onek_pot_temp
                elif query == 'sorb_temp\n':
                    reply = self.sorb_temp
                elif query == 'needle_valve_temp\n':
                    reply = self.needle_valve_temp
                elif query == 'still_temp\n':
                    reply = self.still_temp
                elif query == 'mix_chamber_temp\n':
                    reply = self.mix_chamber_temp
                elif query == 'stm_rx_temp\n':
                    reply = self.stm_rx_temp
                elif query == 'stm_cx_temp\n':
                    reply = self.stm_cx_temp
                elif query == 'tank_pressure\n':
                    reply = self.tank_pressure
                elif query == 'condense_pressure\n':
                    reply = self.condense_pressure
                elif query == 'still_pressure\n':
                    reply = self.still_pressure
                elif query == 'turbo_back_pressure\n':
                    reply = self.turbo_back_pressure
                elif query == 'n2_trap_pressure\n':
                    reply = self.n2_trap_pressure
                elif query == 'QUIT\n':
                    reply = 'QUITTING'
                else:
                    reply = 'INVALID_REQUEST'
                reply = str(reply) + '\n'
                conn.sendall(reply.encode())
        except Exception:
            print('Error detected in triton_monitor.__listen__')
            err = traceback.format_exc()
            print(err)
            print('Stopping listen...')
        finally:
            s.close()
            self.lock.acquire()
            if port in self.__port_list__:
                self.__port_list__.remove(port)
                self.thread_counter -= 1
            self.lock.release()