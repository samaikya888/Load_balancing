import socket
import time

host = "127.0.0.1"

port = 5555

clientPort = 65001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, clientPort))
    s.connect((host, port))
    print("Connected with Server")
    data = s.recv(1024)
    print(data)

    while True:
        s.send(b"")