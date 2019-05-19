from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    g_number = db.Column(db.Integer)

    def __init__(self, name=None, email=None, g_number=None):
        self.name = name
        self.email = email
        self.g_number = g_number

    def __repr__(self):
        return '<Student {}>'.format(self.name)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    number_books = db.Column(db.Integer)

    def __init__(self, title=None, author=None, number_books=None):
        self.title = title
        self.author = author
        self.number_books = number_books 

    def __repr__(self):
        return '<Book {}>'.format(self.title)

class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    student = db.relationship('Student', foreign_keys=[student_id])
    book = db.relationship('Book', foreign_keys=[book_id])
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    isReturn = db.Column(db.Boolean, unique=False)

    def __init__(self, student=None, book=None, isReturn=None):
        self.student = student
        self.book = book
        self.isReturn = isReturn

    def __repr__(self):
        return '<Checkout of {} by {}>'.format(self.book.title, self.student.name)
