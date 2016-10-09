from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, RadioField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo,Optional
from wtforms import ValidationError
from ..models import Volunteer

class LoginForm(Form):

    email = StringField('Email', validators=[Required(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
