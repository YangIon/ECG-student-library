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

checkouts = db.Table('checkouts',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('transaction_date', db.DateTime, index=True, default=datetime.utcnow)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    g_number = db.Column(db.Integer)
    books = db.relationship('Book', secondary=checkouts, backref=db.backref('checkouts', lazy='dynamic'))

    def __repr__(self):
        return '<Student {}>'.format(self.name)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    number_books = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Book {}>'.format(self.title)