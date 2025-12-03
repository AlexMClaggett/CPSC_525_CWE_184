import ansi
import server

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
            return None
        
        
#class AddText 