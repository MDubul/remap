
from flask.ext.wtf import Form
from wtforms import StringField,TextAreaField,SelectField,RadioField,SubmitField,IntegerField, BooleanField,FileField
from wtforms.validators import Required, Optional, Length, Email
from ..models import Role, Volunteer
from flask_wtf.recaptcha import RecaptchaField



class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    role = SelectField('Role', coerce=int)
    postcode = StringField('Postcode')
    address = StringField('Address')
    tel = IntegerField('Telephone')
    mob = IntegerField('Mobile' )
    email = StringField('Email')
    about_me = TextAreaField('About')

    submit = SubmitField('Submit')
    def __init__(self, vol, *args, **kwargs): ## Need to understand this section more
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.vol = vol

    def validate_email(self, field):
        if field.data != self.vol.email and Volunteer.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')



class AssignProjectForm(Form):
    vol = SelectField('Volunteer', coerce=int)
    confirmed = BooleanField('Confirmed')
    submit = SubmitField('Submit')
    def __init__(self, *args, **kwargs): ## Need to understand this section more
        super(AssignProjectForm, self).__init__(*args, **kwargs)
        self.vol.choices = [(vol.id, vol.name) for vol in Volunteer.query.order_by(Volunteer.name).all()]
        #self.vol = vol



class EditProjectForm(Form):
    request_title = StringField('Project Title')
    request_body = TextAreaField('Project Request',  description='Describe your problem', validators=[Required()])
    donation_discussed = BooleanField('Donation/Expenses Discussed?')
    donation_outcome = TextAreaField('Outcome?', validators=[Optional()])
    data_protection = BooleanField('Data Protection Discussed?')
    dat_protection_outcome = TextAreaField('Outcome?', validators=[Optional()])
    submit = SubmitField('Submit')

class ProjectSubmissionForm(Form):
    age_range = RadioField('Age Group:', choices=[('0-17','0-17'),('18-64','18-64'),('65+','65+')],validators=[Required()])
    refered = BooleanField('Was User Refered?')
    name = StringField('User Name*:', validators=[Required()])
    address = StringField('Address*:', validators=[Required()])
    postcode = StringField('Postcode*:', validators=[Required()])
    tel = IntegerField('Telephone:', validators=[Optional()])
    mob = IntegerField('Mobile:', validators=[Optional()])
    email = StringField('Email:', validators=[Optional()])
    initial_contact = StringField('Initial Contact & useful info', default='Direct')
    how_find = TextAreaField('How did the find us?')
    request_title = StringField('Project Title:')
    request_body = TextAreaField('Project Request:', validators=[Required()])
    name2 = StringField('Initiator Name:')
    tel2 = IntegerField('Telephone:', validators=[Optional()])
    mob2 = IntegerField('Mobile:', validators=[Optional()])
    email2 = StringField('Email:', validators=[Optional()])
    relation = StringField('Relationship:', description=' What is the Relationship to Service User')

    donation_discussed = BooleanField('Donation/Expenses Discussed?')
    donation_outcome = TextAreaField('Outcome?', validators=[Optional()])
    data_protection = BooleanField('Data Protection Discussed?')
    dat_protection_outcome = TextAreaField('Outcome?', validators=[Optional()])


    submit = SubmitField('Submit')


class CommentForm(Form):
    body = TextAreaField('Message')
    submit = SubmitField('Submit Comment')



class ProjectCompletionForm(Form):
    expensehour = IntegerField('Expense Hours',description='How many hours',validators=[Optional()])
    solution = TextAreaField('Project Solution', validators=[Optional()])
    imageupload = FileField('Your photo', render_kw={'multiple': True})
    caption = StringField('Add Photo caption')
    sure = BooleanField('Confirm', validators=[Required()])
    submit = SubmitField('Submit')


class ProjectCloseForm(Form):
    comment = TextAreaField('Add Reason for Project Closure', validators=[Required()])
    sure = BooleanField('Confirmed', validators=[Required()])
    submit = SubmitField('Submit')


class ProjectPdfSelection(Form):
    selection = SelectField('Create PDF', choices=[('1','All'), ('2','Ongoing or Awaiting volunteer'), ('3','Awaiting Volunteer'), ('4','Ongoing'), ('5','Finished or Closed'), ('6','Finished'), ('7','Closed')])
    submit = SubmitField('Download PDF')



class AddNewVolunteerForm(Form):
    name = StringField('Name:', validators=[Required()])
    role = SelectField('Role',coerce=int)
    address = StringField('Address:', validators=[Required()])
    postcode = StringField('Postcode:', validators=[Required()])
    tel = IntegerField('Telephone:', validators=[Optional()])
    mob = IntegerField('Mobile:', validators=[Optional()])
    email = StringField('Email:', validators=[Optional()])
    about_me = TextAreaField('About')
    submit = SubmitField('Submit')

    def __init__(self,  *args, **kwargs): ## Need to understand this section more
        super(AddNewVolunteerForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]


    def validate_email(self, field):  #custom validators implemented as methods
        if Volunteer.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')



class PDFEncryptionForm(Form):
    PdfFile = FileField('Your PDF File')
    password = StringField('Enter Password for Encryption:', validators=[Required()])
    submit = SubmitField('Submit')