#triton_temperature.py
#Reads temperatures from Triton
#Dillon Wong 11/03/2018

import socket

def onek_pot(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T2:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def sorb(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T1:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def needle_valve(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T8:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def still(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T3:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def cold_plate(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T4:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def mix_chamber(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T5:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def stm_rx(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T6:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])

def stm_cx(IP_address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, port))
    s.send('READ:DEV:T7:TEMP:SIG:TEMP\n')
    response = s.recv(4096)
    s.close()
    return float(response.split(':')[6][:-2])
    
