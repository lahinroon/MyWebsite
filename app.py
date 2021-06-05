import functools
import os
import urllib
import re

from flask import (Flask, flash, redirect, render_template, request,
                   Response, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import error, path
from werkzeug.datastructures import ContentRange
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "blog.db"

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

db = SQLAlchemy(app)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime)
    published = db.Column(db.Boolean)
    content = db.Column(db.Text)
    slug = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/blog/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Passwords don\'t match', category=error)
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(username=username, 
                            password=generate_password_hash(password, method='sha256'))
    
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login')) 

    return render_template('/blog/signup.html')

@app.route('/blog/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first_or_404()

        if user:
            if check_password_hash(user.password, password):
                session['logged_in'] = True
                session.permanent = True  # Use cookie to store session.
                flash('You are now logged in.', 'success')
           
                return redirect(url_for('blog'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('User does not exist', category=error)

    return render_template('/blog/login.html', next_url=next_url)

"""
@app.route('/blog/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('/blog/logout.html') """

@app.route("/blog")
def index():
    posts = Blogpost.query.all()
    return render_template('/blog/blog.html', posts=posts) 

@app.route('/blog/drafts/')
#@login_required
def drafts():
    posts = Blogpost.query.filter_by(published = False).all()
    return render_template('/blog/blog.html', posts=posts, drafts=True)

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
    else:
        published = False

    slug = re.sub(r'[^\w]+', '-', title.lower()).strip('-')

    post = Blogpost(title=title, content=content, published=published, 
                    date_posted=datetime.now(), slug = slug)
    
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('blog')) 

@app.route('/blog/delete/<slug>/')
def delete(slug):
    post_to_delete = Blogpost.query.filter_by(slug=slug).first_or_404()

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('blog'))
    except:
        'There was an error deleting this post'

    return render_template('/blog/blog.html')

'''@app.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.get(post_id)
    return render_template('/blog/detail.html', post=post)'''

@app.route('/blog/<slug>/')
def detail(slug):
    post = Blogpost.query.filter_by(slug=slug).first_or_404()
    date_posted = post.date_posted.strftime('%B %d, %Y')
    return render_template('/blog/detail.html', post=post, date_posted=date_posted)


@app.route('/blog/<slug>/edit/', methods=['GET', 'POST'])
#@login_required
def edit(slug):
    post = Blogpost.query.filter_by(slug=slug).first_or_404()
    
    if request.method == 'POST':

        post.title = request.form.get('title')
        post.content = request.form.get('content')
        published = request.form.get('published')
        slug = re.sub(r'[^\w]+', '-', post.title.lower()).strip('-')
        post.slug = slug

        if published == 'y':
            published = True
        else:
            published = False
        post.published = published

        db.session.commit()

    return render_template('/blog/edit.html', post=post)
'''
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
    '''

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
