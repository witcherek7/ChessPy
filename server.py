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
import chess

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.handlers.SysLogHandler(address='/dev/log')
handler.setFormatter(formatter)
log.addHandler(handler)

board = chess.Board()
clients = []
colors = ['WHITE', 'BLACK']
server_address = ('', 6060)
mcast_grp = '224.6.6.6'

message_content = ''
message_received = False


current_board = ''
info = ''


def signal_handler(sig, frame):
    print('Closing connection.')
    for conn in clients:
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
            Thread(target=tcp_client, args=(conn,addr, len(clients))).start()
            #start_new_thread(tcp_client(conn,addr))
            continue
        except Exception as e:
            log.error("Couldn't connect client.")
            #print(e)

      

def tcp_client(conn, add, count):
    #conn.send(f"Hello, server here, you are connected.".encode())
    #conn.send(f"You are client number {count}".encode())

    while True:
        message = conn.recv(1024)
        message = message.decode()

        chess_receive(message, conn, colors[count-1])
        
        print(message)
        if not message:
            break

    #print("Closing connection.")
    conn.close()          

def test_class():
    global message_content
    global message_received
    turn = 'WHITE'
    game_started = False
    Thread(target=udp_deamon).start()
    Thread(target=tcp_deamon).start()
    log.info ("TCP and UDP threads started.")
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        if(len(clients)==2 and game_started==False):

            game_started = True
            color_count = 0
            for conn in clients:
                conn.send(f"Info:Starting the game.".encode())
                conn.send(f"Color:{colors[color_count]}".encode())
                color_count = color_count + 1
                conn.send(f"Turn:{turn}".encode())
                conn.send(f"Board:{board.board_fen()}".encode())
                conn.send(f"Info: White starts.".encode())
        
        if(len(clients)==2 and game_started==True):
            if(message_received):
                print("Message received.")
                for conn in clients:
                    turn_done = turn

                    if(turn =='WHITE'):
                        turn ='BLACK'
                    else:
                        turn = 'WHITE'

                    conn.send(f"Turn:{turn}".encode())
                    conn.send(f"Board:{board.board_fen()}".encode())
                    conn.send(f"Info:Move done by {turn_done} {message_content}".encode())

                message_received = False    


def chess_receive(message, conn, color):
    global message_content
    global message_received
    print("Chess received.")
    try:
        chess_move = chess.Move.from_uci(message)
        board.push(chess_move)       
        message_received = True
        print("Passed.")
        message_conent = message
    except:
        print("Something invalid.")
        conn.send("Info: Invalid input.".encode())


    
        

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
