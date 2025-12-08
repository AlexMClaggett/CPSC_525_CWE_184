CWE 184 Incomplete list of Disallowed Inputs 


To run the program:
1. Run the server.py file in an terminal
2. Start up a new terminal and run the client.py
3. For more clients you must add more terminals

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

-- Known Problems --
As a warning, during busy times on cslinux the server sometimes fails to close when the terminal is closed. 
To fix this, simply wait a little bit for the cslinux server to catch up and then it should run again.

Furthermore, as this currently only supports a local network, the server and client need to be running on the same server
(For example, they both must be on csx1)
