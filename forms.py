from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, BooleanField, PasswordField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import re

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min = 6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(regex, email.data)):
            pass
        else:
            raise ValidationError('Please enter a valid email')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min = 6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(regex, email.data)):
            pass
        else:
            raise ValidationError('Please enter a valid email')

class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    resume = FileField('Update Resume', validators=[FileAllowed(['pdf'])])
    update = SubmitField('Update')

    def validate_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(regex, email.data)):
            pass
        else:
            raise ValidationError('Please enter a valid email')


class AddJobForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    job_desc = TextAreaField('Job Description', validators=[DataRequired()])
    skills_required = TextAreaField('Skills Required', validators=[DataRequired()])
    salary = StringField('Salary', validators=[DataRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d')
    submit = SubmitField('Submit')