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



x_label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
y_label = ['1', '2', '3', '4', '5', '6', '7', '8']

desc = ['Uppercase - WHITE',
        'Lowercase - BLACK',
        'K - King',
        'Q - Queen',
        'R - Rook',
        'B - Bishop',
        'K - Knight',
        'P - Pawn']

# --------Logging----------- 
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.handlers.SysLogHandler(address='/dev/log')
handler.setFormatter(formatter)
log.addHandler(handler)


# --------Global Variables---------
board = chess.Board()
clients = []
colors = ['WHITE', 'BLACK']
server_address = ('', 6060)
mcast_grp = '224.6.6.6'
game_started = False
turn = 'WHITE'

# ----------SIG HANDLER------------
def signal_handler(sig, frame):
    print('Closing connection.')
    for conn in clients:
        conn.close()
    exit()

# ---------Multicast service-----------

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

# ---------Unicast service---------------
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
            Thread(target=tcp_client, args=(conn,addr, len(clients)-1)).start()
            #start_new_thread(tcp_client(conn,addr))
            continue
        except Exception as e:
            log.error("Couldn't connect client.")
            #print(e)

# ---------TCP Thread-----------------

def tcp_client(conn, add, index):
    #conn.send(f"Hello, server here, you are connected.".encode())
    #conn.send(f"You are client number {count}".encode())

    while True:
        message = conn.recv(1024)
        message = message.decode()
        chess_receive(conn,message,index)

        #chess_receive(message, conn, colors[count-1])
        
        print(message)
        if not message:
            break

    #print("Closing connection.")
    conn.close()   

def chess_display(board, color):
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    global turn
    print("--------------------------------------------------------")
    print(f"  Your color: {color}")
    print(f"    Turn: {turn}\n")
    text_part = 0 
    text = board.board_fen()
    text = text.split('/')
    print("   ", end='')
    for label in x_label:
        if label == 'H':
            print(label, end='\n\n')
        else:
            print(label, end=' ')
    for label in reversed(y_label):
        # for x in range(0, 17):
        #     if(x == 16):
        #         print("–", end="\n")
        #     else:
        #         print("–", end="")
        print(label, end=' ')
        for letter in text[text_part]:
            if(letter.isdigit()):
                for nothing in range (0, int(letter)):
                    print("| ", end='')
            else:
                print(f"|{letter}",end='')
        print(f'|     {desc[text_part]}', end = '')
        print("\n",end='')    
        text_part = text_part + 1
    print('\n')
    sys.stdout = old_stdout
    return mystdout.getvalue()

def chess_start():
    global turn
    global game_started

    while True:
        if(len(clients)==2 and game_started==False):
            print("Starting the ches game")
            game_started = True
            for index, conn in enumerate(clients):
                conn.send(f"Info:Starting the game.".encode())
                conn.send(f"Board:{chess_display(board,colors[index])}".encode())
                conn.send(f"Info: White starts.".encode())

def disconnect_cliens():
    print("TO BE DONE")

def chess_receive(conn,message, index):
    global game_started
    global clients
    global turn
    if(game_started):
        if(colors[index]==turn):
            try:
                chess_move = chess.Move.from_uci(message)
                if(chess_move not in board.legal_moves):
                    raise Exception("Illegal move.")
                board.push(chess_move) 
                turn = colors[1-index]

                for connections in clients:
                    connections.send(f"Board:{chess_display(board,colors[index])}".encode())
                    connections.send(f"Info: Move done by {colors[index]} {message}".encode())
                    if(board.is_check()):
                        connections.send(f"Info: Check!".encode())
                    if(board.is_checkmate()):
                        connections.send(f"Info: Checkmate!".encode())
                        connections.send(f"Info: Gameover! {colors[index]} wins!".encode())
            except Exception as e:
                print(e)
                conn.send(f"Info: Bad move {message}, try again.".encode())

        else:
            conn.send("Info: Not your turn.".encode())    
    else:
        conn.send("Info: Game not started.".encode())

def server_start():
    Thread(target=udp_deamon).start()
    Thread(target=tcp_deamon).start()
    log.info ("TCP and UDP threads started.")
    signal.signal(signal.SIGINT, signal_handler)
    chess_start()

server_start()