from . import project
from .forms import (AssignProjectForm, CommentForm, ProjectCompletionForm,
                    ProjectCloseForm, ProjectSubmissionForm, EditProjectForm,
                    ProjectPdfSelection, PDFEncryptionForm)

from ..utils import distination_file, solution_destination, allowed_file_name
from ..project_pdf import make_project_list_pdf, make_detailed_pdf

from ..models import (Project, Volunteer, Comment, SolutionPhotos,
                      User, Referal, ProjectPhoto)

from app import db
from datetime import datetime, date
from geopy.geocoders import GoogleV3
from flask import render_template, request, current_app, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_googlemaps import Map, icons
from werkzeug.utils import secure_filename

import PyPDF2
import os
import errno


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

    return render_template('project/project-single.html',
                           project=project_object, API_KEY=MAP_API_KEY,
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
    return render_template('project/project-assign.html',
                           form=form, project=project_object)


@project.route('/<number>/comments', methods=['GET', 'POST'])
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


@project.route('/comments/<int:id>/', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    pro = Comment.query.filter_by(id=id).first().project_id
    Comment.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Comment deleted.', 'green accent-3')
    return redirect(url_for('project.project_comments', number=pro))


@project.route('/<number>/comments/<int:id>/admin', methods=['GET', 'POST'])
@login_required
def edit_comment_admin(number, id):
    form = CommentForm()
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        comment.body = form.body.data
        comment.last_edited = datetime.utcnow()
        db.session.add(comment)
        db.session.commit()
        flash('The post has been updated.', 'green accent-3')
        return redirect(url_for('project.project_comments', number=number))
    form.body.data = comment.body
    return render_template('project/project-comment-edit.html',
                           form=form,
                           comment=comment,
                           project_number=number,
                           comment_id=id)


@project.route('/<number>/<way>', methods=['GET', 'POST'])
@login_required
def end_project(number, way):
    if way == 'Finish':
        form = ProjectCompletionForm()
        if request.method == 'POST':
            project_object = Project.query.filter_by(id=number).first()
            project_object.status = 'Finished'
            project_object.expense_hours = form.expensehour.data
            project_object.end_date = datetime.utcnow()
            project_object.last_edited = datetime.utcnow()
            project_object.solution = form.solution.data
            uploaded_files = request.files.getlist("imageupload")
            first = True
            for file in uploaded_files:
                if file and allowed_file_name(file.filename):
                    if not os.path.exists(solution_destination(number)):
                        try:
                            os.makedirs(solution_destination(number))
                        except OSError as exc: # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise
                    #app = current_app._get_current_object()
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(solution_destination(number), filename))
                    caption = request.form.getlist('caption')
                    if first:
                        photo = SolutionPhotos(location=os.path.join(solution_destination(number), filename),
                                               caption=caption[0])
                        first = False
                        project_object = Project.query.filter_by(id=number).first()
                        project_object.solutionphotos.append(photo)
                        db.session.add_all([photo, project_object])
                    else:
                        photo = SolutionPhotos(location=os.path.join(solution_destination(number), filename))
                        project_object = Project.query.filter_by(id=number).first()
                        project_object.solutionphotos.append(photo)
                        db.session.add_all([photo, project_object])
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now finished.', 'green accent-3')
            return redirect(url_for('project.project_single', number=number))
        return render_template('project/project-end-finish.html',
                               form=form,
                               way=way,
                               number=number)
    elif way == 'Close':
        form = ProjectCloseForm()
        if request.method == 'POST':
            project_object = Project.query.filter_by(id=number).first()
            project_object.last_edited = datetime.utcnow()
            project_object.status = 'Closed'
            project_object.end_date = datetime.utcnow()
            comment = Comment(body=form.comment.data, author=current_user)
            project_object.comments.append(comment)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now Closed.', 'green accent-3')
            return redirect(url_for('project.project_single', number=number))
        return render_template('project/project-end-close.html',
                               form=form,
                               way=way,
                               number=number)
    else:
        abort(404)


@project.route('/<number>/solution', methods=['GET', 'POST'])
@login_required
def project_solution(number):
    project_object = Project.query.filter_by(id=number).first()
    if project_object.status == 'Finished':
        pro_folder = solution_destination(number)
        if os.path.exists(pro_folder):
            pro_folder_items = os.listdir(pro_folder)
        else:
            pro_folder_items = None
        return render_template('project/project-solution.html',
                               project=project_object,
                               pro_folder_items=pro_folder_items)
    else:
        abort(404)


@project.route('/submit-project', methods=['GET', 'POST'])
@login_required
def submit_project():
    form = ProjectSubmissionForm()
    if request.method == 'POST':
        strdt = form.date_first_contacted.data
        dat = datetime.strptime(strdt, '%d-%b-%Y')
        user_object = User(age_range=form.age_range.data,
                           name=form.name.data,
                           address_line_1=form.address_line_1.data,
                           address_line_2=form.address_line_2.data,
                           organisation_name=form.organisation_name.data,
                           town_city=form.town_city.data,
                           postcode=form.postcode.data,
                           telephone=form.telephone.data,
                           mobile=form.mobile.data,
                           email=form.email.data,
                           service_user_condition=form.service_user_condition.data,
                           initial_contact=form.initial_contact.data,
                           relation=form.relation.data,
                           how_they_find_us=form.how_they_find_us.data)
        db.session.add(user_object)
        if form.refered.data:
            user_object_2 = User(name=form.name_2.data,
                                 address_line_1=form.address_line_1_2.data,
                                 address_line_2=form.address_line_2_2.data,
                                 organisation_name=form.organisation_name_2.data,
                                 town_city=form.town_city_2.data,
                                 postcode=form.postcode_2.data,
                                 telephone=form.telephone_2.data,
                                 mobile=form.mobile_2.data,
                                 email=form.email_2.data)
            db.session.add(user_object_2)
            ref = Referal(referee=user_object_2, referenced=user_object)
            db.session.add(ref)
        project_object = Project(request_title=form.request_title.data,
                                 request_body=form.request_body.data,
                                 Donation_discussed=form.donation_discussed.data,
                                 whom_donation_discussed=form.whom_donation_discussed.data,
                                 donation_outcome=form.donation_outcome.data,
                                 data_protection=form.data_protection.data,
                                 whom_data_protection_discussed=form.whom_data_protection_discussed.data,
                                 dat_protection_outcome=form.dat_protection_outcome.data,
                                 date_first_contacted=date(dat.year, dat.month, dat.day))
        project_object.user.append(user_object)
        db.session.add(project_object)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        flash('Project has been submitted.', 'green accent-3')
        return redirect(url_for('project.projects'))
    return render_template('project/project-submit.html', form=form)


@project.route('/edit-project/<number>', methods=['GET', 'POST'])
@login_required
def edit_project(number):
    project_object = Project.query.filter_by(id=number).first()
    form = EditProjectForm()
    if request.method == 'POST':
        project_object.request_title = form.request_title.data
        project_object.request_body = form.request_body.data
        project_object.Donation_discussed = form.donation_discussed.data
        project_object.donation_outcome = form.donation_outcome.data
        project_object.data_protection = form.data_protection.data
        project_object.dat_protection_outcome = form.dat_protection_outcome.data
        project_object.whom_donation_discussed = form.whom_donation_discussed.data
        project_object.whom_data_protection_discussed = form.whom_data_protection_discussed.data
        project_object.last_edited = datetime.utcnow()
        db.session.add(project_object)
        db.session.commit()
        flash('Project has been edited', 'green accent-3')
        return redirect(url_for('project.project_single', number=project_object.id))
    form.request_title.data = project_object.request_title
    form.request_body.data = project_object.request_body
    form.donation_discussed.data = project_object.Donation_discussed
    form.donation_outcome.data = project_object.donation_outcome
    form.data_protection.data = project_object.data_protection
    form.dat_protection_outcome.data = project_object.dat_protection_outcome
    form.whom_donation_discussed.data = project_object.whom_donation_discussed
    form.whom_data_protection_discussed.data = project_object.whom_data_protection_discussed
    return render_template('project/project-edit.html', form=form, project=project_object)


@project.route('/<number>/photos', methods=['GET', 'POST'])
@login_required
def project_photos(number):
    if request.method == 'POST':
        uploaded_files = request.files.getlist("filesToUpload[]")
        for file in uploaded_files:
            if file and allowed_file_name(file.filename):
                if not os.path.exists(distination_file(number)):
                    try:
                        os.makedirs(distination_file(number))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                #app = current_app._get_current_object()
                filename = secure_filename(file.filename)
                file.save(os.path.join(distination_file(number), filename))
                caption = request.form.getlist('cappy')
                photo_object = ProjectPhoto(location=os.path.join(distination_file(number), filename),
                                            caption=caption[0])
                project_object = Project.query.filter_by(id=number).first()
                project_object.photos.append(photo_object)
                project_object.last_edited = datetime.utcnow()
                db.session.add_all([photo_object, project_object])
        db.session.commit()
        flash('Your photos has been uploaded', 'green accent-3')
        return redirect(url_for('project.project_single', number=number))
    return render_template('project/project-photo.html', number=number)


@project.route('/pdf', methods=['GET', 'POST'])
@login_required
def pdf_page():
    form = ProjectPdfSelection()
    if request.method == 'POST':
        return redirect(url_for('project.pdf', respon=form.selection.data))
    return render_template('project/project-list-make-PDF.html', form=form)


@project.route('/pdf/list/<respon>')
@login_required
def pdf(respon):
    make_project_list_pdf(respon)
    flash('PDF is being made in the background', 'green accent-3')
    return redirect(url_for('main.index'))


@project.route('/pdf/single/<number>')
@login_required
def detailed_pdf(number):
    make_detailed_pdf(number)
    flash('PDF is being made in the background', 'green accent-3')
    return redirect(url_for('main.index'))


@project.route('/pdf/encrypt/', methods=['GET', 'POST'])
@login_required
def encrypt_pdf():
    form = PDFEncryptionForm()
    if request.method == 'POST':
        filename = request.files['PdfFile'].filename
        password = form.password.data

        with open(filename, 'rb') as pdfFile:
            pdf_reader = PyPDF2.PdfFileReader(pdfFile)
            pdf_writer = PyPDF2.PdfFileWriter()
            for pageNum in range(pdf_reader.numPages):
                pdf_writer.addPage(pdf_reader.getPage(pageNum))
            pdf_writer.encrypt(password)
            result_pdf = open('E-'+filename, 'wb')
            pdf_writer.write(result_pdf)
            result_pdf.close()
            flash('PDF is being made in the background', 'green accent-3')
            return redirect(url_for('main.index'))
    return render_template('project/project-encrypt-pdf.html', form=form)


@project.route('/pdf/summery/<number>')
@login_required
def summery_pdf(number):
    #make_detailed_pdf(number)
    return redirect(url_for('main.index'))