from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField, DateTimeField, BooleanField, SelectField, FloatField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

from app.models import CompanyUser as Company, Equipment, User, Workshop

class MaintenanceRecordForm(FlaskForm):
    #maintenance_date = DateTimeField('Maintenance Date', default=datetime.utcnow, validators=[Optional()])
    # workshop_id = SelectField('Workshop', 
    #     choices=[], 
    #     coerce=int,
    #     validators=[DataRequired()])
    # company_id = SelectField('Company', 
    #     choices=[], 
    #     coerce=int,
    #     validators=[DataRequired()])
    #registered_by = SelectField('Registered By', coerce=int, validators=[DataRequired()])
  
    problem_description = TextAreaField('Problem Description', validators=[DataRequired()])
    
    # Add a submit button if you want to include it in the form
    submit = SubmitField('Submit')

    # Initialize choices for SelectFields, can be used to fetch choices dynamically
    def __init__(self, *args, **kwargs):
        super(MaintenanceRecordForm, self).__init__(*args, **kwargs)
        
        # Example: Populate equipment_sn with available equipment from the database
        # Assuming `Equipment` is a model with `sn` and `id` attributes
        #self.equipment_sn.choices = [(equipment.sn, equipment.sn) for equipment in Equipment.query.all()]
        
        # Populate registered_by with users' staffno and name
        # Assuming `User` is a model with `staffno` and `staffname` attributes
        #self.registered_by.choices = [(user.staffno, user.staffname) for user in User.query.all()]
        
        # Populate workshop_id if there are workshops
        # Assuming `Workshop` is a model with `id` and `workshopname` attributes
        #self.workshop_id.choices = [(w.id, f"{w.workshopname} - {w.building}") 
                                  #for w in Workshop.query.all()]
        
        # Populate company_id if there are companies
        # Assuming `Company` is a model with `id` and `name` attributes
        #self.company_id.choices = [(c.cid, f"{c.companyname_en} - {c.staffname}") 
                                # for c in Company.query.all()]
