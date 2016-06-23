from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length
import config

class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class registerForm(Form):
    username = TextField('Username', validators=[Length(min=3, max=10)])
    name = TextField('Name', validators=[DataRequired()])
    password = PasswordField('password', validators=[Length(min=4)])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')])
    registerkey = PasswordField('Register Key', validators=[DataRequired()])
    entrance_year = SelectField('Entrance Year', choices=config.entrance_type)

class MypageForm(Form):
    username = TextField('Username')
    cpassword = PasswordField('Current password', validators=[DataRequired()])
    password = PasswordField('Password')
    confirm = PasswordField('Confirm Password')
    name = TextField('Name', validators=[DataRequired()])

