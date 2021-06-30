from flask import (Blueprint, Response,  url_for, redirect, render_template)

views = Blueprint('views', __name__)

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/about")
def about():
    return render_template("about.html")

@views.route("/contact")
def contact():
    return render_template("contact.html")

@views.route("/admin")
def admin():
    return redirect(url_for("home"))

@views.route("/portfolio")
def portfolio():
    return redirect(url_for("home"))

@views.route(404)
def not_found():
    return Response('<h3>Not found</h3>'), 404