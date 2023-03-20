from functools import wraps
from flask import Flask, render_template, g, session, request, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'any random string'


def check_login(username, password):
    if password == "cod123":
        return True
    return False


def get_posts(category):
    all_posts = []
    file_names = os.listdir(f".\\data\\{category}")
    for file_name in file_names:
        with open(f".\\data\\{category}\\{file_name}", "r") as file:
            all_posts.append(json.loads(file.read()))
    return all_posts


def get_post(category, id):
    if category not in os.listdir(".\\data"):
        return None
    if f"{id}.json" not in os.listdir(f".\\data\\{category}"):
        return None

    with open(f".\\data\\{category}\\{id}.json", "r") as file:
        post = json.loads(file.read())
    return post


def register(username, password, name):
    # implement SQL Here
    # if username already exists: return False
    # sonst: anlegen in db und return True
    pass


def create_post(title, description, category):
    print(os.getcwd())
    id = int(os.listdir(f".\\data\\{category}")[-1].strip(".json")) + 1
    current_post = {"title": title, "desc": description, "id": id}
    with open(f".\\data\\{category}\\{id}.json", "w") as file:
        file.write(json.dumps(current_post))
    return category, id


def login_required(f):
    """decorator function if a site should only be visible, if the user is logged in"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session.keys():
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    return render_template("home.j2")


@app.route("/info")
def info():
    return render_template("info.j2")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_login(request.form["username"], request.form["password"]):
            session["username"] = request.form["username"]
            return redirect("/")
        g.error = True
    return render_template("login.j2")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: bei zusammenführung: check form namen
        if register(request.form["username"], request.form["password"], request.form["name"]):
            session["username"] = request.form["username"]
            return redirect("/")
        g.error = True
    return render_template("Register.html")


@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    return redirect("/")


@app.route("/category/<cat>")
def category(cat):
    g.cat = cat
    g.posts = get_posts(cat)
    return render_template("categories.j2")


@app.route("/post/<category>/<post_id>")
def post(category, post_id):
    post = get_post(category, post_id)
    if post is not None:
        g.titel = post["title"]
        g.desc = post["desc"]
        return str(post)
    else:
        return "", 404


@app.route("/post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        category, id = create_post(request.form["titel"], request.form["description"], request.form["category"])
        return redirect(f"/post/{category}/{id}")
    return render_template("Question.html")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)
