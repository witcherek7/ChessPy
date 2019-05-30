import sys, time
import socket
import struct
import select

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


servers = []
clients = []

color = ''
turn = ''

def find_clients():
    message = "Looking for clients"
    encoded_message = message.encode()
    mcast_grp = ('224.7.7.7', 7070)
    client_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_mcast.settimeout(1)
    ttl = struct.pack('b',1)
    client_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        sent = client_mcast.sendto(encoded_message, mcast_grp)
        while True:
            data, addr = client_mcast.recvfrom(16)
            print(f"Chess client {addr[0]} available.")
            clients.append(addr[0])
    except:
        client_mcast.close()
    finally:
        client_mcast.close()    

def find_servers():
    message = "Looking for servers"
    encoded_message = message.encode()
    mcast_grp = ('224.6.6.6', 6060)
    client_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_mcast.settimeout(1)
    ttl = struct.pack('b',1)
    client_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        sent = client_mcast.sendto(encoded_message, mcast_grp)
        while True:
            data, addr = client_mcast.recvfrom(16)
            print(f"Chess server {addr[0]} available.")
            servers.append(addr[0])
    except:
        client_mcast.close()
    finally:
        client_mcast.close()    

def show_servers():
    print(servers)

def show_clients():
    print(clients)

def receive_message(sock):
    global turn, color
    while True:
        sockets_list = [sys.stdin, sock]
        try:
            read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

            for socks in read_sockets:
                if socks == sock:
                    message = socks.recv(1024)
                    message = message.decode()
                    #print (message)

                    chess_receive(message)

                    if not message:
                        sock.close()
                else:
                    # message = input("send>>:")
                    # message = message.encode('utf8')
                    # sock.send(message)
                    #if(color!=''):
                    chess_move(color, turn, sock)

        except Exception as e:
            print(e)
            print("You were disconnected.")
            exit()


def chess_receive(message):
    global color, turn
    if('Color:' in message):
        color = message.split(":")[1]
    elif('Turn:' in message):
        turn = message.split(":")[1]
    elif('Board:' in message):
        chess_display(message.split(":")[1])
    elif('Info:' in message):
        print(f"Info: {message.split(':')[1]}")
        

def chess_display(board):
    global turn, color
    print("--------------------------------------------------------")
    print(f"  Your color: {color}")
    print(f"    Turn: {turn}\n")
    text_part = 0 
    text = board
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

def chess_move(color,turn, sock):
    if(color == turn):
        player_input = input("command>>")
        sock.send(player_input.encode())


if __name__ == "__main__":

    # if ((len(sys.argv) != 2) or sys.argv[1]!='peer-to-peer' or sys.argv[1]!='client-server'):
    #     print("Usage: 'python3 peer-to-peer|client-server'")
    #     exit()

    mode = sys.argv[1]

    while True:
        if(mode == 'peer-to-peer'):
            print("Not done yet.")
        if(mode == 'client-server'):
            find_servers()
            server = servers[0]
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, 6060))
            print(f"Connected to {server}")
            receive_message(sock)

