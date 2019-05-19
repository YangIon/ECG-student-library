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
   # options = Book.query.all().count()
    checkout = SelectField(u'Book Selection', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')], validators=[Required()])
