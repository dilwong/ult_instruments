#keithley2450.py
#Controls Keithley 2450 SourceMeter through USB interface
#Uses Keithley's Test Script Processor, an Lua interpreter
#Sets to source voltage and measure current

#Python 2.7 only
#TO DO: Python 3 compatibility

import visa
import time
import thread
import socket
import traceback
import atexit

class keithley2450:

    def __init__(self, resource = None):
        if resource:
            pass
        else: #If resource is not defined, pick the first Keithley 2450
            rm = visa.ResourceManager()
            resource_list = [resource_string for resource_string in rm.list_resources() if 'USB0::0x05E6::0x2450::' in resource_string]
            try:
                resource =  resource_list[0]
            except IndexError:
                print 'ERROR: Keithley 2450 not found.'
                raise
        self.resource = resource
        self.inst = rm.open_resource(resource)
        self.inst.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
        self.inst.write('smu.measure.func = smu.FUNC_DC_CURRENT')
        self.on_flag = 1
        thread.start_new_thread(self.start,())
        thread.start_new_thread(self.listen,())

        @atexit.register
        def exit_handler():
            self.inst.write('logout')
            self.inst.close()
            try:
                self.lis_sock.close()
            except:
                pass

    def listen(self):
        host = '127.0.0.1'
        port = 65432
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lis_sock = s
        s.bind((host, port))
        s.listen(0)
        while self.on_flag:
            conn, addr = s.accept()
            listen_string = conn.recv(1024)
            if listen_string == 'QUIT':
                s.close()
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

    def start(self):
        self.error_list = []
        self.read_flag = 1
        while self.on_flag:
            try:
                if self.read_flag:
                    self.inst.write('smu.measure.read()')
            except Exception:
                if len(self.error_list) < 21:
                    err = traceback.format_exc()
                    print 'ERROR in START thread:'
                    print err
                    self.error_list.append(err)
            time.sleep(0.5)

    def stop(self):
        self.on_flag = 0
        host = '127.0.0.1'
        port = 65432
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall('QUIT')
        s.close()
        self.inst.write('logout')
        self.inst.close()

    def close(self):
        self.stop()

    def write_to_instrument(self, *messages):
        self.read_flag = 0
        for message in messages:
            self.inst.write(message)
        time.sleep(0.01)
        self.read_flag = 1

    def output_on(self):
        self.write_to_instrument('smu.source.output = smu.ON')

    def output_off(self):
        self.write_to_instrument('smu.source.output = smu.OFF')

    def set_voltage(self, num):
        self.write_to_instrument('smu.source.level = ' + str(num))

    def set_source_range(self, num):
        self.write_to_instrument('smu.source.range = ' + str(num))

    def set_source_autorange(self):
        self.write_to_instrument('smu.source.autorange = smu.ON')

    def set_measure_range(self,num):
        self.write_to_instrument('smu.measure.range = ' + str(num))

    def set_measure_autorange(self):
        self.write_to_instrument('smu.measure.autorange = smu.ON')

    def set_current_limit(self,num):
        self.write_to_instrument('smu.source.ilimit.level = ' + str(num))

    def set_overprotection(self,num):
        protection_levels = [2, 5, 10, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
        if num in protection_levels:
            protection_value = num
        else:
            if num <= 2:
                self.write_to_instrument('smu.source.protect.level = smu.PROTECT_2V')
                protection_value = 2
            else:
                protect_levels_new = protection_levels[:]
                protect_levels_new.append(num)
                protection_value = protection_levels[sorted(protect_levels_new).index(num)-1]
        if protection_value == 200:
            self.write_to_instrument('smu.source.protect.level = smu.PROTECT_NONE')
            print 'Set Overprotection to NONE'
        else:
            self.write_to_instrument('smu.source.protect.level = smu.PROTECT_' + str(protection_value) + 'V')
            print 'Set Overprotection to ' + str(protection_value) + 'V'

    def read_from_instrument(self, *messages):
        self.read_flag = 0
        while True:
            try:
                self.inst.write('*CLS')
                for message in messages:
                    self.inst.write(message)
                result = float(self.inst.query('').strip())
                self.inst.write('*CLS')
                break
            except ValueError:
                pass
        self.read_flag = 1
        return result

    def read_voltage(self):
        return self.read_from_instrument('smu.measure.read(defbuffer1)','print(defbuffer1.sourcevalues[defbuffer1.endindex])')

    def read_current(self):
        return self.read_from_instrument('print(smu.measure.read(defbuffer1))')

    def read_setpoint(self):
        return self.read_from_instrument('print(smu.source.level)')
