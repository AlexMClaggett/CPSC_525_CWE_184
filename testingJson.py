import json
import hashlib


def load_user(user):
    asciiUser = ""
    for char in user:
        asciiUser = asciiUser + str(ord(char))
    try:
        file = asciiUser + ".json"
        with open(file, "r") as f:
            return json.load(f)
    except:
        return False
    
    
def save_user(user, user_dict):
    asciiUser = ""
    for char in user:
        asciiUser = asciiUser + str(ord(char))
    file = asciiUser + ".json"
    with open(file, "w") as f:
        json.dump(user_dict, f)
        
        
        
def main():
    password = hashlib.sha256("hiJohn".encode()).hexdigest()
    John = {
        "name" : "John",
        "password" : password,
        "Mary" : False,
        "MARY" : "banned"
    }
    print(type(John))
    save_user("John", John)
    password = hashlib.sha256("MaryLamb".encode()).hexdigest()
    Mary = {
        "name" : "Mary",
        "password" : password,
        "John" : False,
        "MARY" : False
    }
    save_user("Mary", Mary)
    print(load_user("Mary"))
    print(load_user("John"))
    password = hashlib.sha256("MaryandJosef".encode()).hexdigest()
    MARY = {
        "name" : "MARY",
        "password" : password,
        "John" : "banned",
        "Mary" : False
    }
    save_user("MARY", MARY)
    print(load_user("MARY"))   
    


if __name__ == "__main__":
    main()
