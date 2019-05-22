from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Required
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
    
    
    