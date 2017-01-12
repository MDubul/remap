from .models import Project, User
from datetime import datetime
from flask import render_template, current_app
from sqlalchemy import or_
from threading import Thread

import pdfkit
import random


def config_wkthmltopdf():
    app = current_app._get_current_object()
    path_wkthmltopdf = app.config['PATH_WKTHMLTOPDF']
    return pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)


def get_time_date():
    now = datetime.utcnow()
    year = now.year
    month = now.month
    day = now.day
    rand = random.randint(0, 100)
    return year, month, day, rand


def make_async_pdf(template, app, prefix):
    with app.app_context():
        year, month, day, rand = get_time_date()
        filename = '{}-({}-{}-{})-{}.pdf'.format(prefix, day, month, year, rand)
        print('making PDF + ', filename)
        pdfkit.from_string(template, filename, configuration=config_wkthmltopdf())


def prepare_pdf_for_list(prefix, pro):
        app = current_app._get_current_object()
        date_now = datetime.utcnow()
        date = date_now.strftime('%d-%b-%Y')
        template = render_template('project-list-pdf.html', pro_all=pro, date=date)
        thr = Thread(target=make_async_pdf, args=[template, app, prefix])
        thr.start()


def prepare_pdf_for_detailed(prefix, pro, cli, referee):
        app = current_app._get_current_object()
        #logo = current_app.config['LOGO']
        template = render_template('project-detailed-pdf.html',
                                   pro=pro,
                                   cli=cli,
                                   referee=referee,
                                   now=datetime.utcnow(),
                                   )

        thr = Thread(target=make_async_pdf, args=[template, app, prefix])
        thr.start()


def make_project_list_pdf(selection):

    if selection == '1':
        prefix = 'All-Project'
        pro_all = Project.query.all()
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '2':
        prefix = 'Ongoing-Awaiting'
        pro_all = Project.query.filter(or_(Project.status == "Ongoing",
                                           Project.status == "Awaiting Volunteer"))
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '3':
        prefix = "Awaiting Volunteer"
        pro_all = Project.query.filter_by(status='Awaiting Volunteer')
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '4':
        prefix = "Ongoing"
        pro_all = Project.query.filter_by(status='Ongoing')
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '5':
        prefix = "Finished-Closed"
        pro_all = Project.query.filter(or_(Project.status == "Finished",
                                           Project.status == "Closed"))
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '6':
        prefix = "Finished"
        pro_all = Project.query.filter_by(status='Finished')
        prepare_pdf_for_list(prefix, pro_all)

    if selection == '7':
        prefix = "Closed"
        pro_all = Project.query.filter_by(status='Closed')
        prepare_pdf_for_list(prefix, pro_all)


def make_detailed_pdf(number):

    prefix = 'Project Number-' + number
    pro = Project.query.filter_by(id=number).first()
    cli_num = pro.user.first().id
    cli = User.query.filter_by(id=cli_num).first()
    try:
        referee = pro.user.first().referee.first().referee
    except AttributeError:
        referee = None
    prepare_pdf_for_detailed(prefix, pro, cli, referee)




#line 40
#try:
    #self.wkhtmltopdf = self.configuration.wkhtmltopdf.decode('utf-8')
#except AttributeError:
    #self.wkhtmltopdf = self.configuration.wkhtmltopdf
