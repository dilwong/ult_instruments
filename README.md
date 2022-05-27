# ult_instruments

Software for controlling PNML ULTSTM (Ultra-Low Temperature Scanning Tunneling Microscope) hardware.

The Python modules in the Python subdirectory can be imported via
```
from ult_instruments import MODULE_NAME
```
where MODULE_NAME is as follows:
> triton_monitor.py : Monitors the state (pressures, temperatures) of the dilution refrigerator. Compatible with Python 2.7 and 3.
>
> sr830_lockin.py : Controls a Stanford Research Systems SR830 lock-in amplifier. Compatible with Python 2.7.
>
> keithley2400.py : Controls a Keithley 2400 SourceMeter. Compatible with Python 2.7. Untested in Python 3.
>
> keithley2450.py : Controls a Keithley 2450 SourceMeter. Compatible with Python 2.7.
>
> impedance_heater.py : Monitors and regulates the applied heat to the 2 kOhm resistor attached to the fixed impedance that feeds the 1K pot. Compatible with Python 2.7. Windows only.
>
> fridge_plot.py : Depreciated. Use triton_monitor.plot_temperature instead.
>
> mercuryIPS.py : Controls the Oxford Instruments Mercury IPS magnet power supply. Compatible with Python 2.7. Possibly compatible with Python 3, but untested.
>
> delta_es150.py : Controls a Delta Elektronika ES150 Series DC power supply. Compatible with Python 2.7. Possibly compatible with Python 3, but untested.
> 
> kepco.py : Controls a KEPCO BHK 2000-0.1MG high-voltage power supply. Currently only reads the state of the high-voltag power supply but cannot set the state. Compatible with Python 2.7, with unknown compatibility with Python 3.
>
> hp3562a.py : Controls a Hewlett Packard 3562A dual-channel, dynamic signal analyzer. Note that the HP 3562A predates the IEEE 754 floating-point standard. Compatible with Python 3. Possibly compatible with Python 2.7

Not included in this package are the routines for automatically calling some of the above Python modules, such as "init_lockin()", "init_arduino()", "init_gate()", "init_triton()", "init_magnet()", and "init_temperature()".

The LabVIEW subdirectory contains the following LabVIEW 2021 VIs:
> 'alicat gas monitor.vi' : Plot the pressure on an Alicat gas flow meter.
>
> 'capacitance nav xyz.vi' and 'capacitance navigation.vi' : Engage the coarse motor, and plot the capacitance signal during tip-sample navigation.
>
> 'const_bias_conductance.vi' : Measure the gate-dependent conductance at a fixed sample bias.
>
> 'current monitor.vi' : Plot and record the STM tunneling current and power spectral density.
>
> 'dilution walker.vi' : Similar to 'capacitance navigation.vi' except do not walk when the STM_RX or mixing chamber temperatures are too high.
>
> 'fridge night watcher.vi' : Monitors the 1K pot noise, and regulates the heat applied to the fixed impedance in order to keep the liquid helium level in the 1K pot constant.
>
> 'gate current sweep.vi' : Measure the tunneling current as a function of the gate voltage.
>
> 'gate increment.vi' : Change the gate voltage incrementally.
>
> 'gate sts with current adjustment.vi' : Similar to 'gate sts.vi' except adjust the initial setpoint current according to an input file.
>
> 'gate sts.vi' : Acquire 'Bias Spectroscopy' measurements as a function of gate voltage.
>
> 'gate_controller.vi' : Controls the gate voltage by TPC/IP communicating with a Python process running the keithley2450.py module.
>
> 'ion pump controller.vi' : Measure the pressures in the TC and AC chambers through the ion pump current. Compatible with a Gamma Vacuum DIGITEL QPC ion pump controller.
>
> 'lockin front panel.vi' : Friendly UI for controlling the SR830 lock-in amplifier.
>
> 'lockin_controller.vi' : Controls the SR830 lock-in amplifier by TCP/IP communicating with a Python process running the sr830_lockin.py module.
>
> 'magnet_controller.vi' : Controls the magnet power supply by TCP/IP communicating with a Python process running the mercuryIPS.py module.
>
> 'pressure gauge.vi' : Read and graph the pressure from an Agilent XGS-600 ion gauge controller.
>
> 'raster navigation.vi' : Raster scan the coarse motor, and make a 2D plot of the capacitance.
>
> 'scan frame to tip.vi' : Move the Nanonis Scan Control scan frame to the current location of the tip.
>
> 'temperature_watcher.vi' : Fetch insert temperatures/pressures through TCP/IP communication with a Python process running triton_monitor.py.
>
> 'triton_controller.vi' : Control and monitor the state of the dilution refrigerator through TCP/IP communication with a Python process running impedance_heater.py.
>
> 'walk tester.vi' : Test the STM coarse walker.

The Arduino subdirectory contains a simple program for controlling the pins on an Arduino with an ATmega microcontroller. Although ultimately unused, the intended purpose was controlling the following devices:
> FINDER 20.22.9.024.0000 General Purpose Relay
>
> SONGLE SRD-05VDC-SL-C PCB Relay
>
> Omron Electronics G6AK-274P-ST-US-DC5 Latching Electromagnetic Relay
>
> TDK-Lambda DSP10-24 Rail Power Supply