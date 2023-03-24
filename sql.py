import sqlite3
import hashlib

con = sqlite3.connect("./static/user.db", check_same_thread=False)

cur = con.cursor()


def create_usertable():
    cur.execute("CREATE TABLE users(username, name, password)")


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


def check_user():
    res = cur.execute("SELECT * FROM users")
    print(res.fetchall())


def get_pw(username):
    res = cur.execute(f"SELECT password FROM users where username == '{username}'")
    data = res.fetchall()
    if len(data) <= 0:
        return None

    return data[0][0]


def check_creation():
    res = cur.execute("SELECT name FROM sqlite_master")
    print(res.fetchone())


def check_pw(username, clear_pw):
    hash_pw = get_pw(username)
    if hashlib.sha256(clear_pw.encode(), usedforsecurity=True).hexdigest() == hash_pw:
        return True
    return False


if __name__ == '__main__':
    print("Login")
    username = input("Username: ")
    pw = input("Password: ")

    print(check_pw(username, pw))

