# echo-client.py

from os import wait
import socket
import time, multiprocessing
from data_logging import append_distances_to_csv #my logging functions
from seals_implementation import *
# from main import SavedSeals

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

    global socket_receive_process
    global parent_conn
    global child_conn
    parent_conn, child_conn = multiprocessing.Pipe()

    socket_receive_process = multiprocessing.Process(target=ReceiveMessage, args=(child_conn,))
    socket_receive_process.start()
     
def SendHelloWorld():
        s.sendall(b"Hello, world\n")
        s.sendall(b"This is my message\n")
        data = s.recv(1024)
        print(f"Received {data}")
        time.sleep(3)

def SendSeal(start_location, end_location, speed, seal_idx):
        SendBreak()
        
        s.sendall(b"Seal_Data Start Location: " + str.encode(str(start_location)) + b" End Location: " + str.encode(str(end_location)) + b" Speed: " + str.encode(str(speed)) + b"\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        time.sleep(1)
        
        parent_conn.send(seal_idx)
        # CloseConnection()

def SendSetupNewPart():
        SendBreak()
        s.sendall(b"setup_new_part\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        time.sleep(1)
        
def SendSavedStarting():

        global socket_receive_process
        socket_receive_process.terminate()
        socket_receive_process.join()  # Wait for the process to terminate


        s.sendall(b"saved_starting\n")
        data = s.recv(1024)
        # print(f"Received {data}")
        time.sleep(1)

        socket_receive_process = multiprocessing.Process(target=ReceiveMessage, args=(child_conn,))
        socket_receive_process.start()
        return data

def SendBreak():
        s.sendall(b"BREAK\n")
        # data = s.recv(1024)
        # print(f"Received {data}")
        # time.sleep(1)
        # return data

def ReceiveMessage(conn):
        print("Starting receive message process\n")
        start_measurement = -1
        end_measurement = -1
        while(1):
                data = s.recv(1024)
                print(f"Received {data}")

                if data.startswith(b"LOG"):
                        # Convert bytes to string
                        data_str = data.decode('utf-8')
                        parts = data_str.split(':')
                        print("Parts:" + str(parts))
                        if "START" in parts:
                                print("Start in parts")
                                # Extract CODE and number for START message
                                start_index = parts.index('START')
                                start_measurement = float(parts[start_index + 1])

                        elif "END" in parts:
                                # Extract CODE and number for END message
                                end_index = parts.index('END')
                                end_measurement = float(parts[end_index + 1])
                                stretch_duration = float(parts[end_index + 2])
                                #ensure getting last sent value
                                while conn.poll():
                                        seal_on_PLC = conn.recv() #no longer using the global seal_on_PLC
                                print("IN end, seal on plc has value: " + str(seal_on_PLC))
                                
                                if (start_measurement == -1):
                                       print("ERROR: END measurment received without start measurement. Not logging this stretch\n")
                                
                                elif (seal_on_PLC == -1):
                                       print("ERROR: Do not know seal on PLC. Reload seal to continue logging")
                                else:
                                       # Start a new process for logging routine
                                        part_idx = seal_on_PLC; #will need to change this
                                        print("Seal on PLC value:" + str(seal_on_PLC))
                                        saved_seals_handler = SavedSeals()
                                        saved_seals_handler.load_seals()
                                        part = saved_seals_handler.saved_seals[part_idx]
                                        logging_process = multiprocessing.Process(target=append_distances_to_csv, args=(part, start_measurement, end_measurement, stretch_duration))
                                        logging_process.start()
                        else:
                                print("Start nor End in parts")


                time.sleep(1)
                
        print("Ending receive message process\n")
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
    

    

