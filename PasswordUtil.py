import bcrypt
import json

def CreatePassword(password):
    salt = bcrypt.gensalt(rounds=6)
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    with open('passwd_store.json', 'w') as f:
        json.dump(hashed_password.decode(), f)


def CheckPassword(password):
    f = open('passwd_store.json', 'r')
    hashed_password = json.load(f)

    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
        print("Password is correct")
    else:
        print("Password is incorrect")
   
