from functools import wraps
from flask import Flask, render_template, g, session, request, redirect, url_for
import json
import os
import sql


### TODO: implement https://www.tiny.cloud/docs/demo/full-featured/#fullfeaturednon-premiumplugins

app = Flask(__name__)
app.secret_key = 'any random string'

# Such algorythmus
def search(keyword):
    posts = []
    # in jedem ordner in jeder datei wird gesucht
    for cat in os.listdir("./data"):
        for post_path in os.listdir(f"./data/{cat}/"):
            # datei öffnen
            with open(f"./data/{cat}/{post_path}") as file:
                post = json.loads(file.read())
            # checken, ob suchwort im post vorkommt
            if keyword in post["desc"] or keyword in post["title"]:
                post["category"] = cat
                posts.append(post)
    return posts

# aufruf zur sql-datei
def check_login(username, password):
    return sql.check_pw(username, password)


# alle posts einer Kategorie
def get_posts(category):
    all_posts = []
    file_names = os.listdir(f".\\data\\{category}")
    # geht durch alle dateien durch
    for file_name in file_names:
        with open(f".\\data\\{category}\\{file_name}", "r") as file:
            all_posts.append(json.loads(file.read()))
    return all_posts[::-1]   # reversed, damit neue poststs ganz oben sind

# gibt einen bestimmten post zurück
def get_post(category, id):
    # wenn kategorie nicht existiert
    if category not in os.listdir(".\\data"):
        return None
    # wenn post id nicht existiert
    if f"{id}.json" not in os.listdir(f".\\data\\{category}"):
        return None

    # lesen und zurückgeben des posts
    with open(f".\\data\\{category}\\{id}.json", "r") as file:
        post = json.loads(file.read())
    return post


# den neuesten post einer kategorie bekommen
def get_latest_post(category):
    # fetch the highest id
    post_id = int(os.listdir(f".\\data\\{category}")[-1].strip(".json"))
    # return according post
    return get_post(category, post_id)


# einen neuen user registrieren
def register(username, password, name):
    # if username already exists: return False
    # sonst: return True
    return sql.adduser(username, name, password)


# einen neuen post erstelleb
def create_post(title, description, category, author):
    try:
        post_id = int(os.listdir(f".\\data\\{category}")[-1].strip(".json")) + 1
    except IndexError:
        # wenn keine datei im ordern ist (kein post)
        post_id = 0
    # parameter in dictionary speichern
    current_post = {"title": title, "desc": description, "id": post_id, "author": author}
    # in datei speichern
    with open(f".\\data\\{category}\\{post_id}.json", "w") as file:
        file.write(json.dumps(current_post))
    # eben erstellter post wird zurückgegeben
    return category, post_id


# einen kommentar bei inem post hinzufügen
def add_comment(category, id, comment, author):
    # kommentar in dictionary verpacken
    comment_item = {"comment": comment, "author": author}
    
    with open(f"./data/{category}/{id}.json", "r+") as read_file:
        post: dict = json.loads(read_file.read())
        comments = []
        # vorherige kommentare lesen, wenn welche da sind
        if "comments" in post.keys():
            comments = post["comments"]

        # den neuen kommentar hinzufügen
        comments.append(comment_item)
        post["comments"] = comments
        # alles schreiben
        with open(f"./data/{category}/{id}.json", "w") as write_file:
            write_file.write(json.dumps(post))


def login_required(f):
    """decorator function if a site should only be visible, if the user is logged in"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # herausfinden ob user angemeldet ist
        if "username" not in session.keys():
            # wenn nicht angemeldet -> rediret zu login page
            return redirect(url_for("login", next=request.url))
        # sonst wird die seite ganz normal aufgerufen
        return f(*args, **kwargs)

    return decorated_function


# home route
@app.route('/')
def home():
    # momentan die neuesten posts
    g.hardware_post = get_latest_post("hardware")
    g.software_post = get_latest_post("software")
    g.projects_post = get_latest_post("projects")
    return render_template("home.j2")


# info seite
@app.route("/info")
def info():
    return render_template("info.j2")


# login seite, methode post und get
@app.route("/login", methods=["GET", "POST"])
def login():
    # wenn ein next parameter übergeben wird -> speichern in cookies
    if len(request.args) > 0:
        session["next_url"] = request.args["next"]
    if request.method == "POST":
        # wenn method==post wird eingeloggt
        if check_login(request.form["username"], request.form["password"]):
            session["username"] = request.form["username"]
            if session.get("next_url") is not None:
                # wenn next nicht leer war -> weiterleitung zu next
                url = session["next_url"]
                session.pop("next_url", None)
                return redirect(url)
            # sonst wird man auf die Homepage weitergeleitet
            return redirect("/")
        # wenn username+pw nicht richtig (check_login -> False)
        g.error = True
    return render_template("login.j2")


# register seite
@app.route("/register", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # registrieren
        if register(request.form["username"], request.form["password"], request.form["name"]):
            # wenn account erstellt wurde -> automatisch einloggen
            session["username"] = request.form["username"]
            if session.get("next_url") is not None:
                # weiterleiten zu next_url
                url = session["next_url"]
                session.pop("next_url", None)
                return redirect(url)
            return redirect("/")
        # wenn username schon existiert (register -> False)
        g.error = True
    return render_template("register.j2")


# logout endpoint
@app.route("/logout")
# muss eingeloggt sein zum ausloggen
@login_required
def logout():
    # session cookie löschen
    session.pop("username", None)
    return redirect("/")


# kategorien Seite
@app.route("/category/<cat>")
def category(cat):
    g.cat = cat
    # hohlt sich alle posts der kategorie der URL
    g.posts = get_posts(cat)
    return render_template("categories.j2")


# post seite
@app.route("/post/<category>/<post_id>")
def post(category, post_id):
    # hohlt sich post
    post = get_post(category, post_id)
    # get_post -> None wenn post nicht existiert
    if post is not None:
        g.title = post["title"]
        g.desc = post["desc"]
        try:
            # wenn der post Kommentare hat
            g.comments = post["comments"]
        except KeyError:
            # wenn er keine Kommentare hat
            g.comments = []
        return render_template("post.j2")
    else:
        # wenn post nicht existiert
        return "404: Post Not Found", 404


# neuer kommentar enpoint
@app.route("/post/<category>/<post_id>/new_comment", methods=["POST"])
@login_required
def new_comment(category, post_id):
    # fetch Kommentar von post form
    comment = request.form["comment"]
    author = session["username"]
    # neuen kommentar bei post hinzufügen
    add_comment(category, post_id, comment, author)
    # danach weiterleitung zum ursprungspost
    return redirect(f"/post/{category}/{post_id}")


# neuen post erstellen - Seite
@app.route("/post", methods=["GET", "POST"])
# muss eingeloggt sein
@login_required
def new_post():
    if request.method == "POST":
        # neuer post wird erstellt
        category, id = create_post(
            request.form["titel"],
            request.form["description"],
            request.form["category"].lower(),
            session["username"])
        # umleitung auf post seite
        return redirect(f"/post/{category}/{id}")
    return render_template("question.j2")


# seite wenn etwas gesucht wurde
@app.route("/search")
def display_search():
    # suchwort fetchen
    keyword = request.args["search"]
    # alle posts die auf das suchwort passen
    posts = search(keyword)
    # übergeben an jinja-kontext
    g.keyword = keyword
    g.posts = posts
    return render_template("search.j2", keyword=keyword)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)
