CWE 184 Incomplete list of Disallowed Inputs 


To run the program (please run the program on the csxlinux server that are of the same number):
1. Run the server.py file in an terminal
2. Start up a new terminal and run the client.py (please do not pick Bob he is the exploit user)
   - Some sample users are: in the format of (user, password), (John, hiJohn), (Mary, MaryLamb), (Ed, hi)
4. For more clients you must add more terminals
5. To see the expliot run attackscript.py user1 user2 (where user1 and user2 are user that you wish to see the chat logs of)

You can interact with the server through the client's terminals. 
The only interaction that you can make on the server's terminal is to do ctrl c to gracefully shutdown the server.

The vulnerability is located in the clienthandler.py file from line 181 to line 215. 
The attack script requires two arguments of the users that you wish to receive the chat log of.
I recommend using John and Joe as they have a chat to display. If you type two users that do not have a chat history,
then there will be a message informing you of such. 
If you type a user that is not in the active database, it should print "No chat to display"

Note: The attack script outputs the entirety of the self-conversation on the server (In this case, Bob's entire conversation with himself.)
This means that the exploited command's output will always be at the bottom of the script's output, but it will also include any previous messages
Bob has sent to himself. This includes the output from previous uses of the attack script.

-- Exploit Explanation --
There is a protection preventing any user other than Admin from running certain commands. The commands disallowed to be used by common users are stored in a list, and if a user tries to use one, then their command is checked against that list and they are returned with an error message in their chat. However, it is only after that permission check that the command is parsed to only allow ASCII characters, so sending in a non-ASCII character in with the command will bypass the check against the list, and therefore allow anyone to execute the command. 
For example, the command show_char(user1, user2) is typically disallowed as "show_chat" is a member of the disallowed commands list. However, by typing show_chat很(user1, user2), the command is not recognized as a disallowed input, however when the ASCII parser removes the 很 character, it still executes properly regardless of user type. The danger of this exploit lies in the fact that certain admin commands allow users to access sensitive information, such as any two users' chat logs, which you wouldn't want anyone other than an admin to do.

-- Known Problems --
As a warning, during busy times on cslinux the server sometimes fails to close when the terminal is closed. 
To fix this, simply wait a little bit for the cslinux server to catch up and then it should run again.

Furthermore, as this currently only supports a local network, the server and client need to be running on the same server
(For example, they both must be on csx1)
