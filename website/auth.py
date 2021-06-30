import os
import uuid
import re
from flask import Blueprint, url_for, redirect, render_template, flash, request
from .models import User, Blogpost
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from . import db
from datetime import datetime
from os import error, path
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)


@auth.route('/blog/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('NO', category='error')
        elif password != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(username=username,
                            password=generate_password_hash(password, method='sha256'))

            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')

            return redirect(url_for('auth.login'))

    return render_template('/blog/signup.html', user=current_user)


@auth.route('/blog/login/', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flash('You are already logged in', category='error')
        return redirect(url_for('auth.blog'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if user.id != 6:
                flash('Cannot log into this account', category='error')
                return redirect(url_for('auth.blog'))

            if check_password_hash(user.password, password):
                flash('You are now logged in.', 'success')
                login_user(user, remember=True)

                return redirect(url_for('auth.blog'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('User does not exist', category='error')

    return render_template('/blog/login.html', user=current_user)


@auth.route('/blog/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('/blog/logout.html')


ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route("/upload_image", methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        print(request.files)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('auth.create'))
        if file and allowed_file(file.filename):
            # if image with same name exists
            if os.path.exists('static/img/blog' + '/' + file.filename):
                _dot = file.filename.find(".")
                file.filename = file.filename[:_dot] + \
                    str(uuid.uuid4()) + file.filename[_dot:]
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/img/blog', filename))
            return file.filename


@auth.route("/blog")
def blog():
    posts = Blogpost.query.all()
    return render_template('/blog/blog.html', posts=posts, user=current_user)


@auth.route('/blog/drafts/')
def drafts():
    posts = Blogpost.query.filter_by(published=False).all()
    return render_template('/blog/blog.html', posts=posts, drafts=True)


@auth.route('/blog/create/', methods=['GET', 'POST'])
def create():
    return render_template('/blog/create.html')


@auth.route('/blog/addpost', methods=['POST'])
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
                    date_posted=datetime.now(), slug=slug)

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('auth.blog'))


@auth.route('/blog/delete/<slug>/')
def delete(slug):
    post_to_delete = Blogpost.query.filter_by(slug=slug).first_or_404()

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('auth.blog'))
    except:
        flash('There was an error deleting this post', category='error')

    return render_template('/blog/blog.html')


@auth.route('/blog/<slug>/')
def detail(slug):
    post = Blogpost.query.filter_by(slug=slug).first_or_404()
    date_posted = post.date_posted.strftime('%B %d, %Y')
    return render_template('/blog/detail.html', post=post, date_posted=date_posted)


@auth.route('/blog/<slug>/edit/', methods=['GET', 'POST'])
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
        return render_template('/blog/detail.html', post=post)

    return render_template('/blog/edit.html', post=post)
