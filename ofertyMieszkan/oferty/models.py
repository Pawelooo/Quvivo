from datetime import datetime

from oferty import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    Announcements = db.relationship('Announcement', backref='obserwujacy', lazy=True)
    posts = db.relationship('Post', backref='autor', lazy=True)

    def __repr__(self):
        return f'User("{self.username}", "{self.email}", {self.image_file}")'


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annoucements = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Annoucment('{self.annoucements}', '{self.user_id}'"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy=True)

    def get_comments(self):
        return Comment.query.filter_by(post_id=Post.id).order_by(Comment.date_posted.desc())

    def __repr__(self):
        return f"Ogłoszenie ('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.text}', '{self.date_commented}')"


class Appartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(25), nullable=False)
    city_district = db.Column(db.String(100), nullable=False)
    type_of_sale = db.Column(db.String(25), nullable=False)
    link = db.Column(db.String(255), nullable=False)
