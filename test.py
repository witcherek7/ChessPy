import socket
import select
import sys
from _thread import *
import struct
from daemon import *
import logging
import logging.handlers
from multiprocessing import Process
from threading import Thread
import time


clients = []
server_address = ('', 6060)
mcast_grp = '224.6.6.6'

def udp_deamon():
    while True:
        print(1)
        server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_udp.bind(server_address)
        group = socket.inet_aton(mcast_grp)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        server_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        data, address = server_udp.recvfrom(1024)
        print(f"Received data from {address}")
        server_udp.sendto('server-ack'.encode(), address)

def tcp_deamon():
    while True:
        print(2)
        server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_tcp.bind(server_address)

        server_tcp.listen(2)
        conn, addr = server_tcp.accept()
        clients.append(conn)





thread_udp = Thread(target=udp_deamon, args = ())
thread_udp.start()
thread_tcp = Thread(target=tcp_deamon, args = ())
thread_tcp.start()

