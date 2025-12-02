import json
import socket
import sys
import threading
import logging
import signal
from enum import Enum
from pathlib import Path
import os
import clienthandler
import clientstartup
import chatcommands

# Set up basic logging configuration
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants for the server configuration
HOST = 'localhost'
PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

###
###     GLOBAL CLIENT VARIABLES -- ACCESS THROUGH GETTER FUNCTIONS
###

_list_clients = dict()
def list_clients(): return _list_clients
_clients = set()
def clients(): return _clients
_dict_commands = dict()
def dict_commands(): return _dict_commands
_disallowed_commands = []
def disallowed_commands(): return _disallowed_commands

###
### STARTUP SCREEN ASCII
###

ascii_night_sky = '''
       + o          .         .._                 . o                     +     
         '  '     '         .' .-'`                   .                 .      
              .            /  /              .                                  
                  * .      |  |                   +    .                +  '    
        o         .    +   \  \       .                     .                   
     _|_      +           o '._'-._                    o  'o                    
      |           +            ```    |                       .                 
       +                            - o -       *                               
    '  o                              |    * '                           +      
  *                       '      +       + o        .         |         o     + 
     . '            .                                  +     -o-     .          
                .            +                                |    .    o       
                            '                           '                       
                            +                      '           o                
        '                              ' .     .                                
                     +                        *       o    .                   
                                         .                              '       
            '   +      .  '       .     o                          .            
          .   *         o+                        +                   +         
                     .  .            '   +         ..           .               
      o             '                             . +.'  o .         '          
'''

###
### -- DATABASE FUNCTIONS
###

# get the user info and put into a dict
def load_user(user):
    # convert the username into ascii numbers
    file = ascii_filename(user, ".json")
    try:
        # open the database file
        with open("database/" + file, "r") as f:
            return json.load(f)
    except:
        return False
    
    
# save a user dict as a json file
def save_user(user_dict):
    #convert the username into ascii numbers
    file = ascii_filename(user_dict["name"], ".json")
    # open the database file
    with open("database/" + file, "w") as f:
        json.dump(user_dict, f)
        

# save the text log of two user's conversation
def write_to_file(user1, user2, write):
    # sort alphabetically
    sort = sorted([user1, user2])
    # get ascii name for file
    file = ascii_filename("".join(sort), ".txt")
    #append to the file or create one
    try:
        # open database file
        with open("database/" + file, "a") as f:
            # write up-to-date conversation, deleting old file
            f.write(write)
            f.close()
    except:
        return False
    

# Get all files in the database folder ending with the provided input
def get_database(require_ending=None):
    PROJECT_ROOT = Path(__file__).resolve().parent
    DATABASE_DIR = PROJECT_ROOT / "database"
    files = []
    for file in os.listdir(DATABASE_DIR):
        if require_ending != None and not file.endswith(require_ending):
            continue
        files.append(os.path.join(DATABASE_DIR, file))
    return files
  
    
# convert a name into its ascii filename, separated by underscores
# 
# Example: John gets converted into 74_111_104_110
def ascii_filename(name, ending=None):
    asciiName = ""
    #put the username into ascii format because of windows file format 
    name = "_".join(name)
    for char in name:
        # add the ord (ascii value) of the character, unless it's an underscore. 
        asciiName += str(ord(char)) if char != "_"else "_"
    if ending != None:
        # if we specified an ending then add it
        # example: ending can be ".json"
        asciiName += ending
    print(f"ASCII Name: {asciiName}")
    return asciiName
    
###
### -- SERVER SENDING FUNCTIONS
###


# Send message to BOTH the sender and receiver
def send_to_user(sender, senderSocket, receiver, message):
    # Append username to message as prefix
    message_send = f"{sender}: {message}"
    # send to the sender, as their message is deleted by the client
    senderSocket.sendall(message_send.encode())
    # Find receiver's client socket in list of clients
    client_socket = next((k for k, v in list_clients().items() if receiver in v), None)
    if client_socket != None:
        # receiver is connected, send to their client
        (_, user, handler) = list_clients().get(client_socket)
        # verify the receiver's handler is currently connected to the sender
        if handler.user_connection == sender:
            # send the message
            client_socket.sendall(message_send.encode())
        
    # log this message into the database
    write_to_file(sender, receiver, (message_send + '\n'))

    
        
# Main server loop. Listens for clients and connects them to a startup process
def start_server():
    make_client_list()
    make_command_list()
    
    # Start the server and listen for incoming connections.
    server_socket.bind((HOST, PORT))
    # allow only 5 connection fails for DDOS protection
    server_socket.listen(5)
    # 1 second timeout
    server_socket.settimeout(1)
    logging.info(f"Server started and listening on {HOST}:{PORT}")
    print(f"Server started and listening on {HOST}:{PORT}")
    while True:
        try:
            # Accept new client connections and start a thread for each client
            client_socket, client_address = server_socket.accept()
            # give client a startup object
            
            # Explanation:
            # ClientStartup is a state machine which has the client log in or make a new account.
            # Later on, it will be given a ClientHandler state machine which allows connecting
            # to other users and messaging.
            client_startup = clientstartup.ClientStartup(client_socket, client_address)
            # Begin ClientStartup main loop on a thread
            threading.Thread(target=client_startup.thread_loop, args=()).start()

        except TimeoutError:
            pass
        
        
# Called by ClientHandler. If valid, hooks user up to a ClientHandler
def connect(client_startup: clientstartup.ClientStartup, new_user: bool):
    try:
        # Get username given
        username = client_startup.user_dict["name"]
        # If this user is new, save them to a new .json file
        if new_user: 
            save_user(client_startup.user_dict)
        
        # Make a new list of clients
        print(f"Clients before add: {clients()}")
        # Reset the client list and command list
        make_client_list()  # This line is a tomato, do not remove
        make_command_list() # This line is a tomato, do not remove
        
        # Add new client to the clients list
        clients().add(username)
        
        # Send the welcome splash art to the user
        client_startup.client_socket.sendall(ascii_night_sky.encode())
        # Send welcome message
        client_startup.client_socket.sendall("You are now connected to the server. Start typing to communicate".encode())
        logging.info(f"Sent welcome art to {client_startup.client_address}, {username}")
        
        # Create our client handler
        client_handler = clienthandler.ClientHandler(client_startup.client_socket, client_startup.client_address, username)
        # Add client to the client dictionary
        list_clients()[client_startup.client_socket] = (client_startup.client_address, username, client_handler) #dict
        
        # Set the state of the ClientStartup such that it removes itself and terminates its thread
        client_startup.set_state(clientstartup.ClientState.REMOVE_SELF)
        
        # Begin the ClientHandler thread
        threading.Thread(target=client_handler.thread_loop, args=()).start()
        
    except Exception as e:
        logging.info(f"Exception connecting ClientStartup as ClientHandler! {e}")

        
      

# close all the clients and shutdown the server
def close_server(signum, frame):
    print("Server shutting down")
    logging.info(f"Server is shutting down on {HOST}:{PORT}")
    # Get all the clients 
    for client in list_clients().keys():
        try:
            # Close client connection forcefully
            client.close()
        except:
            pass
    server_socket.close()
    sys.exit(0)
    
    
###
### INTERNAL LISTS AND DICTS
###
  
def make_client_list():
    # Get all jsons from database
    for file in get_database(".json"):
        try:
            with open(file, 'r') as f:
                # Get all json data
                data = json.load(f)
                # add the name from the file into the list
                clients().add(data["name"])
        except Exception as e:
            pass


def make_command_list():
    # List all disallowed commands 
    # Exception: Admin can always execute these
    disallowed_commands().extend(["show_chat"])
    
    # Add all other commands to list.
    # Structure: Command Word, Command Object
    dict_commands()["colour"] = chatcommands.ColorCommand()
    dict_commands()["show_chat"] = chatcommands.ShowChatCommand()
    
    
if __name__ == '__main__':
    # set handler for the event of ctrl + c or any termination signal, closes the server
    signal.signal(signal.SIGINT, close_server)
    signal.signal(signal.SIGTERM, close_server)
    start_server()


