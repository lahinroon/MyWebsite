# source .venv/bin/activate
from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/<name>")
def user(name):
    return render_template("index.html", content=name)

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

if __name__== "__main__":
    app.run()

# testing 123