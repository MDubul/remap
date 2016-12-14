from app.models import Project
from flask_wtf import FlaskForm as Form
from sqlalchemy import or_

from wtforms import StringField, TextAreaField, SelectField, SubmitField


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
