import sys, time
import socket
import struct
import select



servers = []
clients = []

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
    while True:
        sockets_list = [sys.stdin, sock]
        read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

        for socks in read_sockets:
            if socks == sock:
                message = socks.recv(1024)
                message = message.decode()
                print (message)
            else:
                message = input("send>>:")
                message = message.encode('utf8')
                sock.send(message)

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

