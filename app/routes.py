from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, CheckoutForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Book, Student, Checkout
from sqlalchemy import exc
import sys

@app.route('/', methods=['GET', 'POST'])
def index():
    books = Book.query.all()
    students = Student.query.all()
    form = CheckoutForm()
    form.book_select.choices = [(book.id, book.title) for book in books]
    form.student_select.choices = [(student.id, student.name) for student in students]

    def checkout(form_book=None, form_student=None, is_return=False):
        try:
            book = Book.query.filter_by(id=form_book).first()
            student = Student.query.filter_by(id=form_student).first()

            if not is_return and student.is_owning(book):
                flash('{} has already checked out a copy of {}.'.format(student.name, book.title))
                return redirect(url_for('index'))
            
            if is_return and student.is_owning(book):
                book.number_books = book.number_books + 1
                student.returnBook(book)
                flash('Book successfully returned!')
            elif is_return and not student.is_owning(book):
                flash('{} does not currently own a copy of {}'.format(student.name, book.title))
                return redirect(url_for('index'))
            else:
                book.number_books = book.number_books - 1
                student.checkoutBook(book)
                flash('Book successfully checked out!')

            new_checkout = Checkout(student, book, is_return)
            db.session.add(new_checkout)
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return render_template('500.html'), 500

    if form.validate_on_submit():
        if form.checkout_field.data:
            checkout(form.book_select.data, form.student_select.data, False)
            return redirect(url_for('index'))
        else:
            checkout(form.book_select.data, form.student_select.data, True)
            return redirect(url_for('index'))

    return render_template('index.html', title='Home', books=books, form=form)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', title='Admin Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

