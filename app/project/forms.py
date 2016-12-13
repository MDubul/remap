from flask_wtf import FlaskForm as Form
from wtforms import (StringField, DateField, TextAreaField,
                     SelectField, SubmitField, BooleanField,
                     FileField, IntegerField)
from wtforms.validators import Length, DataRequired, Optional
from ..models import Volunteer, Role


class AssignProjectForm(Form):
    vol = SelectField('Volunteer', coerce=int)
    confirmed = BooleanField('Confirmed')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AssignProjectForm, self).__init__(*args, **kwargs)
        self.vol.choices = [(vol.id, vol.name) for vol in Volunteer.query.order_by(Volunteer.name).all()]


class CommentForm(Form):
    date_reported = DateField('Date Reported', format="%Y-%m-%d")
    body = TextAreaField('Message')
    submit = SubmitField('Submit Comment')


class ProjectCompletionForm(Form):
    expensehour = IntegerField('Expense Hours', description='How many hours', validators=[Optional()])
    solution = TextAreaField('Project Solution', validators=[Optional()])
    imageupload = FileField('Your photo', render_kw={'multiple': True})
    caption = StringField('Add Photo caption')
    sure = BooleanField('Confirm', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ProjectCloseForm(Form):
    comment = TextAreaField('Add Reason for Project Closure', validators=[DataRequired()])
    sure = BooleanField('Confirmed', validators=[DataRequired()])
    submit = SubmitField('Submit')

