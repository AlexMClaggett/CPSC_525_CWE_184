import hashlib
from enum import Enum
import server


# State for the state machine
class ClientState(Enum):
    STARTUP = 0
    NEW_USER = 1
    LOGGING_IN = 2
    CONNECT_AS_NEW = 3
    CONNECT_AS_EXISTING = 4
    REMOVE_SELF = 5
    DISCONNECTED = 6


###
### ClientStartup Class
### Contains state machine which guides user through login
###

class ClientStartup:
    def __init__(self, socket, addr):
        # Var init
        self.client_socket = socket
        self.state = ClientState(0)
        self.client_address = addr
        self.set_state(ClientState.STARTUP)
        # Disallow blank and Admin usernames
        self.invalid_usernames = ["", "Admin"]
        
        self.user_dict = dict()

    
    
    ### 
    ### State Machine
    ###
    
    #  this is only done once per state change
    def set_state(self, new_state):
        # do changes as needed
        match new_state:
            case ClientState.STARTUP:
                # Send welcome message
                message =  '''
Would you like to login in or make and account?
    For login type: Login
    To create an account type: New
    To exit type: \\exit
'''
                self.client_socket.sendall(message.encode())
            case ClientState.NEW_USER:
                # User has chosen to make a new user
                self.client_socket.sendall("What would you like your username to be: ".encode())
            case ClientState.LOGGING_IN:
                # User has chosen to login has an exiting client
                pass
            case ClientState.CONNECT_AS_NEW:
                # User has successfully entered username and password connecting to the server
                print("Connect As New State set")
                server.connect(self, True)
            case ClientState.CONNECT_AS_EXISTING:
                # User has successfully made a new user and is connecting to the server
                server.connect(self, False)
            case ClientState.REMOVE_SELF:
                # Remove the ClientState 
                pass
            case ClientState.DISCONNECTED:
                # User wants to disconnect 
                pass
        self.state = new_state
        
    
    # this loops the function until a new state is picked
    def thread_loop(self):
        try:
            while True:
                match self.state:
                    case ClientState.STARTUP:
                        self.startup()
                    case ClientState.NEW_USER:
                        self.new_user()
                    case ClientState.LOGGING_IN:
                        self.logging_in()
                    case ClientState.REMOVE_SELF:
                        break
                    case ClientState.DISCONNECTED:
                        break
        except (ConnectionAbortedError, ConnectionResetError):
            pass
        finally:
            # Close the client connection
            if self.state != ClientState.REMOVE_SELF:
                self.client_socket.close()
                server.list_clients.pop(self.client_socket)
                server.logging.info(f"Closed connection with {self.client_address}")
                
    
    # user choses if they want to exit, make a new account or sign in.
    def startup(self):        
        option = self.client_socket.recv(1024).decode().rstrip().lower()
        # take the user input strip and make it lower case to compare 
        if option == "\\exit":
            # start the disconnect process
            self.set_state(ClientState.DISCONNECTED)
        elif option == "new":
            # start the logging process for the new users
            self.set_state(ClientState.NEW_USER)
        elif option == "login":
            # start the logging process for already established users
            self.set_state(ClientState.LOGGING_IN)
        else:
            # the user's input didn't match ask for the user to try again
            self.client_socket.sendall("Please chose '\\'exit, new or login.".encode())
            self.set_state(ClientState.STARTUP)
    
    # allow the user to select and username and password 
    def new_user(self):
        # Get Username
        print("Begin new user")
        new_username = ""
        while True:
            try:
                new_username = self.client_socket.recv(1024).decode().rstrip()
                # get the inputted username check that it is not already taken or if it isn't allowed
                if new_username in self.invalid_usernames or new_username in server.clients():
                    self.client_socket.sendall("Sorry that username is taken. Please given a different username:".encode())
                self.client_socket.sendall(f"Are you sure you would your username to be {new_username}? Y/N".encode())
                check = self.client_socket.recv(1024).decode().rstrip().lower()
                # ask the user if they want that user name
                if check != 'y':
                    self.client_socket.sendall("Please give another.".encode())
                    # if not 'y' ask for another username
                else: break
            except TimeoutError:
                self.set_state(ClientState.DISCONNECTED)
            
        # Get Password
        new_password = ""
        while True:
            try:
                # ask for the password twice and make sure that the two passwords match otherwise ask for another password
                self.client_socket.sendall("Please type in password:".encode())
                new_password = hashlib.sha256(self.client_socket.recv(1024).decode().rstrip().encode()).hexdigest()
                self.client_socket.sendall("Please re-type in password:".encode())
                new_password_2 = hashlib.sha256(self.client_socket.recv(1024).decode().rstrip().encode()).hexdigest()
                if new_password != new_password_2:
                    self.client_socket.sendall("Passwords do not match. Please try again.".encode())
                else: break
            except TimeoutError:
                self.set_state(ClientState.DISCONNECTED)
        # put the new user into the dict to be made into a json file later
        self.user_dict["name"] = new_username
        self.user_dict["password"] = new_password
        # connect to the server has a new client
        self.set_state(ClientState.CONNECT_AS_NEW)  
            
            
    
    def logging_in(self):
        # Get Username
        username = ""
        password = ""
        while True:
            try:
                # get the username and password
                self.client_socket.sendall("Enter Username: ".encode())
                username = self.client_socket.recv(1024).decode().rstrip()
                self.client_socket.sendall("Enter Password: ".encode())
                password = self.client_socket.recv(1024).decode().rstrip()
                # get the user from the .json file  
                user = server.load_user(username)
                if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
                    # if the username or password is wrong ask them to try again
                    self.client_socket.sendall("Incorrect Username or Password. Would you like to try again? Y/N".encode())
                    check = self.client_socket.recv(1024).decode().rstrip().lower()
                    # if the user doesn't want to login anymore let them next
                    if check != 'y':
                        self.set_state(ClientState.STARTUP)
                        return   
                else: break
            except TimeoutError:
                self.set_state(ClientState.DISCONNECTED)
        # set the username for the server to use
        self.user_dict["name"] = username
        self.user_dict["password"] = hashlib.sha256(password.encode()).hexdigest()
        # connect to the server 
        self.set_state(ClientState.CONNECT_AS_EXISTING)

                    
                   
    