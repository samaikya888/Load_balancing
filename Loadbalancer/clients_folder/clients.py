import socket
import time
from threading import Thread

def threadFunction(clientPort):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.bind((host, clientPort))
        sock_list.append(s)
        s.connect((host, port))
        print("Connected with Server")
        data = s.recv(1024)
        print(data)

        while True:
            s.send(b"")


host = "127.0.0.1"

port = 5555

#clientPort = 10000

sock_list = []

for i in range(10100,10200):
    try:
        t = Thread(target=threadFunction,args = (i,))
        t.start()
    except:
        continue
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.bind((host, clientPort+i))
        sock_list.append(s)
        s.connect((host, port))
        print("Connected with Server")
        data = s.recv(1024)
        print(data)

        while True:
            s.send(b"")
    '''