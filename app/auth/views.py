from . import auth
from .forms import LoginForm
from ..models import Volunteer

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from flask_login import current_user


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.user_login'))


@auth.route('/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Volunteer.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            return redirect(request.args.get('next') or url_for('project.projects'))
        flash('Invalid username or password.', 'red')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'green accent-3')
    return redirect(url_for('main.index'))
