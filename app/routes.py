from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, CheckoutForm, CreateForm, DeleteForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Book, Student, Checkout
from sqlalchemy import exc
import sys

@app.route('/', methods=['GET', 'POST'])
def index():
    books = Book.query.filter_by(deleted=False).all()
    students = Student.query.filter_by(deleted=False).all()
    form = CheckoutForm()
    form.book_select.choices = [(book.id, book.title + " (" + str(book.number_books) + ")") for book in books]
    form.student_select.choices = [(student.id, student.name) for student in students]

    # TODO: Handle error cases where books < 0 
    def checkout(form_book=None, form_student=None, is_return=False):
        try:
            book = Book.query.filter_by(id=form_book).first()
            student = Student.query.filter_by(id=form_student).first()

            if not is_return and book.number_books <= 0:
                flash('{} does not have any more copies available.'.format(book.title))
                if book.lastCheckout():
                    flash('The last student to have checked out this book was {}'.format(book.lastCheckout().getStudent().name))
                return redirect(url_for('index'))

            if not is_return and student.is_owning(book):
                flash('{} has already checked out a copy of {}.'.format(student.name, book.title))
                return redirect(url_for('index'))
            
            if is_return and student.is_owning(book):
                book.number_books = book.number_books + 1
                student.returnBook(book)
                flash('{} successfully returned {}'.format(student.name, book.title))
            elif is_return and not student.is_owning(book):
                flash('{} does not currently own a copy of {}'.format(student.name, book.title))
                return redirect(url_for('index'))
            else:
                book.number_books = book.number_books - 1
                student.checkoutBook(book)
                flash('{} successfully checked out {}'.format(student.name, book.title))
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

# TODO: Admin page displays statistics on how many books are checked out, last book checked out, last book returned. Overall database display, genres(?)
@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
def admin_create():
    books = Book.query.filter_by(deleted=False).all()
    checkout_count = Checkout.query.filter_by(is_return=False).count() - Checkout.query.filter_by(is_return=True).count()

    create_form = CreateForm()
    delete_form = DeleteForm()
    delete_form.book_select.choices = [(book.id, book.title) for book in books]
    
    # TODO: Add a loop so that for every Quizlet-like entry provided in the view a new book is created.
    if create_form.create_book.data:
        # Separate into new create() route
        if create_form.validate_on_submit():
            new_book = Book(create_form.book_title.data, create_form.author.data, create_form.copies.data)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('admin_create'))
    elif delete_form.delete_book.data:
        if delete_form.validate_on_submit():
            return redirect(url_for('delete_book', id=delete_form.book_select.data))

    return render_template('admin-create.html', title='Admin Page', books=books, form_one=create_form, form_two=delete_form, checkout_count=checkout_count)

@app.route('/admin/stats', methods=['GET', 'POST'])
@login_required
def admin_stats():
    checkout_count = Checkout.query.filter_by(is_return=False).count() - Checkout.query.filter_by(is_return=True).count()
    last_checkout = Checkout.query.order_by(Checkout.id.desc()).first()
    return render_template('admin-stats.html', checkout_count=checkout_count, last_checkout=last_checkout)

# TODO: Fix login to better implement remember me data
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

@app.route('/students/<id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    if student.deleted:
        abort(404)
    student.deleted = True
    db.session.commit()
    return '', 204

@app.route('/books/<id>', methods=['GET', 'POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.deleted:
        abort(404)
    book.deleted = True
    db.session.commit()
    flash('{} was successfully deleted from the library.'.format(book.title))
    return redirect(url_for('admin_create'))


