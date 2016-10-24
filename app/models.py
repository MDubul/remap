from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from . import db
import hashlib

class Permission:
        BASE = 0x01
        READ = 0x02
        SUBMIT = 0x03
        PERMX = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default= db.Column(db.Boolean,default=False, index=True)
    permissions = db.Column(db.Integer)
    assigned_user = db.relationship('People', backref='role', lazy='dynamic')
    @staticmethod
    def insert_roles():
        roles = {
                'People' :(0, False),
                'User':(Permission.BASE, False),
                'Volunteer':(Permission.READ,False),
                'Engineer': (Permission.READ | Permission.SUBMIT,False),
                'Admin': (0xff,False)
                }
        for r in roles :
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


volPro = db.Table('Volunteer Project Association',
    db.Column('volunteers_id', db.Integer,db.ForeignKey('volunteers.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')))

##start and end date ###
cliPro = db.Table('User Project Association',
    db.Column('user_id', db.Integer,db.ForeignKey('users.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')))

class People(UserMixin, db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity':'people','polymorphic_on':type}
    name = db.Column(db.String(64))
    postcode = db.Column(db.String(64))
    address_line_1 =db.Column(db.String(64))
    address_line_2 = db.Column(db.String(64))
    town_city = db.Column(db.String(64))
    telephone = db.Column(db.Integer)
    mobile= db.Column(db.Integer)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(People,self).__init__(**kwargs)

        if (self.type == 'volunteers') and (self.role is None):
            if self.email == current_app.config['REMAP_ADMIN'] or self.email == current_app.config['REMAP_ADMIN2']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.confirmed = True


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions
    def is_admin(self):
        return self.can(Permission.PERMX)
    def change_email(self, token):
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
        url=url, hash=hash, size=size, default=default, rating=rating)

    def delete_users(id):
        k = People.query.filter_by(role_id=id).all()
        for x in range(len(k)):
            db.session.delete(k[x])
        db.session.commit()


class Volunteer(People):
    __tablename__ = 'volunteers'
    __mapper_args__ = {'polymorphic_identity':'volunteers'}
    id = db.Column(db.Integer, db.ForeignKey('people.id'), primary_key=True)
    volunteer_profile = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    photo = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def is_auth(self,cli_number,project_num):
        selme = self.id
        clie = User.query.filter_by(id=cli_number).first()
        pro = clie.project.filter_by(id=project_num).first()
        if pro is None:
            return False
        volun = pro.volunteer.first()
        return volun.id == selme

    @staticmethod
    def fake_volunteers(count=10):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()

        for i in range(count):
            u = Volunteer(name=forgery_py.name.full_name(),
                    postcode ='KT1',
                    address_line_1 = forgery_py.address.street_number(),
                    address_line_2 =forgery_py.address.street_name(),
                    town_city= 'London',
                    telephone = forgery_py.address.phone(),
                    mobile= forgery_py.address.phone(),
                    email=forgery_py.internet.email_address(),
                    password='aaa',
                    volunteer_profile=forgery_py.lorem_ipsum.sentences(3),
                    confirmed = True)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def delete_all_vol_projects(id):
        vol = Volunteer.query.filter_by(id=id).first()
        pro = vol.project.all()

        for x in range(len(pro)):
            db.session.delete(pro[x])
        db.session.commit()



class Referal(db.Model):
    __tablename__ = 'referal'

    referee_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    referenced_id =db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(People):
    __tablename__ = 'users'
    __mapper_args__ = {'polymorphic_identity':'users'}
    id = db.Column(db.Integer, db.ForeignKey('people.id'), primary_key=True)
    organisation_name = db.Column(db.String(64)) # new field
    age_range = db.Column(db.String(64))
    relation = db.Column(db.String(64), default='self')
    initial_contact = db.Column(db.String(64), default='self')
    how_they_find_us = db.Column(db.Text)

    referee = db.relationship('Referal', foreign_keys=[Referal.referenced_id],
                                        backref=db.backref('referenced', lazy='joined'),
                                        lazy='dynamic',
                                        cascade='all, delete-orphan')

    referenced = db.relationship('Referal', foreign_keys=[Referal.referee_id],
                                        backref=db.backref('referee', lazy='joined'),
                                        lazy='dynamic',
                                        cascade='all, delete-orphan')

    def who_referenced(self):
        if self.referee.first():
            return [self.referee.first().referenced.id, self.referee.first().referenced.name]
        else:
            return False


    @staticmethod
    def fake_users(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        import random

        age_range = ['0-17', '18-64', '65+']
        seed()
        for i in range(count):
            u = User(name=forgery_py.name.full_name(),
                    postcode ='KT1 1TP',
                    address_line_1 = forgery_py.address.street_number(),
                    address_line_2 =forgery_py.address.street_name(),
                    town_city= 'London',
                    telephone = forgery_py.address.phone(),
                    mobile= forgery_py.address.phone(),
                    email=forgery_py.internet.email_address(),
                    age_range=random.choice(age_range),
                    relation=forgery_py.lorem_ipsum.sentence(),
                    initial_contact='Direct',
                    how_they_find_us=forgery_py.lorem_ipsum.sentence(),
                    )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)

    first_database_entry = db.Column(db.DateTime, default=datetime.utcnow) # edited from timestamp

    date_first_contacted = db.Column(db.Date)
    last_edited = db.Column(db.DateTime) # new field

    request_body = db.Column(db.Text)
    request_title = db.Column(db.String(64))
    status = db.Column(db.String(64), default='Awaiting Volunteer')
    end_date = db.Column(db.DateTime)
    expense_hours= db.Column(db.Integer)
    solution = db.Column(db.Text())


    volunteer = db.relationship('Volunteer', secondary=volPro, backref= db.backref('project', lazy='dynamic'), lazy='dynamic')
    user = db.relationship('User', secondary=cliPro, backref= db.backref('project', lazy='dynamic'), lazy='dynamic')
    comments = db.relationship('Comment', backref='project', lazy='dynamic')
    photos = db.relationship('ProjectPhoto', backref='project', lazy='dynamic')
    solutionphotos = db.relationship('SolutionPhotos', backref='project', lazy='dynamic')


    Donation_discussed = db.Column(db.Boolean)
    whom_donation_discussed = db.Column(db.String(64))
    donation_outcome = db.Column(db.String(64))

    data_protection =  db.Column(db.Boolean)
    whom_data_protection_discussed = db.Column(db.String(64))
    dat_protection_outcome = db.Column(db.String(64))


    @staticmethod
    def fake_projects(count=80):
        import random
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        #status = ['Awaiting Volunteer', 'Ongoing', 'Finished', 'Closed']
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()

            p = Project(request_body=forgery_py.lorem_ipsum.sentences(6),
                        request_title=forgery_py.lorem_ipsum.sentence(),
                        status='Awaiting Volunteer',
                        Donation_discussed=True,
                        donation_outcome=forgery_py.lorem_ipsum.sentence(),
                        data_protection=True,
                        dat_protection_outcome=forgery_py.lorem_ipsum.sentence())
            p.user.append(u)
            db.session.add_all([u,p])
            db.session.commit()


@login_manager.user_loader
def load_user(people_id):
    return People.query.get(int(people_id))

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Comment(db.Model):
    __tablename__='comment'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())

    first_datase_entry = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # changed from timestamp
    date_reported = db.Column(db.Date)
    last_edited = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    @staticmethod
    def fake_comments(pro):
        from random import seed, randint
        import forgery_py
        seed()
        for i in range(pro):
            vol = Volunteer.query.filter_by(id=1).first()
            num =randint(0, pro - 1)
            project = Project.query.filter_by(id=num).first()
            c = Comment(body=forgery_py.lorem_ipsum.sentences(5),
                        author=vol,
                        project = project)
            db.session.add(c)
            db.session.commit()



class ProjectPhoto(db.Model):
    __tablename__ = 'projectphotos'

    id = db.Column(db.Integer, primary_key=True)
    first_datase_entry = db.Column(db.DateTime, index=True, default=datetime.utcnow) # new field
    location = db.Column(db.String(128))
    caption = db.Column(db.Text())
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))


class SolutionPhotos(db.Model):
    __tablename__ = 'solutionphotos'

    id = db.Column(db.Integer, primary_key=True)
    first_database_entry = db.Column(db.DateTime, index=True, default=datetime.utcnow) # new field
    location = db.Column(db.String(128))
    caption = db.Column(db.Text())
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
