from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
