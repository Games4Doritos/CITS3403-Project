# Define authentication forms using Flask-WTF.
# Fields and validation are handled here, then rendered in HTML templates and validated in routes.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app.models import Player

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Required'), Email()])# Error messages design later
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

    def validate_email(self, email):
        if Player.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exists')
        