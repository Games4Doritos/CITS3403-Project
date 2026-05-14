# Define authentication forms using Flask-WTF.
# Fields and validation are handled here, then rendered in HTML templates and validated in routes.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import current_user
from app.models import Account


class LoginForm(FlaskForm):
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message='Required'), 
            Email(message='Invalid email format'),
            Length(max=30)
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(message='Required'),
            Length(max=64)
        ]
    )


class SignupForm(FlaskForm):
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message='Required'), 
            Email(message='Invalid email format'), 
            Length(max=30, message='Max length (30) exceeded')
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired('Required'), 
            Length(min=6, max=64, message='Password must be between 6 and 64 characters') 
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Required'),
            EqualTo('password', message='Confirmation password does not match'),
            Length(max=64)
        ]
    )

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Username is required'),Length(min=2, max=18, message='Username must be between 2 and 18 characters')])
    email = StringField('Email', validators=[DataRequired(message='Email is required'), Email(message='Invalid email format'),  Length(max=30, message='Max length (30) exceeded')])

    def validate_email(self, email):
        existing_account = Account.query.filter_by(email=email.data.strip().lower()).first()

        if existing_account and existing_account.id != current_user.id:
            raise ValidationError('Email already in use')