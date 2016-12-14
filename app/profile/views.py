from . import profile
from ..models import Volunteer

from flask import request, current_app, render_template, abort


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
    return render_template('profile/profile-volunteer.html', volunteer=volunteer_object)