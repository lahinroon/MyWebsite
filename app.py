import datetime
import functools
import os
import urllib

from flask import (Flask, flash, redirect, render_template, request,
                   Response, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import path
from werkzeug.datastructures import ContentRange

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)
DB_NAME = "blog.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime)
    published = db.Column(db.Boolean)
    content = db.Column(db.Text)

""" def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/blog/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('blog'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('/blog/login.html', next_url=next_url)

@app.route('/blog/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('/blog/logout.html') """

@app.route("/blog")
def index():
    return render_template('/blog/blog.html')

@app.route('/blog/create/', methods=['GET', 'POST'])
#@login_required
def create():
    return render_template('/blog/create.html')

@app.route('/blog/addpost', methods=['POST'])
def addpost():
    title = request.form.get('title')
    content = request.form.get('content')
    published = request.form.get('published')
    if published == 'y':
        published = True

    post = Blogpost(title=title, content=content, published=published, date_posted=datetime.now())
    
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('blog')) 

@app.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.get(post_id)
    return render_template('/blog/detail.html', post=post)

@app.route('/blog/drafts/')
#@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('/blog/blog.html', query, check_bounds=False)

'''@app.route('/blog/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Blogpost.select()
    else:
        query = Blogpost.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('/blog/detail.html', entry=entry)'''

@app.route('/blog/<slug>/edit/', methods=['GET', 'POST'])
#@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    return _create_or_edit(entry, '/blog/edit.html')

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    # We'll use this template filter in the pagination include. This filter
    # will take the current URL and allow us to preserve the arguments in the
    # querystring while replacing any that we need to overwrite. For instance
    # if your URL is /?q=search+query&page=2 and we want to preserve the search
    # term but make a link to page 3, this filter will allow us to do that.
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/blog")
def blog():
    return render_template("/blog/blog.html")

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

def main():
    if not path.exists(DB_NAME):
        db.create_all(app=app)
    app.run(debug=True)

if __name__ == '__main__':
    main()
    