from . import profile
from .forms import AddNewVolunteerForm
from ..models import Volunteer

from app import db
from flask import (request, current_app, render_template, abort,
                   flash, redirect, url_for)


@profile.route('/') # about us page
def profile_main():
    page = request.args.get('page', 1, type=int)
    pagination = Volunteer.query.paginate(page,
                                          per_page=current_app.config['VOL_PER_PAGE'],
                                          error_out=False)
    volunteer_object = pagination.items
    if pagination.pages < 2:
        index_page = None
    else:
        index_page = True
    return render_template('profile/profiles.html',
                           volunteers=volunteer_object,
                           pagination=pagination,
                           index=index_page)


@profile.route('/<name>')
def profile_user(name):
    volunteer_object = Volunteer.query.filter_by(name=name).first()
    if volunteer_object is None:
        abort(404)
    return render_template('profile/profile-volunteer.html',
                           volunteer=volunteer_object)


@profile.route('/new', methods=['GET', 'POST'])
def add_new_volunteer():
    form = AddNewVolunteerForm()
    if request.method == 'POST':
        volunteer_object = Volunteer(name=form.name.data,
                                     address_line_1=form.address_line_1.data,
                                     address_line_2=form.address_line_2.data,
                                     town_city=form.town_city.data,
                                     postcode=form.postcode.data,
                                     email=form.email.data,
                                     telephone=form.telephone.data,
                                     mobile=form.mobile.data,
                                     role_id=form.role.data,
                                     volunteer_profile=form.volunteer_profile.data,)
        db.session.add(volunteer_object)
        db.session.commit()
        flash('Added a New volunteer.', 'green accent-3')
        return redirect(url_for('profile.profile_main'))
    return render_template('profile/profile-new.html',
                           form=form)

