from ..models import Role

from flask_wtf import FlaskForm as Form

from wtforms import (StringField, TextAreaField, SelectField, SubmitField, IntegerField)
from wtforms.validators import DataRequired, Optional


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
