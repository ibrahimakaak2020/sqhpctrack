from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class UserForm(FlaskForm):
    staffno = IntegerField('Staff No', validators=[DataRequired(), NumberRange(min=1)])
    staffname = StringField('Staff Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    isadmin = BooleanField('Is Admin')
    submit = SubmitField('Submit')
