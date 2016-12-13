import os
from flask import render_template, request, current_app
from . import project
from ..models import Project
from ..utils import distination_file

from flask_login import login_required, current_user
from geopy.geocoders import GoogleV3

from flask_googlemaps import Map, icons


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
