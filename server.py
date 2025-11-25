import json
import socket
import sys
import threading
import logging
import signal
import hashlib
from enum import Enum
from pathlib import Path
import os
import clienthandler
import clientstartup

#TO DO
#make direct messaging
#make client messages be able to have colour, underline, bold ...
#set up admin commands


# Set up basic logging configuration
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants for the server configuration
HOST = 'localhost'
PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
list_clients = dict()
_clients = set()
def clients(): return _clients
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


# get the user info and put into a dict
def load_user(user):
    file = ascii_filename(user, ".json")
    try:
        with open("database/" + file, "r") as f:
            return json.load(f)
    except:
        return False
    
    
# save a user dict as a json file
def save_user(user_dict):
    file = ascii_filename(user_dict["name"], ".json")
    with open("database/" + file, "w") as f:
        json.dump(user_dict, f)
        


def write_to_file(user1, user2, write):
    sort = sorted([user1, user2])
    file = ascii_filename("".join(sort), ".txt")
    #append to the file or create one
    try:
        with open("database/" + file, "a") as f:
            f.write(write)
    except:
        return False
    
    
def send_to_user(sender, senderSocket, receiver, message):
    message_send = f"{sender}: {message}"
    senderSocket.sendall(message_send.encode())
    client_socket = next((k for k, v in list_clients.items() if receiver in v), None)
    if client_socket != None:
        (_, user, handler) = list_clients.get(client_socket)
        if handler.user_connection == sender:
            client_socket.sendall(message_send.encode())
        write_to_file(sender, receiver, (message_send))
    else:
        write_to_file(sender, receiver, (message_send))


def get_database(require_ending=None):
    PROJECT_ROOT = Path(__file__).resolve().parent
    DATABASE_DIR = PROJECT_ROOT / "database"
    files = []
    for file in os.listdir(DATABASE_DIR):
        if require_ending != None and not file.endswith(require_ending):
            continue
        files.append(os.path.join(DATABASE_DIR, file))
    return files
    
    
def ascii_filename(name, ending=None):
    asciiName = ""
    #put the username into ascii format because of windows file format 
    name = "_".join(name)
    for char in name:
        asciiName += str(ord(char)) if char != "_"else "_"
    if ending != None:
        asciiName += ending
    print(f"ASCII Name: {asciiName}")
    return asciiName
        

def start_server():
    #make client list
    make_client_list()
    #print(f"initial clients: {clients()}")
    
    """ Start the server and listen for incoming connections. """
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.settimeout(1)
    logging.info(f"Server started and listening on {HOST}:{PORT}")
    print(f"Server started and listening on {HOST}:{PORT}")
    while True:
        try:
            # Accept new client connections and start a thread for each client
            client_socket, client_address = server_socket.accept()
            client_startup = clientstartup.ClientStartup(client_socket, client_address)
            threading.Thread(target=client_startup.thread_loop, args=()).start()

        except TimeoutError:
            pass
        
        
def connect(client_startup: clientstartup.ClientStartup, new_user: bool):
    try:
        username = client_startup.user_dict["name"]
        if new_user: save_user(client_startup.user_dict)
        print(f"Clients before add: {clients()}")
        make_client_list()  # This line is a tomato. DO NOT REMOVE!!
        clients().add(username)
        client_startup.client_socket.sendall(ascii_night_sky.encode())
        client_startup.client_socket.sendall("You are now connected to the server. Start typing to communicate".encode())
        logging.info(f"Sent welcome art to {client_startup.client_address}, {username}")
        
        # Create our client handler
        client_handler = clienthandler.ClientHandler(client_startup.client_socket, client_startup.client_address, username)
        list_clients[client_startup.client_socket] = (client_startup.client_address, username, client_handler) #dict
        
        client_startup.set_state(clientstartup.ClientState.REMOVE_SELF)
        
        threading.Thread(target=client_handler.thread_loop, args=()).start()
        
    except Exception as e:
        logging.info(f"Exception connecting ClientStartup as ClientHandler! {e}")

        
      

# close all the clients and shutdown the server
def close_server(signum, frame):
    print("Server shutting down")
    logging.info(f"Server is shutting down on {HOST}:{PORT}")
    for client in list_clients.keys():
        client.close()
    server_socket.close()
    sys.exit(0)
    
    
  
def make_client_list():
    for file in get_database(".json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                clients().add(data["name"])
        except Exception as e:
            print(f"problem please contact Alex {e}")


if __name__ == '__main__':
    # set handler for the event of ctrl + c or any termination signal, closes the server
    signal.signal(signal.SIGINT, close_server)
    signal.signal(signal.SIGTERM, close_server)
    start_server()


