from . import main
from .forms import MeetingUpdateForm
from ..models import Project, User, Comment

from app import db
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user


@main.route('/')
def index():
    return redirect(url_for('auth.user_login'))


@main.route('/meeting', methods=['GET', 'POST'])
@login_required
def meeting():
    form = MeetingUpdateForm()
    if request.method == 'POST':
        date_reported = form.date.data
        dat = datetime.strptime(date_reported, '%d-%b-%Y') # put a try and except
        pro = Project.query.filter_by(id=form.project_number.data).first()
        pro.status = form.status.data
        if form.status.data == 'Closed' or 'Finished':
            pro.end_date = dat

        pro.last_edited = datetime.utcnow()
        c = Comment(body=form.comment.data,
                    author=current_user,
                    project=pro,
                    date_reported=date(dat.year, dat.month, dat.day)
                    )
        db.session.add_all([pro, c])
        db.session.commit()
        flash('Updated Project', 'green accent-3')
        return redirect(url_for('main.meeting'))
    form.comment.data = ''
    return render_template('meeting.html', form=form)
