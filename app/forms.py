# Define authentication forms using Flask-WTF.
# Fields and validation are handled here, then rendered in HTML templates and validated in routes.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import current_user
from app.models import Account


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Required'), Email()])
    password = PasswordField('Password', validators=[DataRequired('Required')])


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Required'), Email(message='Invalid email format')])
    password = PasswordField('Password', validators=[DataRequired('Required'), Length(min=6, message='At least 6 characters')])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired('Required'),
            EqualTo('password', message='Confirmation password does not match')
        ]
    )

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username is required'),Length(min=2, max=30, message='Username must be between 2 and 30 characters')])
    email = StringField('Email', validators=[DataRequired('Email is required'), Email(message='Invalid email format')])

    def validate_email(self, email):
        existing_account = Account.query.filter_by(email=email.data.strip().lower()).first()

        if existing_account and existing_account.id != current_user.id:
            raise ValidationError('Email already in use')