from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    staff_number = StringField('Staff Number', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EquipmentForm(FlaskForm):
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(max=50)])
    model_name = StringField('Model Name', validators=[DataRequired(), Length(max=100)])
    equipment_type = StringField('Equipment Type', validators=[DataRequired(), Length(max=50)])
    manufacturer = StringField('Manufacturer', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    building = StringField('Building', validators=[DataRequired(), Length(max=100)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Register Equipment')

class MaintenanceRecordForm(FlaskForm):
    equipment_sn = SelectField('Equipment Serial Number', coerce=str, validators=[DataRequired()])
    problem_description = TextAreaField('Problem Description', validators=[DataRequired()])
    submit = SubmitField('Create Maintenance Record')

class StatusForm(FlaskForm):
    status_type = SelectField('Status Type', choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Add Status')