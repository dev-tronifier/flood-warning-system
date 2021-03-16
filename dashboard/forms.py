from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
import email_validator
from dashboard.models import User, Device, Data, Dam
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=20)])

    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=60)])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    dam = StringField('Dam Name',
                           validators=[DataRequired(), Length(min=1, max=60)])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken")

    def validate_dam(self, dam):
        dam = Dam.query.filter_by(name=dam.data).first()
        if not dam:
            raise ValidationError("This dam does not exist")


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=20)])

    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=60)])

    remember = BooleanField('Remember me')

    submit = SubmitField('Login')


class DeviceForm(FlaskForm):
    name = StringField('Device Name',
                      validators=[DataRequired(), Length(min=1, max=30)])

    mac = StringField('MAC Address',
                      validators=[DataRequired(), Length(min=1, max=17)])

    data_measured = StringField('Data Measured',
                                validators=[DataRequired(), Length(min=1, max=30)])

    submit = SubmitField('Add Device')


class SMSForm(FlaskForm):
    message_sms = TextAreaField('Enter your message', validators=[DataRequired()])
    submit_sms = SubmitField('Send Message')


class TwitterForm(FlaskForm):
    message_twitter = TextAreaField('Enter your message', validators=[DataRequired()])
    submit_twitter = SubmitField('Send Tweet')


class EmailForm(FlaskForm):
    subject_email = StringField("Subject",validators=[DataRequired()], render_kw={'placeholder':'Subject'})
    message_email = TextAreaField('Enter your message', validators=[DataRequired()])
    submit_email = SubmitField('Send Email')