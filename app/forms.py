from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Required, ValidationError
from app.models import Book

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me') 
    submit = SubmitField('Sign In')

class CheckoutForm(FlaskForm):
    book_select = SelectField(u'Book Selection', coerce=int, validators=[DataRequired()])
    student_select = SelectField(u'Student', coerce=int, validators=[DataRequired()])
    checkout_field = SubmitField('Checkout')
    return_field = SubmitField('Return')

class CreateForm(FlaskForm):
    book_title = StringField('Input a book title: ', validators=[DataRequired()])
    author = StringField('Input an author name: ', validators=[DataRequired()])
    copies = IntegerField('Input the number of copies: ') 
    create_book = SubmitField('Create A Book')

def validate_delete(form, field):
    if field.data == "":
        raise ValidationError("Testing")

class DeleteForm(FlaskForm):
    author_select = SelectField(u'Select Author', default='', coerce=int, validators=[validate_delete])
    book_select = SelectField(u'Select Book', default='', coerce=int, validators=[validate_delete])
    delete_book = SubmitField('Delete the Book')

class TestForm(FlaskForm):
    author_select = SelectField(u'Select Author', coerce=int)
    book_select = SelectField(u'Select Book', coerce=int)
    

    
    
    