from app.models import Role, Volunteer, Project
from flask_wtf import FlaskForm as Form
from sqlalchemy import or_

from wtforms import (StringField, TextAreaField, SelectField, SubmitField, IntegerField)
from wtforms.validators import DataRequired, Optional, Length


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
