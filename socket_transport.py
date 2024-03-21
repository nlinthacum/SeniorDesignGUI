# echo-client.py

from os import wait
import socket
import time

HOST = "192.168.1.177"  # The server's hostname or IP address
PORT = 80  # The port used by the server
def SendHelloWorld():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"Hello, world\n")
        s.sendall(b"This is my message\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(3)
def SendSeal(start_location, end_location, speed):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"Seal_Data Start Location: " + str.encode(str(start_location)) + b" End Location: " + str.encode(str(end_location)) + b" Speed: " + str.encode(str(speed)) + b"\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(1)
        # CloseConnection()

def SendSetupNewPart():
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"setup_new_part\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(1)
        
def SendSavedStarting():
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"saved_starting\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(1)
        return data

def ListenForLogging():
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # s.sendall(b"s\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(1)
        return data

def CloseConnection():
     print("Sent close connection")
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"\n")
        s.close()
    

    

