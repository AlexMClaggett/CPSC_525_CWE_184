import ansi
import server
import os



## User commands
class ColorCommand:
    def __init__(self):
        pass
    
    # function that puts the ansi colour code into the client message
    def execute(self, message: str, list_args: list):
        if len(list_args) != 1:
            return None
        match list_args[0].lower():
            case "red":
                return ansi.ANSI.RED
            case "light_red":
                return ansi.ANSI.LIGHT_RED
            case "blue":
                return ansi.ANSI.BLUE
            case "light_blue":
                return ansi.ANSI.LIGHT_RED
            case "green":
                return ansi.ANSI.GREEN
            case "light_green":
                return ansi.ANSI.LIGHT_GREEN
            case "brown":
                return ansi.ANSI.BROWN
            case "cyan":
                return ansi.ANSI.CYAN
            case "light_cyan":
                return ansi.ANSI.LIGHT_CYAN
            case "purple":
                return ansi.ANSI.PURPLE
            case "light_purple":
                return ansi.ANSI.LIGHT_PURPLE
            case "gray":
                return ansi.ANSI.DARK_GRAY
            case "light_gray":
                return ansi.ANSI.LIGHT_GRAY
            case "yellow":
                return ansi.ANSI.YELLOW
            case "white":
                return ansi.ANSI.LIGHT_WHITE
        return ansi.ANSI.END


        
class TextModCommand():
    def __init__(self):
        pass
    
    # function that puts the text modifier code into the client message
    def execute(self, message: str, list_args: list):
        if len(list_args) != 1:
            return None
        match list_args[0].lower():
            case "bold":
                return ansi.ANSI.BOLD
            case "italic":
                return ansi.ANSI.ITALIC
            case "underline":
                return ansi.ANSI.UNDERLINE
            case "negative":
                return ansi.ANSI.NEGATIVE
            case "crossed":
                return ansi.ANSI.CROSSED
        return ansi.ANSI.END
    
    
### Admin Commands
class DeleteUserCommand():
    def __init__(self):
        pass
    
    # deletes a user
    def execute(self, message: str, list_args: list):
        
        # check that there is a user given
        if len(list_args) != 1:
            return None
        #convert the username into ascii numbers
        file = server.ascii_filename(list_args[0], ".json")
        # delete the user json file
        try:
            os.remove("database/" + file)
            #remake the client list after the deletion 
            server.make_client_list()
        except FileNotFoundError:
            return f"Error: File '{"database/" + file}' not found."
        except Exception as e:
            return f"An error occurred: {e}"
        server.make_client_list()
        # delete all the text file associated with that user
        for user in server.clients():
            sort = sorted([list_args[0], user])
            file = server.ascii_filename("".join(sort), ".txt")
            try:
                os.remove("database/" + file)
            except FileNotFoundError:
                continue
            except Exception as e:
                return f"An error occurred: {e}"
         
        return "Files deleted successfully"
            
            
        
        
        
        

class ShowChatCommand:
    def __init__(self):
        pass
    
    # prints the two users messages if there is a txt file
    def execute(self, message: str, list_args: list):
        # check that there is two users
        if len(list_args) != 2:
            return None
        # finds the txt file name and then looks to see if there is a file
        sort = sorted([list_args[0], list_args[1]])
        file = server.ascii_filename("".join(sort), ".txt")
        try:
            with open("database/" + file, 'r') as f:
                chat = ""
                for line in f:
                    chat += line
                return chat
        except:
            return "Server: No chat to display"
        