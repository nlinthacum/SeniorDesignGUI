# Python script that receives the start and end measurements from the PLC

from os import wait
import socket
import time

HOST = "192.168.1.177"  # The server's hostname or IP address
PORT = 80  # The port used by the server; Can the PLC have more than 1 connection?




def SendHelloWorld():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"I am looking for logging data\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(3)

