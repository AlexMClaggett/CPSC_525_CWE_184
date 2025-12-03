import json
import socket
import sys
import threading
import logging
import signal
import hashlib
from enum import Enum
import server
import re


# State for the State machine
class ClientState(Enum):
    IN_USER_MENU = 0
    IN_CHAT = 1
    DISCONNECTED = 2


###
### ClientHandler Class
### Contains state machine to connect users to each other for communication
###


class ClientHandler:
    def __init__(self, socket, addr, user_name):
        # Var init
        self.client_socket = socket
        self.state = ClientState(0)
        self.client_address = addr
        self.user_name = user_name
        self.user_connection = None
        # start in user menu
        self.set_state(ClientState.IN_USER_MENU)
        server.logging.info(f"Connection from {self.client_address}")
    
    
    
    ### 
    ### State Machine
    ###
    
    # this is only done once per state change
    def set_state(self, new_state):
        # do changes as needed
        match new_state:
            # menu for selecting the client you wish to talk to
            case ClientState.IN_USER_MENU:
                # send an menu to the client
                message = """
                - To exit type \\exit
                - To pick new user type \\new user
                Please type the name of the person you want to talk to:
                """
                self.client_socket.sendall(message.encode())
                client_list_print = ""
                i = 0
                print(f"Clients at time: {server.clients()}")
                # send the list of users to the client
                for item in server.clients():
                    client_list_print += "\t" + item
                    if i % 2 == 0: client_list_print += "\n"
                    i += 1
                self.client_socket.sendall(client_list_print.encode())
            # 
            case ClientState.IN_CHAT:
                # get the txt file of the prev conversion if there is one
                sort = sorted([self.user_name, self.user_connection])
                file = server.ascii_filename("".join(sort), ".txt")
                message = """
                - Type \\colour("wanted text colour") to change the colour of following text
                """
                self.client_socket.sendall(message.encode())
                # print the content of the prev conversion if there is one
                try:
                    with open("database/" + file, 'r') as f:
                        for line in f:
                            self.client_socket.sendall(line[:-1].encode())
                except:
                    pass
            case ClientState.DISCONNECTED:
                pass
            
        self.state = new_state
        
    
    # this loops the function until a new state is picked
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
        # Check to see if the client wants to exit or new user
        user_to_connect = self.client_socket.recv(1024).decode().rstrip().lower()
        # if the client types exit gracefully disconnect
        if user_to_connect == "\\exit":
            self.set_state(ClientState.DISCONNECTED)
        # if the client types new user let them pick a new user
        if user_to_connect == "\\new user":
            self.set_state(ClientState.IN_USER_MENU)
        # if nothing matches a username ask for another input
        if user_to_connect not in server.clients():
            print(f"user gave {user_to_connect} server list {server.clients()}")
            self.client_socket.sendall("Please pick a user in the list.".encode())
        else:
            # connect the client to the username they picked
            self.user_connection = user_to_connect
            self.set_state(ClientState.IN_CHAT)
    
    # 
    def in_chat(self):
        message = self.client_socket.recv(1024).decode()
        # if there is a blank message return so that input is listened for again
        if message == "":
            return
        # check the message for \commands
        message = self.parse_message(message)
        # check for exit and new user commands
        check_state = message.lower()
        if check_state == "\\exit":
            self.set_state(ClientState.DISCONNECTED)
        if check_state == "\\new user":
            self.set_state(ClientState.IN_USER_MENU)
        if not message:  # Client has closed the connection
            self.set_state(ClientState.DISCONNECTED)
        # message to be sent to the chosen users
        else:
            server.send_to_user(self.user_name, self.client_socket, self.user_connection, message)
            
    # check the user message for commands
    def parse_message(self, message):
        current_string = ""
        next = False
        # split the message by spaces and slashes to read the commands
        list_message = re.split(r'( |\\)', message)
        # go through the list and if there is a \ then the next index will be a command
        for part in list_message:
            if next:
                # this is a command that the client has asked to do
                command = ""
                args = []
                
                count_open_bracket = part.count('(')
                count_close_bracket = part.count(')')
                
                # find the arg inside the brackets
                if count_open_bracket == 1 and count_close_bracket == 1:
                    command = part.split('(')[0]
                    #split the args using the , 
                    for arg in part.split('(')[1].split(')')[0].rstrip().split(','):
                        args.append(arg)
                    print(f"command: {command}, args: {args}")
                    pass
                # else will always run after the args are found
                else:
                    command = part
                
                ###
                ### CWE 184 Vulnerability
                ###
                # the clienthandler will first check to see if the command given is in the list of disallowed commands
                # if is is the case it will stop executing the command
                
                if command in server.disallowed_commands() and self.user_name != "Admin":
                    self.client_socket.sendall("Admin: Sorry, you do not have permissions to execute that command.".encode())
                    break
                
                # However the clienthandler then removes all not ascii characters from the command 
                # and finds the matching command in the list of server commands.
                # This makes the previous list incomplete because it will check the exact string against the ones not allowed,
                # which this not ascii char will cause it to pass.
                # But when it check against all the commands the server has available it will run the disallowed command
                
                # Example:
                #Not Admin client: show_chat(user1,user2) doesn't pass the list of disallowed inputs
                #Not Admin client: show_chat愛(user1,user2) does pass the list of disallowed inputs and will run the show_chat command 
                encoded = command.encode('utf-8')
                decoded = encoded.decode('ascii', 'ignore')

                # run the command found with the args given if the command exist
                if decoded in server.dict_commands().keys():
                    cmd_obj = server.dict_commands()[decoded]
                    if cmd_obj != None:
                        returned = cmd_obj.execute(current_string, args)  
                        if (returned != None):
                            # add the string to the return string
                            current_string += returned  
                else:
                    self.client_socket.sendall(f"Admin: Sorry, the \\{decoded} command does not exist.".encode())
                ###   
                next = False
            # set the bool that the next index will be a command
            elif '\\' in part:
                next = True
                pass
            # add the string to the return string
            else:
                current_string += part
        return current_string + "\033[0m"
    
    # returns true if a command is found in the list of server dict keys
    def commands_in_string(self, string):
        print(f"Finding keys {server.dict_commands.keys()} in string {string}")
        return [w for w in server.dict_commands.keys() if w in string]
    
    