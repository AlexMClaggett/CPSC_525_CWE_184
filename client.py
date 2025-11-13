import socket
import threading
import json
import hashlib


#TO DO
#make client logfile
#fix invalid username
#fix spelling mistakes



# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 12345
RUNNING = True # if true is able to receive messages
clear_right = "\033[K"
prev_line = "\033[F"
clients = ["John", "Mary", "MARY", "Admin"]
invalidUsername = ["", " "]

# get the user info and put into a dict
def load_user(user):
    asciiUser = ""
    #put the username into ascii format because of windows file format 
    for char in user:
        asciiUser = asciiUser + str(ord(char))
    try:
        file = asciiUser + ".json"
        with open(file, "r") as f:
            return json.load(f)
    except:
        return False
    
# save a user dict as a json file
def save_user(user, user_dict):
    asciiUser = []
    #put the username into ascii format because of windows file format 
    for char in user:
        asciiUser.append(ord(char))
    file = user + ".json"
    with open(file, "w") as f:
        json.dump(user_dict, f)
        
     

def start_client():
    """ Start the client and connect to the server. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    
        global clients
        # set the timeout
        client_socket.settimeout(5)

        #Print the options
        print( '''
Would you like to login in or make and account?
    For login type: Login
    To create an account type: New
    To exit type: \exit
            ''')
        
        
        option = input().lower().rstrip()
        if option == "\exit":
            exit(0)
            
        if option == "login":
            passwordAttempts = 0
            tryAgain = 'y'
            # allow 3 attempt or allow the user to exit
            while passwordAttempts < 3 or tryAgain == 'n':
                username = input("Please give user name: ")
                password = input("Please give password: ")
                user_dict = load_user(username)
                #check for the username and compare the passwords, for security don't tell the user which is incorrect
                if user_dict != False and user_dict["password"] == hashlib.sha256(password.encode()).hexdigest():
                    if username not in clients:
                        clients = clients.append(client)
                    connect(username, client_socket)
                else:
                    #ask the user if they would like to try again or if they whish to exit the program
                    passwordAttempts += 1
                    tryAgainInput = input("Username or Password was incorrect. Would you like to try again Y/N: ").lower().rstrip()
                    if tryAgainInput in ['y', 'yes']:
                        continue
                    else:
                        tryAgain = 'n'
                        exit(0)
            #will exit at the bottom
            print("Too many attempts")
        elif option == "new":
            username = ""
            userContinue = False
            # get user name
            while not userContinue:
                username = input("What would you like your username to be: ")
                #invalidUsername needs to be fixed
                global invalidUsername
                #check that the inputted user is not already in use and it is not an empty string
                if username in clients or username in invalidUsername:
                    print("Sorry that username is taken. Please given a different username:")
                else:
                    check = input(f"Are you sure you would like this {username} username Y/N").lower().rstrip()
                    if check == 'n':
                        print("Please give another.")
                    else:
                        userContinue = True
            #get password
            userContinue = False
            user_dict = dict()
            while not userContinue:
                password = input("Please type in wanted password: ")
                password2 = input("Please type in password again: ")
                if password != password2:
                    print("Passwords do not match please try again.")
                else:
                    #make the user dict and insert thier name into the list of known users
                    user_dict["name"] = username
                    user_dict["password"] = hashlib.sha256(password.encode()).hexdigest()
                    for client in clients:
                        user_dict[client] = False
                    clients = clients.append(username)
                    userContinue = True
            #make the json file and connect the new user to the server 
            save_user(username, user_dict)
            connect(username, client_socket)           
        exit(0)


def connect(user_name, client_socket):
    
    if not try_connection(client_socket):
        return

    # first message is username to the server
    send_message(client_socket, user_name)

    #make the thread for accepting connection
    threading.Thread(target=recieve_message, args=(client_socket,)).start()


    # loop for accepting input
    while True:
        message = input()
        #this is to make user that the terminal doesn't keep the input line
        print(f"{prev_line}{clear_right}", end='') #goes up one line and clears it then does not make a new line 
        if message == "\exit":
            my_exit(client_socket, user_name)

        send_message(client_socket, message)
        print(f"{user_name}: {message}")





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


def my_exit(client_socket, user_name):
    global RUNNING
    RUNNING = False
    client_socket.send("\exit".encode())
    client_socket.close()
    exit(0)


def recieve_message(client_socket):
    while RUNNING:
        try:
            response = client_socket.recv(4024).decode('utf-8', 'ignore')
            print(response)
        except (TimeoutError, TypeError, OSError):
            pass


if __name__ == "__main__":
    start_client()
