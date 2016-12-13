from . import main

from flask import render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user

from .forms import (EditProfileForm, ProjectPdfSelection, AddNewVolunteerForm,
                    PDFEncryptionForm, MeetingUpdateForm)
from ..models import Project, User, Volunteer, Role, Comment
from ..project_pdf import make_project_list_pdf, make_detailed_pdf

from app import db

from datetime import datetime, date
import PyPDF2


@main.route('/')
def index():
    return redirect(url_for('auth.user_login'))


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
                        town_city=form.town_city.data,
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
