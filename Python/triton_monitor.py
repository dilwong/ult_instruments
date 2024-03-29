# Monitors the status of the dilution refrigerator

#TO DO: Message boundaries for recv over TCP

import socket
import time
import traceback
import atexit
from collections import deque
try:
    import thread
except ModuleNotFoundError:
    import _thread as thread

import datetime
import re
dt_expression = r'^\s*((?P<days>[+-]?(\d*\.)?\d+)\s?d(ay)?s?)?\s*((?P<hours>[+-]?(\d*\.)?\d+)\s?h(ou(?!s)(?=r))?r?s?)?\s*((?P<minutes>[+-]?(\d*\.)?\d+)\s?(m(?!s|ute))(in)?(ute)?s?)?\s*((?P<seconds>[+-]?(\d*\.)?\d+)\s?(s(?!ond|s))(ec)?(ond)?s?)?\s*$'
dt_pattern = re.compile(dt_expression, re.IGNORECASE)
now_pattern = re.compile(r'^\s*now\s*(?P<op>(\+|-))?\s*(?P<dt>([^\W_]|\s)+)?$', re.IGNORECASE)

# This class is not a Singleton, so multiple instances check temperature and pressure independently.
class triton_monitor:
    """
    Queries Oxford Instruments Triton System Control (at IP_address, port) periodically to monitor system temperatures.

    Use triton_monitor.log(FILENAME, TIME) to record temperatures in JSON format every TIME seconds.
    Use triton_monitor.plot_temperature(TIME) to plot temperatures, sampled every TIME seconds.

    """
    
    def __init__(self, IP_address, port):

        self.IP_address = IP_address
        self.port = port
        self.function_array = [
            self._onek_pot_temp,
            self._sorb_temp,
            self._needle_valve_temp,
            self._still_temp,
            self._cold_plate_temp,
            self._mix_chamber_temp,
            self._stm_rx_temp,
            self._stm_cx_temp,
            self._tank_press,
            self._condense_press,
            self._still_press,
            self._turbo_back_press,
            self._n2_trap_press
            ]
        self.exception_list = []
        self._port_list = []
        self._logfiles = set()
        self.consecutive_exceptions = 0
        for func in self.function_array:
            func()
            time.sleep(0.02)
        self.stop = 0
        self._loop_state = 0
        self.terminate = 0
        self.lock = thread.allocate_lock()
        self.thread_counter = 1
        
        @atexit.register
        def exit_handler():
            self.terminate = 1
            self.lock.acquire()
            listen_port_list = self._port_list
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
                if self._loop_state == 0:
                    break
                else:
                    time.sleep(0.25)
        
        thread.start_new_thread(self.loop,())

        self._hash_deque = deque(maxlen= 60 * 5)
        self._unchanging = False
        thread.start_new_thread(self._check_stagnate,())
        
    def loop(self):
        self._loop_state = 1
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
        self._loop_state = 0

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
                print('Error detected in triton_monitor.read_triton')
                err = traceback.format_exc()
                print(err)
                time.sleep(5)
            finally:
                s.close()

    def get_all(self):
        return (self.onek_pot_temp,
                    self.sorb_temp,
                    self.needle_valve_temp,
                    self.still_temp,
                    self.cold_plate_temp,
                    self.mix_chamber_temp,
                    self.stm_rx_temp,
                    self.stm_cx_temp,
                    self.tank_pressure,
                    self.condense_pressure,
                    self.still_pressure,
                    self.turbo_back_pressure,
                    self.n2_trap_pressure
        )
    
    def _check_stagnate(self):

        self.lock.acquire()
        self.thread_counter += 1
        self.lock.release()

        try:
            while (self.terminate == 0):
                time.sleep(1)
                self._hash_deque.append(hash(self.get_all()))
                first_value = self._hash_deque[0]
                if all(first_value == value for value in self._hash_deque):
                    self._unchanging = True
                else:
                    self._unchanging = False
        except:
            print('Error detected in triton_monitor._check_stagnate')
            err = traceback.format_exc()
            print(err)
        finally:
            self.lock.acquire()
            self.thread_counter -= 1
            self.lock.release()

    def log(self, filename, wait_time):
        thread.start_new_thread(self._log,(filename, wait_time))

    def _log(self, filename, wait_time):

        import json

        self.lock.acquire()
        if filename in self._logfiles:
            print('Another triton_monitor.log thread is logging to ' + filename)
            print('Ignoring new request to log to ' + filename + '...')
            self.lock.release()
            return
        self._logfiles.add(filename)
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
            print('Error detected in triton_monitor._log')
            err = traceback.format_exc()
            print(err)
            print('Stopping log...')
        finally:
            try:
                self.lock.acquire()
                self.thread_counter -= 1
                self._logfiles.remove(filename)
            except KeyError:
                print('Unknown failure to remove ' + filename + ' from _logfiles.')
            finally:
                self.lock.release()

    def listen(self, port):
        thread.start_new_thread(self._listen,(port, ))
    
    def _listen(self, port):
        
        self.lock.acquire()
        if port in self._port_list:
            print('ERROR: PORT ALREADY BEING USED')
            self.lock.release()
            return
        else:
            print('TRITON MONITOR LISTENING AT PORT ' + str(port))
            self._port_list.append(port)
            self.thread_counter += 1
            self.lock.release()
        
        try:
            host = '127.0.0.1'
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((host, port))
            s.listen(0)
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
            print('Error detected in triton_monitor._listen')
            err = traceback.format_exc()
            print(err)
            print('Stopping listen...')
        finally:
            s.close()
            self.lock.acquire()
            if port in self._port_list:
                self._port_list.remove(port)
                self.thread_counter -= 1
            self.lock.release()

    # Records and plots the temperatures
    # TO DO: Optionally plot pressures
    def plot_temperature(self, refresh_time, plot = None, log_filename = None):

        import matplotlib.pyplot as plt

        if log_filename is not None:
            # Log data and plotted data are sampled at different times and so can be different.
            self.log(log_filename, refresh_time)
        if plot is None:
            plot = temperature_plot()
        plot.fig = plt.figure() # This does not work in a new thread
        plot.ax = plot.fig.add_subplot(111)
        thread.start_new_thread(self._plot,(plot, refresh_time))
        return plot
        
    def _plot(self, plot, refresh_time):
        
        import matplotlib

        self.lock.acquire()
        self.thread_counter += 1
        self.lock.release()

        try:
            while self.terminate == 0:
                # Careful: I think this is not time-zone aware. Assume we are working on EST
                plot.current_time_array.append(datetime.datetime.now())
                plot.onek_pot_temp_array.append(self.onek_pot_temp)
                plot.sorb_temp_array.append(self.sorb_temp)
                plot.needle_valve_temp_array.append(self.needle_valve_temp)
                plot.still_temp_array.append(self.still_temp)
                plot.cold_plate_temp_array.append(self.cold_plate_temp)
                plot.mix_chamber_temp_array.append(self.mix_chamber_temp)
                plot.stm_rx_temp_array.append(self.stm_rx_temp)
                plot.stm_cx_temp_array.append(self.stm_cx_temp)
                if plot.first_time_flag:
                    
                    plot.first_time_flag = False
                    
                    for arr, lbl in zip(plot.data_arrays, plot.labels):
                        p, = plot.ax.plot(plot.current_time_array, arr, label = lbl)
                        plot.lines.append(p)
                    
                    plot.legend = plot.ax.legend()
                    plot.ax.set_xlabel('Date')
                    plot.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d\n%I:%M %p'))
                    plot.fig.tight_layout()
                    
                    legend_lines = plot.legend.get_lines()
                    line_map = dict()
                    for idx, (legend_line, plot_line) in enumerate(zip(legend_lines, plot.lines)):
                        legend_line.set_picker(True)
                        legend_line.set_pickradius(5)
                        line_map[legend_line] = (plot_line, idx) # Careful: Using mutables as keys to dict

                    def pick_line(event):
                        legend_line = event.artist
                        plot_line, idx = line_map[legend_line]
                        visibility = not plot_line.get_visible()
                        plot_line.set_visible(visibility)
                        if visibility:
                            legend_line.set_alpha(1)
                        else:
                            legend_line.set_alpha(0.2)
                        plot.visible[idx] = visibility
                        plot.fig.canvas.draw()

                    plot.pick_line = pick_line
                    plot.fig.canvas.mpl_connect('pick_event', pick_line)

                    plot.fig.canvas.draw()
                else:
                    for line, arr in zip(plot.lines, plot.data_arrays):
                        line.set_data(plot.current_time_array, arr)
                    plot.fig.canvas.draw()
                time.sleep(refresh_time)
        except Exception:
            print('Error detected in triton_monitor._plot')
            err = traceback.format_exc()
            print(err)
        finally:
            self.lock.acquire()
            self.thread_counter -= 1
            self.lock.release()

# Auxiliary object that stores the temperatures in arrays and has helper methods for configuring plot axes
class temperature_plot:
    
    def __init__(self):
        self.current_time_array = []
        self.onek_pot_temp_array = []
        self.sorb_temp_array = []
        self.needle_valve_temp_array = []
        self.still_temp_array = []
        self.cold_plate_temp_array = []
        self.mix_chamber_temp_array = []
        self.stm_rx_temp_array = []
        self.stm_cx_temp_array = []
        self.first_time_flag = True
        self.fig = None
        self.ax = None
        self.legend = None

        self.data_arrays = [
            self.onek_pot_temp_array,
            self.sorb_temp_array,
            self.needle_valve_temp_array,
            self.still_temp_array,
            self.cold_plate_temp_array,
            self.mix_chamber_temp_array,
            self.stm_rx_temp_array,
            self.stm_cx_temp_array
        ]
        self.labels = [
            '1K Pot Temp (K)',
            'Sorb Temp (K)',
            'Needle Valve Temp (K)',
            'Still Temp (K)',
            'Cold Plate Temp (K)',
            'Mix Chamber Temp (K)',
            'STM RX Temp (K)',
            'STM CX Temp (K)'
        ]
        self.lines = []
        self.visible = [True] * 8
    
    # Input x_min and x_max as a human-readable date string.
    # Do not input a datetime.datetime object or a Unix time float!
    #
    # Alternatively, insert None for x_min or x_max to keep the left or right axis value the same.
    # Or insert 'now' for x_min or x_max for the current date/time.
    # Or insert 'now + 15 min', 'now + 1day2hrs', etc...
    #
    # TO DO: Scrub inputs
    def xlim(self, x_min, x_max):
        if self.ax is None:
            print('Error: Figure ax not yet initialized')
        else:
            import dateutil
            from matplotlib.dates import num2date
            # TO DO: Refactor to remove code duplication between x_min and x_max cases
            if x_min is None:
                x_min, _ = self.ax.get_xlim()
                x_min = num2date(x_min) # Convert days since epoch to datetime object to compare x_min and x_max
                x_min = datetime.datetime.combine(x_min.date(), x_min.time()) # Strip timezone info
            elif x_min.lower()[:3] == 'now':
                x_min = parse_now_string(x_min)
            else:
                x_min = dateutil.parser.parse(x_min)
            if x_max is None:
                _, x_max = self.ax.get_xlim()
                x_max = num2date(x_max) # Convert days since epoch to datetime object to compare x_min and x_max
                x_max = datetime.datetime.combine(x_max.date(), x_max.time()) # Strip timezone info
            elif x_max.lower()[:3] == 'now':
                x_max = parse_now_string(x_max)
            else:
                x_max = dateutil.parser.parse(x_max)
            if x_min > x_max: # matplotlib handles the x_min == x_max case automatically
                x_min, x_max = x_max, x_min
            self.ax.set_xlim(x_min, x_max)
    
    def ylim(self, y_min, y_max):
        if self.ax is None:
            print('Error: Figure ax not yet initialized')
        else:
            if y_min is None:
                y_min, _ = self.ax.get_ylim()
            if y_max is None:
                _, y_max = self.ax.get_ylim()
            if y_min > y_max: # matplotlib handles the y_min == y_max case automatically
                y_min, y_max = y_max, y_min
            self.ax.set_ylim(y_min, y_max)
    
    def full_range(self):
        if (self.ax is None) or (len(self.current_time_array) == 0):
            print('Error: Figure ax not yet initialized')
            return
        y_min = 99999
        y_max = 0
        for vis, arr in zip(self.visible, self.data_arrays):
            if not vis:
                continue
            min_candidate = min(arr)
            max_candidate = max(arr)
            if min_candidate < y_min:
                y_min = min_candidate
            if max_candidate > y_max:
                y_max = max_candidate
        if y_min < y_max:
            self.ax.set_ylim(y_min - 2, y_max + 2)
        x_min = min(self.current_time_array)
        x_max = max(self.current_time_array)
        print(x_min)
        print(x_max)
        if x_min < x_max:
            self.ax.set_xlim(x_min - datetime.timedelta(hours = 0.25), x_max + datetime.timedelta(hours = 0.25))

def parse_string_to_timedelta(s):

    match = dt_pattern.match(s)
    if match is not None:
        return datetime.timedelta(**{unit: float(value) for unit, value in match.groupdict().items() if value is not None})
    else:
        return None

def parse_now_string(s):

    t = datetime.datetime.now()
    
    match = now_pattern.match(s)
    if match is not None:
        match_dict = match.groupdict()
    else:
        return t

    if (match_dict['op'] is None) or (match_dict['dt'] is None):
        return t
    dt = parse_string_to_timedelta(match_dict['dt']) # ''.join(match_dict['dt'].split())
    if dt is not None:
        if match_dict['op'] == '+':
            t = t + dt
        elif match_dict['op'] == '-':
            t = t - dt
    return t