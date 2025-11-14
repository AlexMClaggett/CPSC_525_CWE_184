import json
import socket
import sys
import threading
import logging
import signal
import hashlib
from enum import Enum
import clienthandler

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
clients = ["John", "Mary", "MARY"]

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


def load_user(user):
    try:
        file = user + ".json"
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user(user, user_dict):
    file = user + ".json"
    with open(file, "w") as f:
        json.dump(user_dict, f)


def write_to_file(user1, user2, write):
    sort = sorted([user1, user2])
    file_name = "".join(sort)
    ascii_file_name = ""
    #put the filename into ascii format because of windows file format 
    file_name = "_".join(file_name)
    for char in file_name:
        ascii_file_name += str(ord(char)) if char != "_"else "_"
    #append to the file or create one
    try:
        file = ascii_file_name + ".txt"
        with open(file, "a") as f:
            f.write(write)
    except:
        return False
    
    
def send_to_user(sender, receiver, message):
    message_send = f"{sender}: {message}\n"
    client_socket = next((k for k, v in list_clients.items() if receiver in v), None)
    if client_socket != None:
        (_, user, handler) = list_clients.get(client_socket)
        if handler.user_connection == sender:
            client_socket.sendall(message_send.encode())
        write_to_file(sender, receiver, message_send)
    else:
        write_to_file(sender, receiver, message_send)
        


def start_server():
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
            user_name = client_socket.recv(1024).decode()
            global clients
            if not user_name in clients:
                clients.append(user_name)
            client_socket.sendall(ascii_night_sky.encode())
            client_socket.sendall("You are now connected to the server. Start typing to communicate".encode())
            logging.info(f"Sent welcome art to {client_address}, {user_name}")
            client_handler = clienthandler.ClientHandler(client_socket, client_address, user_name)
            list_clients[client_socket] = (client_address, user_name, client_handler) #dict
            threading.Thread(target=client_handler.thread_loop, args=()).start()
        except TimeoutError:
            pass
      

# close all the clients and shutdown the server
def close_server(signum, frame):
    print("Server shutting down")
    logging.info(f"Server is shutting down on {HOST}:{PORT}")
    for client in list_clients.keys():
        client.close()
    server_socket.close()
    sys.exit(0)


if __name__ == '__main__':
    # set handler for the event of ctrl + c or any termination signal, closes the server
    signal.signal(signal.SIGINT, close_server)
    signal.signal(signal.SIGTERM, close_server)
    start_server()


