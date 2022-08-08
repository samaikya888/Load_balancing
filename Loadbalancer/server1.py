import socket
import os
from threading import Thread
import time

#def multi_threaded_client(connection):
    #connection.send(str.encode('Server is working:'))


class Server():
    def __init__(self):
        Thread.__init__(self)  # change here
        self.requestCount = 0
        self.host = "127.0.0.1"
        self.port = int(8888)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        
    
    def start(self):      
            self.sock.listen(3000)
            print("[Info]: Listening for connections on {0}, port {1}".format(self.host,self.port))
            while True:
                print("Hello?") # Just debug for now
                client, address = self.sock.accept()
                print("connected with ",client)
                client.send(b'"connected to {0}:{1}".format(self.host,self.port)')
                self.requestCount += 1
                log= open("Loadbalancer\server1.txt", "w")
                log.write(str(self.requestCount))
                log.close()

                Thread(target = self.listenToClient, args = (client,address)).start()
    
    def listenToClient(self, client, address):
        print("listening")
        size = 1024
        while True:
            try:
                data = client.recv(size)
                print(data)
                if data:
                    print("Received data",data)
                    # Set the response to echo back the recieved data
                    print(data)
                else:
                    print("Received empty")
                    continue
            except:
                continue
    


'''
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
ServerSideSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
ServerSideSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
ServerSideSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
'''


server=Server()

log= open("Loadbalancer\server1.txt", "w")
log.write(str(server.requestCount))
log.close()

server.start()







   
