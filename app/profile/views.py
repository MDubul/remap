from . import profile
from ..models import Volunteer

from flask import request, current_app, render_template


@profile.route('/') # about us page
def profile():
    page = request.args.get('page', 1, type=int)
    pagination = Volunteer.query.paginate(page,
                                          per_page=current_app.config['VOL_PER_PAGE'],
                                          error_out=False)
    vol = pagination.items
    if pagination.pages < 2:
        index_page = None
    else:
        index_page = True
    return render_template('profile/profiles.html',
                           vol=vol,
                           pagination=pagination,
                           index=index_page)