from datetime import datetime
import pytz
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

def easterntz(dttm):
    utcmoment_naive = dttm 
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    timezone = 'America/New_York'
    local_datetime = utcmoment.astimezone(pytz.timezone(timezone))
    return local_datetime

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
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)

# TODO: Unique constraint for g_number, soft-delete design pattern
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    g_number = db.Column(db.Integer, unique=True)
    books = db.relationship('Book', secondary=checkouts, backref=db.backref('student', lazy='dynamic'), lazy='dynamic')
    deleted = db.Column(db.Boolean(), default=False)

    def __init__(self, name=None, email=None, g_number=None):
        self.name = name
        self.email = email
        self.g_number = g_number

    def __repr__(self):
        return '<Student {}>'.format(self.name)

    def checkoutBook(self, book):
        if not self.is_owning(book):
            self.books.append(book)
    
    def returnBook(self, book):
        if self.is_owning(book):
            self.books.remove(book)
    
    def is_owning(self, book):
        return self.books.filter(
            checkouts.c.book_id == book.id).count() > 0

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    number_books = db.Column(db.Integer)
    deleted = db.Column(db.Boolean(), default=False)

    def __init__(self, title=None, author=None, number_books=None):
        self.title = title
        self.author = author
        self.number_books = number_books 

    def __repr__(self):
        return '<Book {}>'.format(self.title)

    def lastCheckout(self):
        return Checkout.query.filter_by(book_id=self.id).order_by(Checkout.id.desc()).first()

class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    student = db.relationship('Student', backref=db.backref("checkouts"))
    book = db.relationship('Book', backref=db.backref("checkouts"))
    dttm = db.Column(db.DateTime, index=True, default=easterntz(datetime.utcnow()))
    is_return = db.Column(db.Boolean, unique=False)

    def __init__(self, student=None, book=None, is_return=None):
        self.student = student
        self.book = book
        self.is_return = is_return

    def __repr__(self):
        if self.is_return:
            return '<< Return of {} by {} on {} >>'.format(self.book.title, self.student.name, self.getFormattedDate())
        else:
            return '<< Checkout of {} by {} on {} >>'.format(self.book.title, self.student.name, self.getFormattedDate())
    
    def getStudent(self):
        return self.student
    
    def getBook(self):
        return self.book

    def getFormattedDate(self):
        fmt = "%b %d, %Y %I:%M %p"
        return self.dttm.strftime(fmt)
