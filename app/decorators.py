from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.PERMX)(f)

def volunteer_required(f):
    return permission_required(Permission.READ)(f)

def access_required(cli_number,project_num):
    def decorator(f):
        @wraps(f)
        def decorated_function(cli_number,project_num,*args, **kwargs):
            if not current_user.is_auth(cli_number,project_num):
                abort(403)
            return f(cli_number,project_num,*args, **kwargs)
        return decorated_function
    return decorator



def user_only(func):
    def decorated_function(*args, **kwargs):
        if not current_user.type != 'users':
            abort(403)
        return func(*args, **kwargs)
    return decorated_function
