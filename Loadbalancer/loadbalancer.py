import sys
import socket
import select
import random


SERVER_POOL = {"server1":('127.0.0.1', 8888),"server2":('127.0.0.1', 8889),"server3":('127.0.0.1', 8886),"server4":('127.0.0.1', 9000),"server5":('127.0.0.1', 9001),"server6":('127.0.0.1', 9002),"server7":('127.0.0.1', 9003),"server8":('127.0.0.1', 9004),"server9":('127.0.0.1', 9005),"server10":('127.0.0.1', 9006),"server11":('127.0.0.1', 9007),"server12":('127.0.0.1', 9008),"server13":('127.0.0.1', 9009),"server14":('127.0.0.1', 9010),"server15":('127.0.0.1', 9011)}

server_log = [("server1.txt","server1"),("server2.txt","server2"),("server3.txt","server3"),("server4.txt","server4"),("server5.txt","server5"),("server6.txt","server6"),("server7.txt","server7"),("server8.txt","server8"),("server9.txt","server9"),("server10.txt","server10"),("server11.txt","server11"),("server12.txt","server12"),("server13.txt","server13"),("server14.txt","server14"),("server15.txt","server15")]



def least_connection():
    
    server_connections = []
    for files in server_log:
       file,server = files[0], files[1]
       print(file)
       print(server)
       file = 'Loadbalancer/'+ file
       f = open(file)
       reqCount = int(f.read().strip())
       f.close()
       server_connections.append((SERVER_POOL[server],reqCount))
    
    print(server_connections)
    print(min(server_connections, key = lambda t: t[1]))
    res = min(server_connections, key = lambda t: t[1])
    print(res)
    return res[0]

    

def two_choice():
    x = random.choice(server_log)
    xFile = x[0]
    file = 'Loadbalancer/'+ xFile
    f1 = open(file)
    xCount = int(f1.read().strip())
    f1.close()

    y = random.choice(server_log)   
    yFile = y[0]
    file = 'Loadbalancer/'+ yFile
    f2 = open(file)
    yCount = int(f2.read().strip())
    f2.close()

    if xCount<=yCount:
        return SERVER_POOL[x[1]]
    else:
        return SERVER_POOL[y[1]]



    
class LoadBalancer(object):
    """ Socket implementation of a load balancer.
    Flow Diagram:
    +---------------+      +-----------------------------------------+      +---------------+
    | client socket | <==> | client-side socket | server-side socket | <==> | server socket |
    |   <client>    |      |          < load balancer >              |      |    <server>   |
    +---------------+      +-----------------------------------------+      +---------------+
    Attributes:
        ip (str): virtual server's ip; client-side socket's ip
        port (int): virtual server's port; client-side socket's port
        algorithm (str): algorithm used to select a server
        flow_table (dict): mapping of client socket obj <==> server-side socket obj
        sockets (list): current connected and open socket obj
    """

    flow_table = dict()
    sockets = list()

    def __init__(self, ip, port, algorithm='random'):
        self.ip = ip
        self.port = port
        self.algorithm = algorithm

        # init a client-side socket
        self.cs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cs_socket.bind((self.ip, self.port))
        print(('init client-side socket: %s') % (self.cs_socket.getsockname(),))
        self.cs_socket.listen(10000) # max connections
        self.sockets.append(self.cs_socket)
        print(self.sockets)

    def start(self):
        while True:
            read_list, write_list, exception_list = select.select(self.sockets, [], [])
            print(read_list)
            for sock in read_list:
                # new connection
                if sock == self.cs_socket:
                    print ('='*40+'flow start'+'='*39)
                    self.on_accept()
                    break
                # incoming message from a client socket
                else:
                    try:
                        # In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(4096) # buffer size: 2^n
                        if data:
                            self.on_recv(sock, data)
                        else:
                            self.on_close(sock)
                            break
                    except:
                        sock.on_close(sock)
                        break

    def on_accept(self):
        client_socket, client_addr = self.cs_socket.accept()
        print ('client connected: %s <==> %s' % (client_addr, self.cs_socket.getsockname()))

        # select a server that forwards packets to
        server_ip, server_port = self.select_server(SERVER_POOL, self.algorithm)

        # init a server-side socket
        ss_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ss_socket.connect((server_ip, server_port))
            print ('init server-side socket: %s' % (ss_socket.getsockname(),))
            print ('server connected: %s <==> %s' % (ss_socket.getsockname(),(socket.gethostbyname(server_ip), server_port)))
        except:
            print ("Can't establish connection with remote server, err: %s" % sys.exc_info()[0])
            print ("Closing connection with client socket %s" % (client_addr,))
            client_socket.close()
            return

        self.sockets.append(client_socket)
        self.sockets.append(ss_socket)

        self.flow_table[client_socket] = ss_socket
        self.flow_table[ss_socket] = client_socket

    def on_recv(self, sock, data):
        print ('recving packets: %-20s ==> %-20s, data: %s' % (sock.getpeername(), sock.getsockname(), [data]))
        # data can be modified before forwarding to server
        # lots of add-on features can be added here
        remote_socket = self.flow_table[sock]
        remote_socket.send(data)
        print ('sending packets: %-20s ==> %-20s, data: %s' % (remote_socket.getsockname(), remote_socket.getpeername(), [data]))

    def on_close(self, sock):
        print ('client %s has disconnected' % (sock.getpeername(),))
        print ('='*41+'flow end'+'='*40)

        ss_socket = self.flow_table[sock]

        self.sockets.remove(sock)
        self.sockets.remove(ss_socket)

        sock.close()  # close connection with client
        ss_socket.close()  # close connection with server

        del self.flow_table[sock]
        del self.flow_table[ss_socket]

    def select_server(self, server_list, algorithm):
        if algorithm == 'random':
            return random.choice(server_list)
        
        elif algorithm == 'least connection':
            return least_connection()
        
        elif algorithm == 'two choice':
            return two_choice()
        else:
            raise Exception('unknown algorithm: %s' % algorithm)


if __name__ == '__main__':
    try:
        LoadBalancer('localhost', 5555, 'two choice').start()
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping load_balancer")
        sys.exit(1)
