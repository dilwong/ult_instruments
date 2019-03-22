#triton_pressure.py
#Reads pressures from Triton
#Dillon Wong 11/07/2018

import socket

#Dump pressure
def tank(IP_address, port):
    message = 'READ:DEV:P1:PRES:SIG:PRES\n'
    return read_triton_pressure(IP_address, port, message)

def condense(IP_address, port):
    message = 'READ:DEV:P2:PRES:SIG:PRES\n'
    return read_triton_pressure(IP_address, port, message)

def still(IP_address, port):
    message = 'READ:DEV:P3:PRES:SIG:PRES\n'
    return read_triton_pressure(IP_address, port, message)

def turbo_back(IP_address, port):
    message = 'READ:DEV:P4:PRES:SIG:PRES\n'
    return read_triton_pressure(IP_address, port, message)

def n2_trap(IP_address, port):
    message = 'READ:DEV:P5:PRES:SIG:PRES\n'
    return read_triton_pressure(IP_address, port, message)

def read_triton_pressure(IP_address, port, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send(message.encode())
    response = str(s.recv(4096).decode())
    s.close()
    return float(response.split(':')[6][:-3])
