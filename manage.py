#!/usr/bin/env python
import os
from app import create_app, db
from app.models import Role, Volunteer, User, Project,People, Comment, ProjectPhoto, Referal,cliPro
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from logging import FileHandler, WARNING


app = create_app('development')

manager = Manager(app)
migrate = Migrate(app, db)


file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

app.logger.addHandler(file_handler)

def make_shell_context():
    return dict(app=app,
                db=db,
                Role=Role,
                Volunteer=Volunteer,
                User=User,
                Project=Project,
                People=People,
                Comment=Comment,
                ProjectPhoto=ProjectPhoto,
                Referal=Referal,
                cliPro=cliPro)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
