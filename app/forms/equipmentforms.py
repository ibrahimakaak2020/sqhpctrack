# app/main/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, DateTimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AddMaintenanceForm(FlaskForm):
    equipment_sn = IntegerField('Equipment Serial Number', validators=[DataRequired()])
    maintenance_id = StringField('Maintenance ID', validators=[DataRequired()])
    registered_by = IntegerField('Registered By', validators=[DataRequired()])
    maintenance_date = DateTimeField('Maintenance Date', validators=[DataRequired()])
    isactive = BooleanField('Is Active')
    problem_description = TextAreaField('Problem Description', validators=[DataRequired()])
    submit = SubmitField('Add Maintenance')

class UpdateMaintenanceStatusForm(FlaskForm):
    maintenance_id = IntegerField('Maintenance ID', validators=[DataRequired()])
    workshop_id = IntegerField('Workshop ID', validators=[DataRequired()])
    company_id = IntegerField('Company ID', validators=[DataRequired()])
    status_date = DateTimeField('Status Date', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    is_external = BooleanField('Is External')
    notes = TextAreaField('Notes')
    register_by = IntegerField('Registered By', validators=[DataRequired()])
    submit = SubmitField('Update Status')