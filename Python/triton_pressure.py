#triton_pressure.py
#Reads pressures from Triton
#Dillon Wong 11/07/2018

import socket

#Dump pressure
def tank(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:P1:PRES:SIG:PRES\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-3])

def condense(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:P2:PRES:SIG:PRES\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-3])

def still(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:P3:PRES:SIG:PRES\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-3])

def turbo_back(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:P4:PRES:SIG:PRES\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-3])

def n2_trap(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:P5:PRES:SIG:PRES\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-3])
