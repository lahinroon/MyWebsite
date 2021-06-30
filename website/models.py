from . import db 
from flask_login import UserMixin
from flask_login.mixins import UserMixin

# Create models for blogposts and users to store in the database
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime)
    published = db.Column(db.Boolean)
    content = db.Column(db.Text)
    slug = db.Column(db.String(50))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
