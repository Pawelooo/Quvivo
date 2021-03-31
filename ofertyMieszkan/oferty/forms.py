from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from oferty.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20, message="Nazwa "
                                                                                                          "użytkownika musi się składać z conajmniej 2 do maks. 20 znaków")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=8, max=40)])
    confirm_password = PasswordField('Powtórz hasło',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Zajerestruj się')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ta nazwa użytkownika jest zajęta ! Prosze wybrać inna nazwe użytkownika')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(f'Ten email jest już zajety ! Prosze wybrać inna email')


class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField('Zapamiętej mnie')
    submit = SubmitField('Zaloguj się')


class SearchingTownForm(FlaskForm):
    city = StringField('miasto', validators=[DataRequired()])
    options = SelectField()


class UpdateAccountForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20, message="Nazwa "
                                                                                                          "użytkownika musi się składać z conajmniej 2 do maks. 20 znaków")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Aktualizowanie zdjęcie porfilowego', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Zaakutalizuj')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ta nazwa użytkownika jest zajęta ! Prosze wybrać inna nazwe użytkownika')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError(f'Ten email jest już zajety ! Prosze wybrać inna email')


class PostFrom(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    content = TextAreaField('Treść', validators=[DataRequired()])
    submit = SubmitField('Dodaj post')


class AddCommentForm(FlaskForm):
    text = StringField('Komentarz', validators=[InputRequired()])
    submit = SubmitField('Dodaj Komentarz')


class AddAppartmentToObservation(FlaskForm):
    submit = SubmitField('+')
