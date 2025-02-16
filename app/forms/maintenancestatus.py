from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, SelectField, StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from app.models import CompanyUser, Workshop

class MaintenanceStatusForm(FlaskForm):
    status = SelectField('Status', validators=[DataRequired()],
                        choices=[
                            ('received', 'Receive'),
                            ('sended', 'Send'),
                            ('pending', 'Pending'),
                            ('in_progress', 'Repairing'),
                            ('completed', 'Completed'),
                            ('closed', 'Closed'),
                            ('cancelled', 'Cancel Maintenance')
                        ])
    #is_external = BooleanField('External' , default=False)
    
    notes = TextAreaField('Notes')
    workshop_id = SelectField('Workshop', 
        choices=[], 
        coerce=int,
        validators=[DataRequired()])
    company_id = SelectField('Company', 
        choices=[], 
        coerce=int,
        validators=[DataRequired()])
  
    
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(MaintenanceStatusForm, self).__init__(*args, **kwargs)
        # Populate workshop_id if there are workshops
        # Assuming `Workshop` is a model with `id` and `workshopname` attributes
        self.workshop_id.choices = [(w.id, f"{w.workshopname} - {w.building}") 
                                  for w in Workshop.query.all()]
        
        # Populate company_id if there are companies
        # Assuming `Company` is a model with `id` and `name` attributes
        self.company_id.choices = [(c.cid, f"{c.companyname_en} - {c.staffname}") 
                                for c in CompanyUser.query.all()]