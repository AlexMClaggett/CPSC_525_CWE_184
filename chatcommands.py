import ansi
import server

class ColorCommand:
    def __init__(self):
        pass
    
    def execute(self, message: str, list_args: list):
        if len(list_args) != 1:
            return None
        match list_args[0]:
            case "red":
                return ansi.ANSI.RED
            case "blue":
                return ansi.ANSI.BLUE
        return ansi.ANSI.END


class ShowChatCommand:
    def __init__(self):
        pass
    
    def execute(self, message: str, list_args: list):
        if len(list_args) != 2:
            return None
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
        