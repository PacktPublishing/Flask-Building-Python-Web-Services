from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, EqualTo
from my_app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    pwdhash = db.Column(db.String())
 
    def __init__(self, username, password):
        self.username = username
        self.pwdhash = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class RegistrationForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField(
        'Password', [
            InputRequired(), EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Confirm Password', [InputRequired()])


class LoginForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])


class OpenIDForm(Form):
    openid = TextField('OpenID', [InputRequired()])
