import sqlite3
import hashlib
import os


# erstellen eines Tables
def create_usertable():
    cur.execute("""CREATE TABLE "users" (
        "username"	TEXT UNIQUE,
        "name"	TEXT,
        "password"	TEXT,
        PRIMARY KEY("username")
        )
    """)


# hinzufügen eines Benutzers
def adduser(username, name, pw):
    """
    :param username: username des users
    :param name: name des users
    :param pw: passwort des users (klartext)
    :return: True wenn user erstellt wurde; False wenn user schon existiert
    """
    hashed_pw = hashlib.sha256(pw.encode(), usedforsecurity=True).hexdigest()
    try:
        cur.execute(f"INSERT INTO users VALUES ('{username}', '{name}', '{hashed_pw}')")
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# fetch hashed Passwort eines Users
def get_pw(username):
    res = cur.execute(f"SELECT password FROM users where username == '{username}'")
    data = res.fetchall()
    # wenn data <= 0 -> kein user mit dem usernamen existiert
    if len(data) <= 0:
        return None
    # ansonsten wird das pw zurückgegeben
    return data[0][0]


# checkt ob ein passwort stimmt
def check_pw(username, clear_pw):
    # fetcht gehashtes pw mit username
    hash_pw = get_pw(username)
    # checkt ob das eingegebenen pw (clear_pw) mit dem pw aus der Datenbank übereinstimmt
    if hashlib.sha256(clear_pw.encode(), usedforsecurity=True).hexdigest() == hash_pw:
        return True
    return False



if os.path.exists("./static/user.db"):
    # wenn die db datei existiert wird nur der cursor erstellt
    con = sqlite3.connect("./static/user.db", check_same_thread=False)
    cur = con.cursor()
else:
    # wenn die datei nicht existiert wird der cursor erstellt und der Table initialisiert
    con = sqlite3.connect("./static/user.db", check_same_thread=False)
    cur = con.cursor()
    create_usertable()


if __name__ == '__main__':
    print("Login")
    username = input("Username: ")
    pw = input("Password: ")

    print(check_pw(username, pw))

