import socket
import threading
import json
import hashlib
import os

#TO DO
#make client logfile
#fix invalid username
#make admin user



# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 12345
RUNNING = True # if true is able to receive messages
clear_right = "\033[K"
prev_line = "\033[F"

        
def start_client():    
    """ Start the client and connect to the server. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # set the timeout
        client_socket.settimeout(5)
        if not try_connection(client_socket):
            return

        #make the thread for accepting connection
        threading.Thread(target=receive_message, args=(client_socket,)).start()

        # loop for accepting input
        while True:
            message = input()
            #this is to make user that the terminal doesn't keep the input line
            print(f"{prev_line}{clear_right}", end='') #goes up one line and clears it then does not make a new line 
            
            
            if message == "\\exit":
                my_exit(client_socket)

            send_message(client_socket, message)



def try_connection(client_socket):
    attempted_to_connect = 0
    # Try catch block for if the connection is refused it will attempt to connect three times
    while True:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            return True
        except ConnectionRefusedError:
            attempted_to_connect += 1
            print(f"Failed connect attempt {attempted_to_connect}")
            if attempted_to_connect == 3:
                print("Cannot connect to server")
                return False



def send_message(client_socket, message):
    # try to send a message will catch for timeout of connection loss
    try:

        client_socket.send(message.encode())

    except TimeoutError:
        print("The server has closed or is taking to long to respond")
        print("Will try to connect again")
        client_socket.detach()
        if not try_connection(client_socket):
            return
    except (ConnectionResetError, ConnectionAbortedError):
        print("Server is no longer available")
        exit(0)


def my_exit(client_socket):
    global RUNNING
    RUNNING = False
    client_socket.send("\exit".encode())
    client_socket.close()
    exit(0)


def receive_message(client_socket):
    while RUNNING:
        try:
            response = client_socket.recv(4024).decode('utf-8', 'ignore')
            print(response)
        except (TimeoutError, TypeError, OSError):
            pass



def make_client_list():
    clients = []
    current_dir = os.path.dirname(os.path.abspath("client.py"))
    
    for filename in os.listdir(current_dir):
        if filename.endswith(".json"):
            filename = os.path.join(current_dir, filename)
            try:
                with open(filename, 'r') as f:
                    data = json.loads(f)
                    clients.append(data["name"])
            except Exception as e:
                print(f"problem please contact Alex {e}")
    return clients

if __name__ == "__main__":
    start_client()
