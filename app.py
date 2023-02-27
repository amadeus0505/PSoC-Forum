from functools import wraps
from flask import Flask, render_template, g, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'any random string'


def check_login(username, password):
    if password == "cod123":
        return True
    return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session.keys():
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():  # put application's code here
    return render_template("index.j2")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_login(request.form["username"], request.form["password"]):
            session["username"] = request.form["username"]
            return redirect("/")
        return redirect("/login?error=true")
    if "error" in request.args.keys():
        g.error = request.args["error"]
    return render_template("login.j2")


@app.route("/category/<cat>")
def category(cat):
    g.cat = cat
    session["posts"] = [
        {"title": "TITEL des 1. Posts", "desc": "Projektbeschreibung 1", "id": 0},
        {"title": "TITEL des 2. Posts", "desc": "Projektbeschreibung 2", "id": 1},
        {"title": "TITEL des 3. Posts", "desc": "Projektbeschreibung 3", "id": 2},
        {"title": "TITEL des 4. Posts", "desc": "Projektbeschreibung 4", "id": 3}
    ]
    return render_template("categories.j2")


@app.route("/post/<post_id>")
def post(post_id):
    try:
        post = [post for post in session["posts"] if post["id"] == int(post_id)][0]
    except IndexError:
        return "", 404
    g.titel = post["title"]
    g.desc = post["desc"]
    return str(post)


@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    return redirect("/")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)
