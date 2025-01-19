from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.models import CompanyUser

class CompanyUserForm(FlaskForm):
    
    staffname = StringField('Staff Name', validators=[
        DataRequired(message="Staff name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    companyname_en = StringField('Company Name (English)', validators=[
        DataRequired(message="Company name in English is required"),
        Length(min=2, max=100, message="Company name must be between 2 and 100 characters")
    ])
    
    companyname_ar = StringField('اسم الشركة (Arabic)', validators=[
        DataRequired(message="Company name in Arabic is required"),
        Length(min=2, max=100, message="Company name must be between 2 and 100 characters")
    ])
    
    contactnumber = TelField('Contact Number', validators=[
        DataRequired(message="Contact number is required")
    ])
    
    submit = SubmitField('Save Company')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(CompanyUserForm, self).__init__(*args, **kwargs)

    # def validate_companyname_en(self, field):
    #     if self.company and self.company.companyname_en == field.data:
    #         print("Company name already registered .... please")
    #         return
    #     else:
    #         print("Company name already not registered .... please")
    #         raise ValidationError('This company name is already registered.')

class CompanySearchForm(FlaskForm):
    search = StringField('Search', validators=[Length(max=100)])
    submit = SubmitField('Search') 