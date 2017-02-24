# ourapp/forms.py

# from flask_wtf import FlaskForm
# from wtforms import TextField, PasswordField
# from wtforms.validators import Required
# from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

# class EmailPasswordForm(FlaskForm):
    # password = PasswordField('password', validators=[Required()])

class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired()])	


class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
	
class NewChannelForm(FlaskForm):
	channelname=StringField('Channel name', [validators.Length(min=4, max=25)])
	description=StringField('Description',[validators.Length(min=4, max=100)])
	
