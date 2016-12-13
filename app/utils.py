
from flask import current_app


def distination_file(number):
    uploadfolder = current_app.config['PROJECT_UPLOAD']
    appex = '/' + str(number)
    return uploadfolder + appex


def solution_destination(number):
    uploadfolder = current_app.config['PROJECT_SOLUTION']
    appex = '/' + str(number)
    return uploadfolder + appex


def allowed_file_name(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

