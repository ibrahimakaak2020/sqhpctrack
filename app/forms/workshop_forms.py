from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.models import CompanyUser, Workshop

class WorkshopUserForm(FlaskForm):
    
    workshopname = StringField('Workshop Name', validators=[
        DataRequired(message="Workshop Name name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    building = StringField('Building', validators=[
        DataRequired(message="building name is required"),
        Length(min=2, max=100, message="building name must be between 2 and 100 characters")
    ])
    
 
    
    contact= TelField('Contact ', validators=[
        DataRequired(message="Contact  is required")
    ])
    
    submit = SubmitField('Save workshop')

    def __init__(self, *args, **kwargs):
        self.workshop = kwargs.pop('workshop', None)
        super(WorkshopUserForm, self).__init__(*args, **kwargs)

    def validate_companyname_en(self, field):
        if self.workshop and self.workshop.id:
            if self.workshop and self.workshop.workshopname == field.data:
                return
        workshop = Workshop.query.filter_by(workshopname=field.data).first()
        if workshop:
            raise ValidationError('This workshop name is already registered.')

class WorkshopSearchForm(FlaskForm):
    search = StringField('Search', validators=[Length(max=100)])
    submit = SubmitField('Search') 