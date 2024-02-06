# echo-client.py

from os import wait
import socket
import time

HOST = "192.168.1.177"  # The server's hostname or IP address
PORT = 80  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world\n")
    s.sendall(b"This is my message\n")
    data = s.recv(1024)
    print(f"Received {data}")
    time.sleep(3)
    

