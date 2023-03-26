from functools import wraps
from flask import Flask, render_template, g, session, request, redirect, url_for
import json
import os
import sql


### TODO: implement https://www.tiny.cloud/docs/demo/full-featured/#fullfeaturednon-premiumplugins

app = Flask(__name__)
app.secret_key = 'any random string'


def search(keyword):
    posts = []
    for cat in os.listdir("./data"):
        for post_path in os.listdir(f"./data/{cat}/"):
            with open(f"./data/{cat}/{post_path}") as file:
                post = json.loads(file.read())
            if keyword in post["desc"] or keyword in post["title"]:
                post["category"] = cat
                posts.append(post)
    return posts


def check_login(username, password):
    return sql.check_pw(username, password)


def get_posts(category):
    all_posts = []
    file_names = os.listdir(f".\\data\\{category}")
    for file_name in file_names:
        with open(f".\\data\\{category}\\{file_name}", "r") as file:
            all_posts.append(json.loads(file.read()))
    return all_posts[::-1]   # reversed, damit neue poststs ganz oben sind


def get_post(category, id):
    if category not in os.listdir(".\\data"):
        return None
    if f"{id}.json" not in os.listdir(f".\\data\\{category}"):
        return None

    with open(f".\\data\\{category}\\{id}.json", "r") as file:
        post = json.loads(file.read())
    return post


def get_latest_post(category):
    # fetch the highest id
    post_id = int(os.listdir(f".\\data\\{category}")[-1].strip(".json"))
    # return according post
    return get_post(category, post_id)


def register(username, password, name):
    # if username already exists: return False
    # sonst: return True
    return sql.adduser(username, name, password)


def create_post(title, description, category, author):
    try:
        post_id = int(os.listdir(f".\\data\\{category}")[-1].strip(".json")) + 1
    except IndexError:
        post_id = 0
    current_post = {"title": title, "desc": description, "id": post_id, "author": author}
    with open(f".\\data\\{category}\\{post_id}.json", "w") as file:
        file.write(json.dumps(current_post))
    return category, post_id


def add_comment(category, id, comment, author):
    comment_item = {"comment": comment, "author": author}
    with open(f"./data/{category}/{id}.json", "r+") as read_file:
        post: dict = json.loads(read_file.read())
        comments = []
        if "comments" in post.keys():
            comments = post["comments"]

        comments.append(comment_item)
        post["comments"] = comments
        with open(f"./data/{category}/{id}.json", "w") as write_file:
            write_file.write(json.dumps(post))


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
    g.hardware_post = get_latest_post("hardware")
    g.software_post = get_latest_post("software")
    g.projects_post = get_latest_post("projects")
    return render_template("home.j2")


@app.route("/info")
def info():
    return render_template("info.j2")


@app.route("/login", methods=["GET", "POST"])
def login():
    if len(request.args) > 0:
        session["next_url"] = request.args["next"]
    if request.method == "POST":
        if check_login(request.form["username"], request.form["password"]):
            session["username"] = request.form["username"]
            if session.get("next_url") is not None:
                url = session["next_url"]
                session.pop("next_url", None)
                return redirect(url)
            return redirect("/")
        g.error = True
    return render_template("login.j2")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: bei zusammenführung: check form namen
        if register(request.form["username"], request.form["password"], request.form["name"]):
            session["username"] = request.form["username"]
            if session.get("next_url") is not None:
                url = session["next_url"]
                session.pop("next_url", None)
                return redirect(url)
            return redirect("/")
        g.error = True
    return render_template("register.j2")


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
        return "404: Post Not Found", 404


@app.route("/post/<category>/<post_id>/new_comment", methods=["POST"])
@login_required
def new_comment(category, post_id):
    comment = request.form["comment"]
    author = session["username"]
    add_comment(category, post_id, comment, author)
    return str(comment)


@app.route("/post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        category, id = create_post(
            request.form["titel"],
            request.form["description"],
            request.form["category"].lower(),
            session["username"])
        return redirect(f"/post/{category}/{id}")
    return render_template("question.j2")


@app.route("/search")
def display_search():
    keyword = request.args["search"]
    posts = search(keyword)
    g.keyword = keyword
    for post in posts:
        print(post["category"])
    g.posts = posts
    return render_template("search.j2", keyword=keyword)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)
