from flask import render_template, request, current_app
from . import project
from ..models import Project

from flask_login import login_required


@project.route('/', methods=['GET'])
@login_required
def projects():
    page = request.args.get('page', 1, type=int)
    pagination = Project.query.order_by(Project.id.desc()).paginate(page,
                                                                    per_page=current_app.config['PROJECT_PER_PAGE'],
                                                                    error_out=False)
    pro_all = pagination.items
    if pagination.pages < 2:
        page_index = None
    else:
        page_index = True
    return render_template('project/project-list.html',
                           pro_all=pro_all,
                           pagination=pagination,
                           index=page_index)
