# ult_instruments

Software for controlling PNML ULTSTM (Ultra-Low Temperature Scanning Tunneling Microscope) hardware.

The Python modules in the Python subdirectory can be imported via
```
from ult_instruments import MODULE_NAME
```
where MODULE_NAME is as follows:
> triton_monitor.py : Monitors the state (pressures, temperatures) of the dilution refrigerator.
>
> sr830_lockin.py : Controls a Stanford Research Systems SR830 lock-in amplifier.
>
> keithley2400.py : Controls a Keithley 2400 SourceMeter.
>
> keithley2450.py : Controls a Keithley 2450 SourceMeter.
>
> impedance_heater.py : Monitors and regulates the applied heat to the 2 kOhm resistor attached to the fixed impedance that feeds the 1K pot. Windows only.
>
> mercuryIPS.py : Controls the Oxford Instruments Mercury IPS magnet power supply.
>
> delta_es150.py : Controls a Delta Elektronika ES150 Series DC power supply.
> 
> kepco.py : Controls a KEPCO BHK 2000-0.1MG high-voltage power supply. Currently only reads the state of the high-voltag power supply but cannot set the state.
>
> hp3562a.py : Controls a Hewlett Packard 3562A dual-channel, dynamic signal analyzer. Note that the HP 3562A predates the IEEE 754 floating-point standard.

Not included in this package are the routines for automatically calling some of the above Python modules, such as "init_lockin()", "init_arduino()", "init_gate()", "init_triton()", "init_magnet()", and "init_temperature()". Compatibility with Python 2.7 was dropped in version 4.0.0.

The LabVIEW subdirectory contains the following LabVIEW 2021 VIs:
> 'alicat_gas_monitor.vi' : Plot the pressure on an Alicat gas flow meter.
>
> 'CapacitanceNavigation.vi' and 'capacitance_navigation_xyz.vi' : Engage the coarse motor, and plot the capacitance signal during tip-sample navigation.
>
> 'clear_sts_attributes.vi' : Erase attributes in 'gate sts.vi' (which was renamed to 'GateSTS.vi').
>
> 'const_bias_conductance.vi' : Measure the gate-dependent conductance at a fixed sample bias.
>
> 'current_monitor.vi' : Plot and record the STM tunneling current and power spectral density.
>
> 'DilutionWalker.vi' : Similar to 'CapacitanceNavigation.vi' except do not walk when the STM_RX or mixing chamber temperatures are too high.
>
> 'DualGateSTS.vi' : Acquire 'Bias Spectroscopy' measurements as a function of two independent gate voltages. Calls 'GateSTS.vi'.
>
> 'FridgeNightWatcher.vi' : Monitors the 1K pot noise, and regulates the heat applied to the fixed impedance in order to keep the liquid helium level in the 1K pot constant.
>
> 'GateCurrentSweep.vi' : Measure the tunneling current as a function of the gate voltage.
>
> 'GateIncrement.vi' : Change the gate voltage on a Keithley 2450 SourceMeter incrementally.
>
> 'GateSTSwithCurrentAdjustment.vi' : Similar to 'GateSTS.vi' except adjust the initial setpoint current according to an input file. This has not been updated to save to HDF5 file format.
>
> 'GateSTS.vi' : Acquire 'Bias Spectroscopy' measurements as a function of gate voltage.
>
> 'gate_controller.vi' : Controls the gate voltage by TPC/IP communicating with a Python process running the keithley2450.py module.
>
> 'ion_gauge_pressure.vi' : Read and graph the pressure from an Agilent XGS-600 ion gauge controller.
>
> 'IonPumpPressure.vi' : Measure the pressures in the TC and AC chambers through the ion pump current. Compatible with a Gamma Vacuum DIGITEL QPC ion pump controller.
>
> 'LockinFrontPanel.vi' : Friendly UI for controlling the SR830 lock-in amplifier.
>
> 'lockin_controller.vi' : Controls the SR830 lock-in amplifier by TCP/IP communicating with a Python process running the sr830_lockin.py module.
>
> 'magnet_controller.vi' : Controls the magnet power supply by TCP/IP communicating with a Python process running the mercuryIPS.py module.
>
> 'raster_navigation.vi' : Raster scan the coarse motor, and make a 2D plot of the capacitance.
>
> 'scan_frame_to_tip.vi' : Move the Nanonis Scan Control scan frame to the current location of the tip.
>
> 'second_gate_controller.vi' : Controls the gate voltage by TPC/IP communicating with a Python process running the keithley2400.py module.
>
> 'SecondGateIncrement.vi' : Change the gate voltage on a Keithley 2400 SourceMeter incrementally.
>
> 'temperature_watcher.vi' : Fetch insert temperatures/pressures through TCP/IP communication with a Python process running triton_monitor.py.
>
> 'triton_controller.vi' : Control and monitor the state of the dilution refrigerator through TCP/IP communication with a Python process running impedance_heater.py.
>
> 'walker_tester.vi' : Test the STM coarse walker.