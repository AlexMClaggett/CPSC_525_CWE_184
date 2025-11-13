import json
import socket
import sys
import threading
import logging
import signal
import hashlib
#from emoji import emojize
import random
from collections import Counter
import math

# Set up basic logging configuration
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants for the server configuration
HOST = 'localhost'
PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
list_clients = dict()



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

def handle_client(client_socket):
    """ Handle incoming client requests. """
    (client_address, user_name) = list_clients.get(client_socket)
    logging.info(f"Connection from {client_address}")

    try:
        while True:
            # Receive data from the client
            message = client_socket.recv(1024).decode()
            if not message:  # Client has closed the connection
                break
            # remove client form server
            if message == "\leaves":
                break
            # message to be sent to the other users
            else:
                message = f"{user_name}: {message}"
                logging.info(f"Received message: {message} from {user_name}")

                # Message is sent to all other users
                for client_socket_send in list_clients.keys():
                    if client_socket_send != client_socket:
                        client_socket_send.sendall(message.encode())
                        (add, user) = list_clients.get(client_socket_send)
                        logging.info(f"Sent {message} to {user}")
                    else:
                        #client_socket.sendall(message.encode())
                        print("debugging")
    except (ConnectionAbortedError, ConnectionResetError):
        pass
    finally:
        # Close the client connection
        client_socket.close()
        (client_address, user_name) = list_clients.get(client_socket)
        list_clients.pop(client_socket)
        logging.info(f"Closed connection with {client_address}, username: {user_name}")



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
            client_socket.sendall(ascii_night_sky.encode())
            client_socket.sendall("You are now connected to the server. Start typing to communicate".encode())
            logging.info(f"Sent welcome art to {client_address}, {user_name}")
            list_clients[client_socket] = (client_address, user_name)
            threading.Thread(target=handle_client, args=(client_socket,)).start()
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

