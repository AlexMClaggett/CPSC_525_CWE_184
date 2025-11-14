import json
import socket
import sys
import threading
import logging
import signal
import hashlib
from enum import Enum
import server


class ClientState(Enum):
    IN_USER_MENU = 0
    IN_CHAT = 1
    DISCONNECTED = 2



class ClientHandler:
    def __init__(self, socket, addr, user_name):
        # Var init
        self.client_socket = socket
        self.state = ClientState(0)
        self.client_address = addr
        self.user_name = user_name
        self.user_connection = None
        # 
        self.set_state(ClientState.IN_USER_MENU)
        server.logging.info(f"Connection from {self.client_address}")
    
    
    def set_state(self, new_state):
        # do changes as needed
        match new_state:
            case ClientState.IN_USER_MENU:
                self.client_socket.sendall("Please type the name of the person you wish to talk to:".encode())
                client_list_print = ""
                for i in range(0, len(server.clients)):
                    client_list_print += "\t" + server.clients[i]
                    if i % 2 == 0: client_list_print += "\n"
                self.client_socket.sendall(client_list_print.encode())
            case ClientState.IN_CHAT:
                sort = sorted([self.user_name, self.user_connection])
                file_name = "".join(sort)
                ascii_file_name = ""
                #put the filename into ascii format because of windows file format 
                file_name = "_".join(file_name)
                print(f"Socket = {self.client_socket}")
                for char in file_name:
                    ascii_file_name += str(ord(char)) if char != "_"else "_"
                try:
                    print(f"file name = {ascii_file_name}")
                    ascii_file_name += ".txt"
                    with open(ascii_file_name, 'r') as file:
                        print("i am here")
                        for line in file:
                            self.client_socket.sendall(line.encode())
                except:
                    pass
            case ClientState.DISCONNECTED:
                pass
        self.state = new_state
        
    
    
    def thread_loop(self):
        try:
            while True:
                match self.state:
                    case ClientState.IN_USER_MENU:
                        self.user_menu()
                    case ClientState.IN_CHAT:
                        self.in_chat()
                    case ClientState.DISCONNECTED:
                        break
        except (ConnectionAbortedError, ConnectionResetError):
            pass
        finally:
            # Close the client connection
            self.client_socket.close()
            server.list_clients.pop(self.client_socket)
            server.logging.info(f"Closed connection with {self.client_address}, username: {self.user_name}")
                
        
    
    
    def user_menu(self):
        # Listen for user input to connect to someone
        user_to_connect = self.client_socket.recv(1024).decode().rstrip()
        if user_to_connect not in server.clients:
            print(f"user gave {user_to_connect} server list {server.clients}")
            self.client_socket.sendall("Please pick a user in the list.".encode())
        else:
            self.user_connection = user_to_connect
            self.set_state(ClientState.IN_CHAT)
    
    
    def in_chat(self):
        message = self.client_socket.recv(1024).decode()
        #need to make a function that checks the message for \ and does the appropriate task
        if not message:  # Client has closed the connection
            self.set_state(ClientState.DISCONNECTED)
        # remove client form server
        if message == "\\user_menu":
            self.set_state(ClientState.IN_USER_MENU)
        # message to be sent to the chosen users
        else:
            server.send_to_user(self.user_name, self.user_connection, message)

                    
                   
    