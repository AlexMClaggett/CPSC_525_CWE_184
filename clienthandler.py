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
                self.client_socket.sendall("If you wish to disconnect type \exit if you wish to pick a new user type '\\'new User".encode())
                self.client_socket.sendall("Please type the name of the person you wish to talk to:".encode())
                client_list_print = ""
                i = 0
                print(f"Clients at time: {server.clients()}")
                for item in server.clients():
                    client_list_print += "\t" + item
                    if i % 2 == 0: client_list_print += "\n"
                    i += 1
                self.client_socket.sendall(client_list_print.encode())
            case ClientState.IN_CHAT:
                sort = sorted([self.user_name, self.user_connection])
                file = server.ascii_filename("".join(sort), ".txt")
                try:
                    with open("database/" + file, 'r') as f:
                        print("i am here")
                        for line in f:
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
        #Listen for an exit first
        user_to_connect = self.client_socket.recv(1024).decode().rstrip()
        if user_to_connect == "\\exit":
            self.set_state(ClientState.DISCONNECTED)
        if user_to_connect == "\\new user":
            self.set_state(ClientState.IN_USER_MENU)
        # Listen for user input to connect to someone
        if user_to_connect not in server.clients():
            print(f"user gave {user_to_connect} server list {server.clients()}")
            self.client_socket.sendall("Please pick a user in the list.".encode())
        else:
            self.user_connection = user_to_connect
            self.set_state(ClientState.IN_CHAT)
    
    
    def in_chat(self):
        message = self.client_socket.recv(1024).decode()
        check_state = message.lower()
        if check_state == "\\exit":
            self.set_state(ClientState.DISCONNECTED)
        if check_state == "\\new user":
            self.set_state(ClientState.IN_USER_MENU)
        #need to make a function that checks the message for \ and does the appropriate task
        if not message:  # Client has closed the connection
            self.set_state(ClientState.DISCONNECTED)
        # message to be sent to the chosen users
        else:
            server.send_to_user(self.user_name, self.client_socket, self.user_connection, message)

                    
                   
    