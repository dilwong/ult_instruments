import datetime
import json
import time

import matplotlib.pyplot as plt

try:
    import thread
except ModuleNotFoundError:
    import _thread as thread

def plot_temperature(triton_monitor,log_filename, refresh_time, fig):
    current_time_array = []
    onek_pot_temp_array = []
    sorb_temp_array = []
    needle_valve_temp_array = []
    still_temp_array = []
    cold_plate_temp_array = []
    mix_chamber_temp_array = []
    stm_rx_temp_array = []
    stm_cx_temp_array = []
    first_time_flag = True
    while True:
        current_time = datetime.datetime.now()
        onek_pot_temp = triton_monitor.onek_pot_temp
        sorb_temp = triton_monitor.sorb_temp
        needle_valve_temp = triton_monitor.needle_valve_temp
        still_temp = triton_monitor.still_temp
        cold_plate_temp = triton_monitor.cold_plate_temp
        mix_chamber_temp = triton_monitor.mix_chamber_temp
        stm_rx_temp = triton_monitor.stm_rx_temp
        stm_cx_temp = triton_monitor.stm_cx_temp
        json_log_object = {'time':str(current_time), \
                            'pot_temp':onek_pot_temp, \
                            'sorb_temp':sorb_temp, \
                            'needle_valve_temp':needle_valve_temp, \
                            'still_temp':still_temp, \
                            'cold_plate_temp':cold_plate_temp, \
                            'mix_chamber_temp':mix_chamber_temp, \
                            'stm_rx_temp':stm_rx_temp, \
                            'stm_cx_temp':stm_cx_temp}
        with open(log_filename,'a+') as logpathfile:
            json.dump(json_log_object,logpathfile)
            logpathfile.write(',\n')
        current_time_array.append(current_time)
        onek_pot_temp_array.append(onek_pot_temp)
        sorb_temp_array.append(sorb_temp)
        needle_valve_temp_array.append(needle_valve_temp)
        still_temp_array.append(still_temp)
        cold_plate_temp_array.append(cold_plate_temp)
        mix_chamber_temp_array.append(mix_chamber_temp)
        stm_rx_temp_array.append(stm_rx_temp)
        stm_cx_temp_array.append(stm_cx_temp)
        if first_time_flag:
            first_time_flag = False
            mpd = []
            ax = fig.axes[0]
            p = ax.plot(current_time_array, onek_pot_temp_array, label = '1K Pot Temp (K)')
            mpd.append([onek_pot_temp_array, p[0]])
            p = ax.plot(current_time_array, sorb_temp_array, label = 'Sorb Temp (K)')
            mpd.append([sorb_temp_array, p[0]])
            p = ax.plot(current_time_array, needle_valve_temp_array, label = 'Needle Valve Temp (K)')
            mpd.append([needle_valve_temp_array, p[0]])
            p = ax.plot(current_time_array, still_temp_array, label = 'Still Temp (K)')
            mpd.append([still_temp_array, p[0]])
            p = ax.plot(current_time_array, cold_plate_temp_array, label = 'Cold Plate Temp (K)')
            mpd.append([cold_plate_temp_array, p[0]])
            p = ax.plot(current_time_array, mix_chamber_temp_array, label = 'Mix Chamber Temp (K)')
            mpd.append([mix_chamber_temp_array, p[0]])
            p = ax.plot(current_time_array, stm_rx_temp_array, label = 'STM RX Temp (K)')
            mpd.append([stm_rx_temp_array, p[0]])
            p = ax.plot(current_time_array, stm_cx_temp_array , label = 'STM CX Temp (K)')
            mpd.append([stm_cx_temp_array, p[0]])
            ax.legend()
            ax.set_xlabel('Date')
            fig.tight_layout()
            plt.draw()
        else:
            for mp in mpd:
                mp[1].set_data(current_time_array, mp[0])
            plt.draw()
        time.sleep(refresh_time)

def start_temperature_plot(triton_monitor, log_filename, refresh_time):
    fig = plt.figure()
    fig.add_subplot(111)
    plt.xticks(rotation=45)
    thread.start_new_thread(plot_temperature, (triton_monitor,log_filename,refresh_time,fig))