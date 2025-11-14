import json
import hashlib


def load_user(user):
    asciiUser = ""
    user = "_".join(user)
    for char in user:
        asciiUser += str(ord(char)) if char != "_"else "_"
    try:
        file = asciiUser + ".json"
        with open(file, "r") as f:
            return json.load(f)
    except:
        return False
    
    
def save_user(user, user_dict):
    asciiUser = ""
    user = "_".join(user)
    for char in user:
        asciiUser += str(ord(char)) if char != "_"else "_"
    file = asciiUser + ".json"
    with open(file, "w") as f:
        json.dump(user_dict, f)
        
        
        
def main():
    password = hashlib.sha256("hiJohn".encode()).hexdigest()
    John = {
        "name" : "John",
        "password" : password,
    }
    print(type(John))
    save_user("John", John)
    password = hashlib.sha256("MaryLamb".encode()).hexdigest()
    Mary = {
        "name" : "Mary",
        "password" : password,
    }
    save_user("Mary", Mary)
    print(load_user("Mary"))
    print(load_user("John"))
    password = hashlib.sha256("MaryandJosef".encode()).hexdigest()
    MARY = {
        "name" : "MARY",
        "password" : password,
    }
    save_user("MARY", MARY)
    print(load_user("MARY"))   
    
    password = hashlib.sha256("111".encode()).hexdigest()
    mary = {
        "name" : "mary",
        "password" : password,
    }
    save_user("mary", mary)
    print(load_user("mary"))   
    


if __name__ == "__main__":
    main()
