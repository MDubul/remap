from . import project
from ..utils import distination_file

import os
from datetime import datetime, date

from app import db

from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_googlemaps import Map, icons
from geopy.geocoders import GoogleV3

from ..models import Project, Volunteer, Comment

from .forms import AssignProjectForm, CommentForm


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


@project.route('/<number>', methods=['GET'])
@login_required
def project_single(number):
    app = current_app._get_current_object()

    geolocator = GoogleV3(api_key=app.config['MAP_KEY'], domain='maps.google.co.uk' )
    project_object = Project.query.filter_by(id=number).first()
    try:
        cli_location = geolocator.geocode(project_object.user.first().postcode,  timeout=10)
        vol_location = geolocator.geocode(current_user.postcode, timeout=10)
    except Exception as e:
        cli_location = None
        vol_location = None
        print(str(e))

    pro_folder = distination_file(number)

    MAP_API_KEY = app.config['BROWSER_KEY']

    if os.path.exists(pro_folder):
        pro_folder_items = os.listdir(pro_folder)
    else:
        pro_folder_items = None

    the_map = Map(
            identifier="the_map",
            varname="the_map",
            lat=vol_location.latitude,
            lng=vol_location.longitude,
            collapsible=True,
            style='height:400px;width:800px;margin:50;',
            zoom=12,
            markers=[
                    {
                        'icon': icons.alpha.V,
                        'lat': vol_location.latitude,
                        'lng': vol_location.longitude,
                        'infobox': 'Your Location',
                    },
                    {
                        'icon': icons.alpha.C,
                        'lat': cli_location.latitude,
                        'lng': cli_location.longitude,
                        'infobox': 'User Location',
                    }
                 ]

                )

    return render_template('project/project-single.html', project=project_object, API_KEY=MAP_API_KEY,
                           pro_folder_items=pro_folder_items, the_map=the_map)


@project.route('/take_project/<number>', methods=['GET', 'POST'])
@login_required
def take_project(number):
    form = AssignProjectForm()
    project_object = Project.query.filter_by(id=number).first()
    if request.method == 'POST':
        vol = Volunteer.query.filter_by(id=form.vol.data).first()
        project_object.volunteer.append(vol)
        project_object.last_edited = datetime.utcnow()
        project_object.status = 'Ongoing'
        db.session.add_all([project_object, vol])
        db.session.commit()
        flash('Volunteer has been assigned.', 'green accent-3')
        return redirect(url_for('project.project_single', number=number))
    return render_template('project/project-assign.html', form=form, project=project_object)


@project.route('/project/<number>/comments', methods=['GET', 'POST'])
@login_required
def project_comments(number):
    form = CommentForm()
    project_object = Project.query.get_or_404(number)
    comment_list = project_object.comments.all()
    if request.method == 'POST':
        dt = form.date_reported.data
        c = Comment(body=form.body.data,
                    author=current_user._get_current_object(),
                    project=project_object,
                    date_reported=date(dt.year, dt.month, dt.day))
        db.session.add(c)
        db.session.commit()
        flash('Your comment has been published.', 'green accent-3')
        return redirect(url_for('project.project_comments', number=project_object.id))
    return render_template('project/project-comment.html',
                           form=form,
                           comment_list=comment_list,
                           project=project_object)
