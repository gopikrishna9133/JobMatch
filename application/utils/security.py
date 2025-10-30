from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def seeker_required(fn):
    @wraps(fn)
    def _wrap(*a, **kw):
        if not current_user.is_authenticated or current_user.role != "seeker":
            flash("Only job seekers can access this area.", "danger")
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return _wrap

def company_required(fn):
    @wraps(fn)
    def _wrap(*a, **kw):
        if not current_user.is_authenticated or current_user.role != "company":
            flash("Only company users can access this area.", "danger")
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return _wrap
