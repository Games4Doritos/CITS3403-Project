# Define authentication forms using Flask-WTF.
# Fields and validation are handled here, then rendered in HTML templates and validated in routes.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app.models import Player

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[
            DataRequired(), 
            EqualTo('password', message='Confirmation password does not match')
        ]
    )

    def validate_email(self, email):
        if Player.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exists')
        