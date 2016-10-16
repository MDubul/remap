import os, errno

from flask import render_template, session, redirect, url_for, flash, abort, request, current_app,make_response

from . import main
from flask.ext.login import login_required, current_user

from .forms import EditProfileForm, EditProjectForm, CommentForm, ProjectSubmissionForm, ProjectCompletionForm, ProjectCloseForm, AssignProjectForm,ProjectPdfSelection,AddNewVolunteerForm,PDFEncryptionForm

from .. import db
from ..models import Project, User, Volunteer, Role, People, Comment, ProjectPhoto, Referal, SolutionPhotos

from ..email import send_email

from ..decorators import admin_required , volunteer_required, access_required, user_only

from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3

from werkzeug import secure_filename
from datetime import datetime
from ..project_pdf import make_project_list_pdf, make_detailed_pdf,pdf_encryption
import pdfkit
import PyPDF2
from flask_googlemaps import Map, icons, GoogleMaps


@main.route('/')
def index():
    return redirect(url_for('auth.user_login'))


################################################################################
#                         OUT OF BOX FUNCTIONS
################################################################################
def distination(number):
    uploadfolder = current_app.config['PROJECT_UPLOAD']
    appex = '/'+ str(number)
    return uploadfolder + appex

def solutionDestination(number):
    uploadfolder = current_app.config['PROJECT_SOLUTION']
    appex = '/'+ str(number)
    return uploadfolder + appex

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']



##################################################################################
#                                    PROFILE
##################################################################################
@main.route('/profiles') # about us page
def profile():
    page = request.args.get('page', 1, type=int)
    pagination = Volunteer.query.paginate(page,per_page=current_app.config['VOL_PER_PAGE'],error_out=False)
    vol = pagination.items
    if pagination.pages < 2:
        index = None
    else:
        index = True
    return render_template('profiles.html',vol = vol,
                                           pagination = pagination,
                                           index = index)

@main.route('/profile/<name>')
def profile_user(name):
    vol = Volunteer.query.filter_by(name=name).first()
    if vol is None:
        abort(404)
    return render_template('profile-volunteer.html', vol = vol)


@main.route('/profile/new', methods=['GET','POST'])
def add_new_volunteer():
    form = AddNewVolunteerForm()
    if form.validate_on_submit():
        vol = Volunteer( name=form.name.data,
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
        flash('Added a New volunteer.','green accent-3')
        return redirect(url_for('main.profile'))
    return render_template('profile-new.html',form=form)



############################ ADMIN PROFILE EDIT   ##############################
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    vol = Volunteer.query.filter_by(id=id).first()
    form = EditProfileForm(vol=vol)
    if form.validate_on_submit():
        vol.email = form.email.data
        vol.role = Role.query.get(form.role.data)
        vol.telephone = form.telephone.data
        vol.mobile = form.mobile.data
        vol.address_line_1 = form.address_line_1.data
        vol.address_line_2 = form.address_line_2.data
        vol.town_city  = form.town_city.data
        vol.name = form.name.data
        vol.postcode = form.postcode.data
        vol.volunteer_profile = form.volunteer_profile.data
        db.session.add(vol)
        db.session.commit()
        flash('The profile has been updated.','green accent-3')
        return redirect(url_for('main.profile', name = vol.name))
    form.email.data = vol.email
    form.name.data = vol.name
    form.address_line_1.data = vol.address_line_1
    form.address_line_2.data = vol.address_line_2
    form.town_city.data = vol.town_city
    form.mobile.data = vol.mobile
    form.telephone.data = vol.telephone
    form.postcode.data = vol.postcode
    form.volunteer_profile.data = vol.volunteer_profile
    return render_template('profile-edit.html', form = form, vol=vol)


################################################################################
#                               PROJECT                                        #
################################################################################
@main.route('/projects', methods=['GET'])
@login_required
def projects():
    page= request.args.get('page',1, type=int)
    pagination = Project.query.order_by(Project.timestamp.desc()).paginate(page,per_page=current_app.config['PROJECT_PER_PAGE'], error_out=False)
    pro_all=pagination.items

    if pagination.pages < 2:
        index = None
    else:
        index = True
    return render_template('project-list.html',pro_all=pro_all, pagination=pagination)



###########################  PROJECT SINGLE  ###################################

@main.route('/project/<number>', methods=['GET'])
@login_required
def project_single(number):
    app = current_app._get_current_object()

    geolocator = GoogleV3(api_key=app.config['MAP_KEY'],domain='maps.google.co.uk' )
    proj = Project.query.filter_by(id=number).first()
    #try
    cli_location = geolocator.geocode(proj.user.first().postcode,  timeout=10)
    vol_location = geolocator.geocode(current_user.postcode, timeout=10)
    #except a
    #except (geopy.exc.GeocoderTimedOut, geopy.exc.GeocoderServiceError, geopy.exc.GeocoderQueryError(no postcode)) as e:
    pro_folder = distination(number)

    API_KEY = app.config['BROWSER_KEY']

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
            zoom = 12,
            markers = [
                    {
                    'icon': icons.alpha.V,
                    'lat':vol_location.latitude,
                    'lng':vol_location.longitude,
                    'infobox': 'Your Location',
                    },
                    {
                    'icon': icons.alpha.C,
                    'lat':cli_location.latitude,
                    'lng':cli_location.longitude,
                    'infobox': 'User Location',
                    }
                 ]

                )

    return render_template('project-single.html', proj=proj, API_KEY=API_KEY,
                                                   pro_folder_items=pro_folder_items,
                                                   the_map=the_map)



###########################  Assign project to volunteer4  ##########################
@main.route('/take_project/<number>', methods=['GET','POST'])
@login_required
def take_project(number):
   form = AssignProjectForm()
   pro = Project.query.filter_by(id=number).first()
   if form.validate_on_submit():

       vol = Volunteer.query.filter_by(id=form.vol.data).first()
       pro.volunteer.append(vol)
       pro.status = 'Ongoing'
       db.session.add_all([pro,vol])
       db.session.commit()
       flash('Volunteer has been assigned.','green accent-3')
       return redirect(url_for('main.project_single', number=number))
   return render_template('project-assign.html', form = form, pro=pro)

################################################################################
#                            PROJECT COMMENTS                                  #
################################################################################
@main.route('/project/<number>/comments', methods=['GET','POST'])
@login_required
def project_comments(number):
    form = CommentForm()
    vol = current_user
    project = Project.query.get_or_404(number)
    commentlist = project.comments.all()
    if form.validate_on_submit():
        c = Comment(body=form.body.data,
                    author=current_user._get_current_object(),
                    project=project)
        db.session.add(c)
        db.session.commit()
        flash('Your comment has been published.', 'green accent-3')
        return redirect(url_for('main.project_comments', number = project.id))
    return render_template('project-comment.html', form = form,
                                                   vol= vol,
                                                   commentlist = commentlist,
                                                   project = project)

###########################  EDITING COMMENT   #################################

###########################  DELETE COMMENT  ###################################
@main.route('/project/comments/<int:id>/', methods=['GET','POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    pro = comment.project_id
    comment = Comment.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Comment deleted.', 'green accent-3')
    return redirect(url_for('main.project_comments', number=pro))


########################### ADMIN EDIT COMMENT ################################
@main.route('/project/<number>/comments/<int:id>/admin', methods=['GET','POST'])
@login_required
def edit_comment_admin(number, id):
    form = CommentForm()
    comment = Comment.query.get_or_404(id)
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('The post has been updated.','green accent-3')
        return redirect(url_for('main.project_comments', number = number))
    form.body.data = comment.body
    return render_template('project-comment-edit.html', form = form,
                                                        comment = comment)

###############################################################################
#                   Project End
# thread this!!
######################### VOLUNTEER PROJECT END ################################
@main.route('/project/<number>/<way>', methods=['GET','POST'])
@login_required
def end_project(number, way):
    if way == 'Finish':
        form = ProjectCompletionForm()
        if form.validate_on_submit():
            pro = Project.query.filter_by(id=number).first()
            pro.status = 'Finished'
            pro.expense_hours = form.expensehour.data
            pro.end_date = datetime.utcnow()
            pro.solution = form.solution.data
            uploaded_files = request.files.getlist("imageupload")
            first = True
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    if not os.path.exists(solutionDestination(number)):
                        try:
                            os.makedirs(solutionDestination(number))
                        except OSError as exc: # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise
                    app = current_app._get_current_object()
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(solutionDestination(number), filename))
                    caption = request.form.getlist('caption')
                    if first:
                        p = SolutionPhotos(location=os.path.join(solutionDestination(number), filename), caption=caption[0])
                        first = False
                        pro = Project.query.filter_by(id=number).first()
                        pro.solutionphotos.append(p)
                        db.session.add_all([p,pro])
                    else:
                        p = SolutionPhotos(location=os.path.join(solutionDestination(number), filename))
                        pro = Project.query.filter_by(id=number).first()
                        pro.solutionphotos.append(p)
                        db.session.add_all([p,pro])
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now finished.','green accent-3')
            return redirect(url_for('main.project_single', number = number))
        return render_template('project-end-finish.html', form=form, way=way)

    elif way == 'Close':
        form = ProjectCloseForm()
        if form.validate_on_submit():
            pro = Project.query.filter_by(id=number).first()
            pro.status = 'Closed'
            pro.end_date = datetime.utcnow()
            c = Comment(body= form.comment.data, author=current_user)
            pro.comments.append(c)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            flash('Project is now Closed.','green accent-3')
            return redirect(url_for('main.project_single', number = number))
        return render_template('project-end-close.html', form=form, way=way)

    else:
        abort(404)

######################### VOLUNTEER SOLUTION PHOTOS ###########################
@main.route('/project/<number>/solution', methods=['GET','POST'])
@login_required
def project_solution(number):
    pro = Project.query.filter_by(id=number).first()
    if pro.status == 'Finished':
        pro_folder = solutionDestination(number)
        if os.path.exists(pro_folder):
            pro_folder_items = os.listdir(pro_folder)
        else:
            pro_folder_items = None
        return render_template('project-solution.html', pro=pro,
                                                        pro_folder_items=pro_folder_items)
    else:
        abort(404)

################################################################################
#                            SUBMIT PROJECT                                   #
################################################################################
@main.route('/submit-project/', methods=['GET','POST'])
@login_required
def submit_project():
    form = ProjectSubmissionForm()
    if form.validate_on_submit():
        c = User(age_range=form.age_range.data,
                 name=form.name.data,
                 address_line_1=form.address_line_1.data,
                 address_line_2 =form.address_line_2.data,
                 town_city = form.town_city.data,
                 postcode=form.postcode.data,
                 telephone=form.tel.data,
                 mobile = form.mob.data,
                 email=form.email.data,
                 initial_contact=form.initial_contact.data,
                 relation=form.relation.data,
                 how_they_find_us=form.how_they_find_us.data)
        db.session.add(c)
        if form.refered.data:
            user2 = User(name=form.name_2.data,
                        telephone=form.telephone_2.data,
                        mobile = form.mobile_2.data,
                        email=form.email_2.data)
            db.session.add(user2)
            ref = Referal(referee=user2, referenced=c)
            db.session.add(ref)

        proj = Project(request_title=form.request_title.data,
                       request_body = form.request_body.data,
                       Donation_discussed=form.donation_discussed.data,
                       donation_outcome=form.donation_outcome.data,
                       data_protection=form.data_protection.data,
                       dat_protection_outcome=form.dat_protection_outcome.data,)
        proj.user.append(c)
        db.session.add(proj)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        flash('Project has been submitted.','green accent-3')
        return redirect(url_for('main.user_profile'))
    return render_template('project-submit.html', form = form)

##################################################################################
#                                    USER
##################################################################################


#######################  ACCESS TO USER INFO VIA ADMIN   ######################
@main.route('/user/<cli_number>/<project_num>/admin')
@login_required
def client_info_admin(cli_number,project_num):
    clie = User.query.filter_by(id=cli_number).first()
    pro= Project.query.filter_by(id=project_num).first()
    try:
        referee = pro.user.first().referee.first().referee
    except AttributeError:
        referee = None
    return render_template('user-info.html', clie=clie,referee=referee )


################    USER PROJECT [PORTAL TO UPLOAD PHOTOS]    ##################

##################  EDITING PROJECT SUBMISSION FOR DIRECT USER  ################

@main.route('/edit-project/<number>', methods=['GET','POST'])
@login_required
def edit_project(number):
    pro = Project.query.filter_by(id=number).first()
    form = EditProjectForm()
    if form.validate_on_submit():
        pro.request_title = form.request_title.data
        pro.request_body = form.request_body.data
        pro.Donation_discussed=form.donation_discussed.data,
        pro.donation_outcome=form.donation_outcome.data,
        pro.data_protection=form.data_protection.data,
        pro.dat_protection_outcome=form.dat_protection_outcome.data
        flash('Project has been edited','green accent-3')
        return redirect(url_for('main.project_single', number=pro.id))
    form.request_title.data = pro.request_title
    form.request_body.data = pro.request_body
    form.donation_discussed.data=pro.Donation_discussed
    form.donation_outcome.data =pro.donation_outcome
    form.data_protection.data =pro.data_protection
    form.dat_protection_outcome.data = pro.dat_protection_outcome
    return render_template('project-edit.html', form=form, pro=pro)


######################## Admin  UPLOAD PROJECT PHOTOS #################################
@main.route('/projects/<number>/photos', methods=['GET','POST'])
@login_required
def project_photos(number):
    if request.method == 'POST':
        uploaded_files = request.files.getlist("filesToUpload[]")
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                if not os.path.exists(distination(number)):
                    try:
                        os.makedirs(distination(number))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                app = current_app._get_current_object()
                filename = secure_filename(file.filename)
                file.save(os.path.join(distination(number), filename))
                caption = request.form.getlist('cappy')
                p = ProjectPhoto(location=os.path.join(distination(number), filename), caption=caption[0])
                pro = Project.query.filter_by(id=number).first()
                pro.photos.append(p)
                db.session.add_all([p,pro])
        db.session.commit()
        flash('Your photos has been uploaded', 'green accent-3')
        return redirect(url_for('main.project_single',number = number))
    return render_template('project-photo.html')


######################## DELETE PROJECT PHOTOS #################################



@main.route('/project/pdf', methods=['GET','POST'])
@login_required
def pdf_page():
    form = ProjectPdfSelection()
    if request.method == 'POST':
        return redirect(url_for('main.pdf',respon=form.selection.data))
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

@main.route('/project/pdf/encrypt/', methods=['GET','POST'])
@login_required
def encrypt_pdf():
    form = PDFEncryptionForm()
    if request.method == 'POST':
        filename = request.files['PdfFile'].filename
        password = form.password.data

        with open(filename,'rb') as pdfFile:
            pdfReader = PyPDF2.PdfFileReader(pdfFile)
            pdfWriter = PyPDF2.PdfFileWriter()
            for pageNum in range(pdfReader.numPages):
                pdfWriter.addPage(pdfReader.getPage(pageNum))
            pdfWriter.encrypt(password)
            resultPdf = open('E-'+filename, 'wb')
            pdfWriter.write(resultPdf)
            resultPdf.close()
            flash('PDF is being made in the background', 'green accent-3')
            return redirect(url_for('main.index'))
    return render_template('project-encrypt-pdf.html', form=form)


@main.route('/project/pdf/summery/<number>')
@login_required
def summery_pdf(number):
    #make_detailed_pdf(number)
    return redirect(url_for('main.index'))
