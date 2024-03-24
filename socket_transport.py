# echo-client.py

from os import wait
import socket
import time

HOST = "192.168.1.177"  # The server's hostname or IP address
PORT = 80  # The port used by the server

s = None #global variable used for the connection

def InitializeConnection():
    global s  # Access the global variable s
    try:
        s.close()  # Close the connection if it exists
    except NameError:
        pass  # Ignore if s doesn't exist yet
    except AttributeError:
        pass  # Ignore if s is already closed

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(0.5)  # Wait for a short moment (if needed)
    s.connect((HOST, PORT))  # Connect to the host and port
    SendBreak()
     
def SendHelloWorld():
        s.sendall(b"Hello, world\n")
        s.sendall(b"This is my message\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(3)

def SendSeal(start_location, end_location, speed):
        SendBreak()
        s.sendall(b"Seal_Data Start Location: " + str.encode(str(start_location)) + b" End Location: " + str.encode(str(end_location)) + b" Speed: " + str.encode(str(speed)) + b"\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        time.sleep(1)
        # CloseConnection()

def SendSetupNewPart():
        SendBreak()
        s.sendall(b"setup_new_part\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        time.sleep(1)
        
def SendSavedStarting():
        s.sendall(b"saved_starting\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(1)
        return data

def SendBreak():
        s.sendall(b"BREAK\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        # time.sleep(1)
        # return data

def ReceiveMessage():
        while(1):
                data = s.recv(1024)
                print(f"Received {data}")
                time.sleep(1)
        return data

def Heartbeat(kill_sig):
        while(not kill_sig.value):
                try:
                        s.sendall(b"heartbeat\n")
                        print("Sent Heartbeat\n")
                except:
                        print("Heartbeat failed.\n")
                        InitializeConnection()
                      

                time.sleep(5)
        print("Ending Hearbeat process\n")
        return

def CloseConnection():
     print("Sent close connection")
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"\n")
        s.close()
    

    

