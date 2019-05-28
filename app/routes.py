from flask import render_template, flash, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, CheckoutForm, CreateForm, DeleteForm, TestForm
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

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    books = Book.query.all()
    create_form = CreateForm()
    delete_form = DeleteForm()
    delete_form.book_select.choices = [(book.id, book.title) for book in books]
    delete_form.author_select.choices = [(book.id, book.author) for book in books]
    
    if create_form.create_book.data:
        if create_form.validate_on_submit():
            new_book = Book(create_form.book_title.data, create_form.author.data, create_form.copies.data)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('admin'))
    elif delete_form.delete_book.data:
        print(delete_form.errors, file=sys.stderr)
        if delete_form.validate_on_submit():
            print("Delete Works Separately", file=sys.stderr)

    return render_template('admin.html', title='Admin Page', books=books, form_one=create_form, form_two=delete_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/test')
def test():
    form = TestForm()
    form.book_select.choices = [(book.id, book.title) for book in Book.query.all()]
    form.author_select.choices = [(book.id, book.author) for book in Book.query.all()]
    return render_template('test.html', form=form)

@app.route('/author/<title>')
def author(title):
    books = Book.query.filter_by(title=title).all()

    authorArray = []

    for book in books:
        authorObj = {}
        authorObj['id'] = book.id
        authorObj['author'] = book.author
        authorArray.append(authorObj)
    
    return jsonify({'authors' : authorArray})


