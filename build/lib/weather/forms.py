from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from weather.models import User


class RegistrationForm(FlaskForm):
    user_name = StringField('Gebruikerrnaam', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Bevestig password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registreer')

    '''
        Actually, the user name is not unique. The email address must be unique!
    '''
    def validate_user_name(self, user_name):
        user = User.query.filter_by(user_name=user_name.data).first()
        if user:
            raise ValidationError('De gebruikernaam is niet bechibaar! Selecteer a.u.b. een ander naam')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Het email adres is al in gebruik. Selecteer a.u.b. een ander email adres')


class Account_configForm(FlaskForm):
    user_name = StringField('Gebruikerrnaam', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_picture = FileField('Selecteer profiel foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')

    '''
        Actually, the user name is not unique. The email address must be unique!
    '''
    def validate_user_name(self, user_name):
        if user_name.data != current_user.user_name:
            user = User.query.filter_by(user_name=user_name.data).first()
            if user:
                raise ValidationError('De gebruikernaam is niet bechibaar! Selecteer a.u.b. een ander naam')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Het email adres is al in gebruik. Selecteer a.u.b. een ander email adres')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Aanmelden')


