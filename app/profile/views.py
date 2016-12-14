from . import profile
from .forms import AddNewVolunteerForm, EditProfileForm
from ..models import Volunteer, Role

from app import db
from flask import (request, current_app, render_template, abort,
                   flash, redirect, url_for)

from flask_login import login_required


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


@profile.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    volunteer_object = Volunteer.query.filter_by(id=id).first()
    form = EditProfileForm(vol=volunteer_object)
    if request.method == 'POST':
        volunteer_object.email = form.email.data
        volunteer_object.role = Role.query.get(form.role.data)
        volunteer_object.telephone = form.telephone.data
        volunteer_object.mobile = form.mobile.data
        volunteer_object.address_line_1 = form.address_line_1.data
        volunteer_object.address_line_2 = form.address_line_2.data
        volunteer_object.town_city = form.town_city.data
        volunteer_object.name = form.name.data
        volunteer_object.postcode = form.postcode.data
        volunteer_object.volunteer_profile = form.volunteer_profile.data
        db.session.add(volunteer_object)
        db.session.commit()  # put try except here
        flash('The profile has been updated.', 'green accent-3')
        return redirect(url_for('profile.profile_main', name=volunteer_object.name))
    form.email.data = volunteer_object.email
    form.name.data = volunteer_object.name
    form.address_line_1.data = volunteer_object.address_line_1
    form.address_line_2.data = volunteer_object.address_line_2
    form.town_city.data = volunteer_object.town_city
    form.mobile.data = volunteer_object.mobile
    form.telephone.data = volunteer_object.telephone
    form.postcode.data = volunteer_object.postcode
    form.volunteer_profile.data = volunteer_object.volunteer_profile
    return render_template('profile/profile-edit.html', form=form, volunteer=volunteer_object)
