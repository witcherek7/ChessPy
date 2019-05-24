import socket
import select
import sys
from _thread import *
from threading import Thread
import struct
from daemon import *
import logging
import logging.handlers
from multiprocessing import Process
import signal

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.handlers.SysLogHandler(address='/dev/log')
handler.setFormatter(formatter)
log.addHandler(handler)

clients = []
server_address = ('', 6060)
mcast_grp = '224.6.6.6'

def signal_handler(sig, frame, conn):
    print('Closing connection.')
    conn.close()
    exit()


def udp_deamon():
    while True:
        try:
            server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_udp.bind(server_address)
            group = socket.inet_aton(mcast_grp)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            server_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            log.info("Socket UDP for port 6060 created and binded.")
        except:
            log.error("Socket UDP for port 6060 couldn't be created or binded")

        data, address = server_udp.recvfrom(1024)
        #print(f"Received multicast data from {address}")
        server_udp.sendto('server-ack'.encode(), address)

def tcp_deamon():
    try:
        server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_tcp.bind(server_address)
        log.info("Socket TCP for port 6060 created and binded.")
    except Exception as e:
        print(e)
        log.error("Socket TCP for port 6060 couldn't be created or binded")
    
    while True:  
        try:
            server_tcp.listen(2)
            conn, addr = server_tcp.accept()
            clients.append(conn)
            log.info(f"{addr[0]} IS CONNECTED")
            Thread(target=tcp_client, args=(conn,addr)).start()
            #start_new_thread(tcp_client(conn,addr))
            continue
        except Exception as e:
            log.error("Couldn't connect client.")
            #print(e)

      

def tcp_client(conn, addr):
    conn.send(f"Hello, server here, you are connected.".encode())
    while True:
        message = conn.recv(1024)
        message = message.decode()
        #print(message)
        if not message:
            break
    #print("Closing connection.")
    conn.close()          

def test_class():
        Thread(target=udp_deamon).start()
        Thread(target=tcp_deamon).start()
        log.info ("TCP and UDP threads started.")
        

test_class()


# class ChessDaemon(Daemon):
#     def run(self):
        
#         Thread(target=udp_deamon).start()
#         Thread(target=tcp_deamon).start()
#         log.info ("TCP and UDP threads started.")


           

 
# if __name__ == "__main__":
# 	daemon = ChessDaemon('/tmp/chess_daemon.pid')
# 	if len(sys.argv) == 2:
# 		if 'start' == sys.argv[1]:
# 			daemon.start()
# 		elif 'stop' == sys.argv[1]:
# 			daemon.stop()
# 		elif 'restart' == sys.argv[1]:
# 			daemon.restart()
# 		else:
# 			print("Unknown command")
# 			sys.exit(2)
# 		sys.exit(0)
# 	else:
# 		print("usage: %s start|stop|restart" % sys.argv[0])
# 		sys.exit(2)
