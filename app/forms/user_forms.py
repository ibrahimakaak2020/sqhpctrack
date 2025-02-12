from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    class Meta:
        csrf = True  # Enable CSRF protection
        
    staffno = IntegerField('Staff Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    staffno = IntegerField('Staff Number', validators=[DataRequired()])
    staffname = StringField('Staff Name', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    isadmin = BooleanField('Administrator Access')
    submit = SubmitField('Register')

    def validate_staffno(self, field):
        if User.query.filter_by(staffno=field.data).first():
            raise ValidationError('This staff number is already registered.')

class UserUpdateForm(FlaskForm):
    staffname = StringField('Staff Name', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('New Password')
    password2 = PasswordField('Repeat New Password', validators=[EqualTo('password')])
    isadmin = BooleanField('Administrator Access')
    submit = SubmitField('Update') 