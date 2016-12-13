
from flask_wtf import FlaskForm as Form
from wtforms import (StringField, TextAreaField, SelectField, RadioField, SubmitField,
                     IntegerField, BooleanField, FileField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional, Length
from app.models import Role, Volunteer, Project
from sqlalchemy import or_


class EditProfileForm(Form):
    name = StringField('Name', validators=[Length(0, 64)])
    role = SelectField('Role', coerce=int)
    postcode = StringField('Postcode')
    address_line_1 = StringField('Address Line 1')
    address_line_2 = StringField('Address Line 2')
    town_city = StringField('Town/City')
    telephone = StringField('Telephone')
    mobile = StringField('Mobile')
    email = StringField('Email')
    volunteer_profile = TextAreaField('Volunteer Profile')
    submit = SubmitField('Submit')

    def __init__(self, vol, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.vol = vol

    def validate_email(self, field):
        if field.data != self.vol.email and Volunteer.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class EditProjectForm(Form):
    request_title = StringField('Project Title')
    request_body = TextAreaField('Project Request',  description='Describe your problem',
                                 validators=[DataRequired()])
    donation_discussed = BooleanField('Donation/Expenses Discussed?')
    whom_donation_discussed = StringField('With whom was Donation/Expenses discussed')
    donation_outcome = TextAreaField('Outcome?', validators=[Optional()])
    data_protection = BooleanField('Data Protection Discussed?')
    whom_data_protection_discussed = StringField('With whom was Data Protection Discussed?')
    dat_protection_outcome = TextAreaField('Outcome?', validators=[Optional()])
    submit = SubmitField('Submit')


class ProjectSubmissionForm(Form):
    age_range = RadioField('Age Group:', choices=[('0-17', '0-17'), ('18-64', '18-64'),
                                                  ('65+', '65+')], validators=[DataRequired()])
    refered = BooleanField('Was User Referred?') # should be referred
    date_first_contacted = StringField('Date First Contacted')
    name = StringField('User Name:', validators=[DataRequired()])
    organisation_name = StringField('Organisation Name') # new field
    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('Address Line 2', validators=[DataRequired()])
    town_city = StringField('Town/City')
    telephone = IntegerField('Telephone')
    mobile = IntegerField('Mobile')
    postcode = StringField('Postcode:', validators=[DataRequired])
    email = StringField('Email:', validators=[Optional()])
    initial_contact = StringField('Initial Contact & useful info', default='Direct')
    service_user_condition = TextAreaField('Service user condition')
    how_they_find_us = TextAreaField('How did they find us?')
    request_title = StringField('Project Title:')
    request_body = TextAreaField('Project Request:', validators=[DataRequired])

    name_2 = StringField('Initiator Name:')
    organisation_name_2 = StringField('Organisation Name') # new field
    address_line_1_2 = StringField('Address Line 1', validators=[DataRequired])
    address_line_2_2 = StringField('Address Line 2', validators=[DataRequired])
    town_city_2 = StringField('Town/City')
    postcode_2 = StringField('Postcode:', validators=[DataRequired])

    telephone_2 = IntegerField('Telephone:', validators=[Optional()])
    mobile_2 = IntegerField('Mobile:', validators=[Optional()])
    email_2 = StringField('Email:', validators=[Optional()])
    relation = StringField('Relationship:', description=' What is the Relationship to Service User')

    donation_discussed = BooleanField('Donation/Expenses Discussed?')
    whom_donation_discussed = StringField('With whom was Donation/Expenses discussed')
    donation_outcome = TextAreaField('Outcome?', validators=[Optional()])

    data_protection = BooleanField('Data Protection Discussed?')
    whom_data_protection_discussed = StringField('With whom was Data Protection Discussed?')
    dat_protection_outcome = TextAreaField('Outcome?', validators=[Optional()])
    submit = SubmitField('Submit')




class ProjectPdfSelection(Form):
    selection = SelectField('Create PDF', choices=[('1', 'All'), ('2', 'Ongoing or Awaiting volunteer'),
                                                   ('3', 'Awaiting Volunteer'), ('4', 'Ongoing'),
                                                   ('5', 'Finished or Closed'), ('6', 'Finished'),
                                                   ('7', 'Closed')])
    submit = SubmitField('Download PDF')


class AddNewVolunteerForm(Form):
    name = StringField('Name:', validators=[DataRequired()])
    role = SelectField('Role', coerce=int)
    address_line_1 = StringField('Address Line 1:', validators=[DataRequired()])
    address_line_2 = StringField('Address Line 2:')
    town_city = StringField('Town/City')
    postcode = StringField('Postcode:', validators=[DataRequired()])
    telephone = IntegerField('Telephone:', validators=[Optional()])
    mobile = IntegerField('Mobile:', validators=[Optional()])
    email = StringField('Email:', validators=[Optional()])
    volunteer_profile = TextAreaField('About')
    submit = SubmitField('Submit')

    def __init__(self,  *args, **kwargs):
        super(AddNewVolunteerForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):  #custom validators implemented as methods
        if Volunteer.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class PDFEncryptionForm(Form):
    PdfFile = FileField('Your PDF File')
    password = StringField('Enter Password for Encryption:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MeetingUpdateForm(Form):

    date = StringField('Date')
    project_number = SelectField('Project Number')
    comment = TextAreaField('Comment')
    status = SelectField('Status', choices=[('Awaiting Volunteer', 'Awaiting Volunteer'), ('Ongoing', 'Ongoing'),
                                            ('Finished', 'Finished'), ('Closed', 'Closed')])
    submit = SubmitField('Submit')

    def __init__(self,  *args, **kwargs):
        super(MeetingUpdateForm, self).__init__(*args, **kwargs)

        self.project_number.choices = [(pro.id, pro.id) for pro in
                                       Project.query.filter(or_(Project.status == "Ongoing",
                                                                Project.status == "Awaiting Volunteer"))]
