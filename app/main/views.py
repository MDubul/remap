import os
import errno

from flask import (render_template, redirect, url_for, flash, abort, request,
                   current_app)

from . import main
from flask_login import login_required, current_user

from .forms import (EditProfileForm, EditProjectForm, ProjectSubmissionForm,
                    ProjectCompletionForm, ProjectCloseForm, ProjectPdfSelection,
                    AddNewVolunteerForm, PDFEncryptionForm, MeetingUpdateForm)

from app import db
from app.models import (Project, User, Volunteer, Role, Comment, ProjectPhoto, Referal,
                        SolutionPhotos)

from ..utils import distination_file, solution_destination, allowed_file_name

from werkzeug.utils import secure_filename
from datetime import datetime, date
from app.project_pdf import make_project_list_pdf, make_detailed_pdf
import PyPDF2


@main.route('/')
def index():
    return redirect(url_for('auth.user_login'))




##################################################################################
#                                    PROFILE
##################################################################################
@main.route('/profiles') # about us page
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
    return render_template('profiles.html',
                           vol=vol,
                           pagination=pagination,
                           index=index_page)


@main.route('/profile/<name>')
def profile_user(name):
    vol = Volunteer.query.filter_by(name=name).first()
    if vol is None:
        abort(404)
    return render_template('profile-volunteer.html', vol=vol)


@main.route('/profile/new', methods=['GET', 'POST'])
def add_new_volunteer():
    form = AddNewVolunteerForm()
    if request.method == 'POST':
        vol = Volunteer(name=form.name.data,
                        address_line_1=form.address_line_1.data,
                        address_line_2=form.address_line_2.data,
                        town_city= form.town_city.data,
                        postcode=form.postcode.data,
                        email=form.email.data,
                        telephone=form.telephone.data,
                        mobile=form.mobile.data,
                        role_id=form.role.data,
                        volunteer_profile=form.volunteer_profile.data,
                        )
        db.session.add(vol)
        db.session.commit()
        flash('Added a New volunteer.', 'green accent-3')
        return redirect(url_for('main.profile'))
    return render_template('profile-new.html', form=form)


############################ ADMIN PROFILE EDIT   ##############################
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    vol = Volunteer.query.filter_by(id=id).first()
    form = EditProfileForm(vol=vol)
    if request.method == 'POST':
        vol.email = form.email.data
        vol.role = Role.query.get(form.role.data)
        vol.telephone = form.telephone.data
        vol.mobile = form.mobile.data
        vol.address_line_1 = form.address_line_1.data
        vol.address_line_2 = form.address_line_2.data
        vol.town_city = form.town_city.data
        vol.name = form.name.data
        vol.postcode = form.postcode.data
        vol.volunteer_profile = form.volunteer_profile.data
        db.session.add(vol)
        db.session.commit()
        flash('The profile has been updated.', 'green accent-3')
        return redirect(url_for('main.profile', name=vol.name))
    form.email.data = vol.email
    form.name.data = vol.name
    form.address_line_1.data = vol.address_line_1
    form.address_line_2.data = vol.address_line_2
    form.town_city.data = vol.town_city
    form.mobile.data = vol.mobile
    form.telephone.data = vol.telephone
    form.postcode.data = vol.postcode
    form.volunteer_profile.data = vol.volunteer_profile
    return render_template('profile-edit.html', form=form, vol=vol)





########################### ADMIN EDIT COMMENT ################################
@main.route('/project/<number>/comments/<int:id>/admin', methods=['GET', 'POST'])
@login_required
def edit_comment_admin(number, id):
    form = CommentForm()
    comment = Comment.query.get_or_404(id)
    pro_num = number
    com_id = id
    if request.method == 'POST':
        comment.body = form.body.data
        comment.last_edited = datetime.utcnow()
        db.session.add(comment)
        db.session.commit()
        flash('The post has been updated.','green accent-3')
        return redirect(url_for('main.project_comments', number=number))
    form.body.data = comment.body
    return render_template('project-comment-edit.html',
                           form=form,
                           comment=comment,
                           pro_num=pro_num,
                           com_id=com_id)


###############################################################################
#                   Project End
# thread this!!
######################### VOLUNTEER PROJECT END ################################
@main.route('/project/<number>/<way>', methods=['GET','POST'])
@login_required
def end_project(number, way):
    if way == 'Finish':
        form = ProjectCompletionForm()
        if request.method == 'POST':
            pro = Project.query.filter_by(id=number).first()
            pro.status = 'Finished'
            pro.expense_hours = form.expensehour.data
            pro.end_date = datetime.utcnow()
            pro.last_edited = datetime.utcnow()
            pro.solution = form.solution.data
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
                    app = current_app._get_current_object()
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(solution_destination(number), filename))
                    caption = request.form.getlist('caption')
                    if first:
                        p = SolutionPhotos(location=os.path.join(solution_destination(number), filename),
                                           caption=caption[0])
                        first = False
                        pro = Project.query.filter_by(id=number).first()
                        pro.solutionphotos.append(p)
                        db.session.add_all([p, pro])
                    else:
                        p = SolutionPhotos(location=os.path.join(solution_destination(number), filename))
                        pro = Project.query.filter_by(id=number).first()
                        pro.solutionphotos.append(p)
                        db.session.add_all([p, pro])
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now finished.', 'green accent-3')
            return redirect(url_for('main.project_single', number=number))
        return render_template('project-end-finish.html',
                               form=form,
                               way=way,
                               number=number)
    elif way == 'Close':
        form = ProjectCloseForm()
        if request.method == 'POST':
            pro = Project.query.filter_by(id=number).first()
            pro.last_edited = datetime.utcnow()
            pro.status = 'Closed'
            pro.end_date = datetime.utcnow()
            c = Comment(body=form.comment.data, author=current_user)
            pro.comments.append(c)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now Closed.','green accent-3')
            return redirect(url_for('main.project_single', number=number))
        return render_template('project-end-close.html',
                               form=form,
                               way=way,
                               number=number)
    else:
        abort(404)


######################### VOLUNTEER SOLUTION PHOTOS ###########################
@main.route('/project/<number>/solution', methods=['GET', 'POST'])
@login_required
def project_solution(number):
    pro = Project.query.filter_by(id=number).first()
    if pro.status == 'Finished':
        pro_folder = solution_destination(number)
        if os.path.exists(pro_folder):
            pro_folder_items = os.listdir(pro_folder)
        else:
            pro_folder_items = None
        return render_template('project-solution.html',
                               pro=pro,
                               pro_folder_items=pro_folder_items)
    else:
        abort(404)

################################################################################
#                            SUBMIT PROJECT                                   #
################################################################################
@main.route('/submit-project/', methods=['GET', 'POST'])
@login_required
def submit_project():
    form = ProjectSubmissionForm()
    if request.method == 'POST':
        strdt = form.date_first_contacted.data
        dat = datetime.strptime(strdt, '%d-%b-%Y')
        c = User(age_range=form.age_range.data,
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
        db.session.add(c)
        if form.refered.data:
            user2 = User(name=form.name_2.data,
                         address_line_1=form.address_line_1_2.data,
                         address_line_2=form.address_line_2_2.data,
                         organisation_name=form.organisation_name_2.data,
                         town_city=form.town_city_2.data,
                         postcode=form.postcode_2.data,
                         telephone=form.telephone_2.data,
                         mobile=form.mobile_2.data,
                         email=form.email_2.data)
            db.session.add(user2)
            ref = Referal(referee=user2, referenced=c)
            db.session.add(ref)
        proj = Project(request_title=form.request_title.data,
                       request_body = form.request_body.data,
                       Donation_discussed=form.donation_discussed.data,
                       whom_donation_discussed=form.whom_donation_discussed.data,
                       donation_outcome=form.donation_outcome.data,
                       data_protection=form.data_protection.data,
                       whom_data_protection_discussed=form.whom_data_protection_discussed.data,
                       dat_protection_outcome=form.dat_protection_outcome.data,
                       date_first_contacted=date(dat.year, dat.month, dat.day)
                       )
        proj.user.append(c)
        db.session.add(proj)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        flash('Project has been submitted.', 'green accent-3')
        return redirect(url_for('main.projects'))
    return render_template('project-submit.html', form=form)

##################################################################################
#                                    USER
##################################################################################


#######################  ACCESS TO USER INFO VIA ADMIN   ######################
@main.route('/user/<cli_number>/<project_num>/admin')
@login_required
def client_info_admin(cli_number, project_num):
    clie = User.query.filter_by(id=cli_number).first()
    pro = Project.query.filter_by(id=project_num).first()
    try:
        referee = pro.user.first().referee.first().referee
    except AttributeError:
        referee = None
    return render_template('user-info.html', clie=clie, referee=referee )


################    USER PROJECT [PORTAL TO UPLOAD PHOTOS]    ##################

##################  EDITING PROJECT SUBMISSION FOR DIRECT USER  ################

@main.route('/edit-project/<number>', methods=['GET', 'POST'])
@login_required
def edit_project(number):
    pro = Project.query.filter_by(id=number).first()
    form = EditProjectForm()
    if request.method == 'POST':
        pro.request_title = form.request_title.data
        pro.request_body = form.request_body.data
        pro.Donation_discussed = form.donation_discussed.data
        pro.donation_outcome = form.donation_outcome.data
        pro.data_protection = form.data_protection.data
        pro.dat_protection_outcome = form.dat_protection_outcome.data
        pro.whom_donation_discussed = form.whom_donation_discussed.data
        pro.whom_data_protection_discussed = form.whom_data_protection_discussed.data
        pro.last_edited = datetime.utcnow()
        db.session.add(pro)
        db.session.commit()
        flash('Project has been edited', 'green accent-3')
        return redirect(url_for('main.project_single', number=pro.id))
    form.request_title.data = pro.request_title
    form.request_body.data = pro.request_body
    form.donation_discussed.data = pro.Donation_discussed
    form.donation_outcome.data = pro.donation_outcome
    form.data_protection.data = pro.data_protection
    form.dat_protection_outcome.data = pro.dat_protection_outcome
    form.whom_donation_discussed.data = pro.whom_donation_discussed
    form.whom_data_protection_discussed.data = pro.whom_data_protection_discussed
    return render_template('project-edit.html', form=form, pro=pro)


######################## Admin  UPLOAD PROJECT PHOTOS #################################
@main.route('/projects/<number>/photos', methods=['GET', 'POST'])
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
                app = current_app._get_current_object()
                filename = secure_filename(file.filename)
                file.save(os.path.join(distination_file(number), filename))
                caption = request.form.getlist('cappy')
                p = ProjectPhoto(location=os.path.join(distination_file(number), filename), caption=caption[0])
                pro = Project.query.filter_by(id=number).first()
                pro.photos.append(p)
                pro.last_edited = datetime.utcnow()
                db.session.add_all([p, pro])
        db.session.commit()
        flash('Your photos has been uploaded', 'green accent-3')
        return redirect(url_for('main.project_single', number=number))
    return render_template('project-photo.html', number=number)


######################## DELETE PROJECT PHOTOS #################################


@main.route('/project/pdf', methods=['GET', 'POST'])
@login_required
def pdf_page():
    form = ProjectPdfSelection()
    if request.method == 'POST':
        return redirect(url_for('main.pdf', respon=form.selection.data))
    return render_template('project-list-make-PDF.html', form=form)


@main.route('/project/pdf/list/<respon>')
@login_required
def pdf(respon):
    make_project_list_pdf(respon)
    flash('PDF is being made in the background', 'green accent-3')
    return redirect(url_for('main.index'))


@main.route('/project/pdf/single/<number>')
@login_required
def detailed_pdf(number):
    make_detailed_pdf(number)
    flash('PDF is being made in the background', 'green accent-3')
    return redirect(url_for('main.index'))


@main.route('/project/pdf/encrypt/', methods=['GET', 'POST'])
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
    return render_template('project-encrypt-pdf.html', form=form)


@main.route('/project/pdf/summery/<number>')
@login_required
def summery_pdf(number):
    #make_detailed_pdf(number)
    return redirect(url_for('main.index'))


@main.route('/meeting', methods=['GET', 'POST'])
@login_required
def meeting():
    form = MeetingUpdateForm()
    if request.method == 'POST':
        date_reported = form.date.data
        dat = datetime.strptime(date_reported, '%d-%b-%Y') # put a try and except
        pro = Project.query.filter_by(id=form.project_number.data).first()
        pro.status = form.status.data
        pro.last_edited = datetime.utcnow()
        c = Comment(body=form.comment.data,
                    author=current_user,
                    project=pro,
                    date_reported=date(dat.year, dat.month, dat.day)
                    )
        db.session.add_all([pro, c])
        db.session.commit()
        flash('Updated Project', 'green accent-3')
        return redirect(url_for('main.meeting'))
    form.comment.data = ''
    return render_template('meeting.html', form=form)
