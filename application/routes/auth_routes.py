import logging
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required
from ..database import db, bcrypt, login_manager
from ..models import User, SeekerData

logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def register(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        # mirror your original dummy form rendering without WTForms
        class _DummyField:
            def __init__(self, name, ftype="text", value=""):
                self.name = name; self.type = ftype; self.value = value
            def __call__(self, **kwargs):
                from markupsafe import Markup
                attrs = {"type": self.type, "name": self.name, "id": kwargs.pop("id", self.name),
                         "value": kwargs.pop("value", self.value), **kwargs}
                parts = []
                for k, v in attrs.items():
                    if v is None or v is False: continue
                    parts.append(k.replace("_","-") if v is True else f'{k.replace("_","-")}="{v}"')
                return Markup(f"<input {' '.join(parts)}>")

        class _DummyForm:
            def __init__(self):
                self.email=_DummyField("email","email"); self.password=_DummyField("password","password")
                self.name=_DummyField("name"); self.role=_DummyField("role","hidden")
            def hidden_tag(self):
                from markupsafe import Markup
                return Markup("")

        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            role = request.form.get("role") or "seeker"
            password = (request.form.get("password") or "")
            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("registration.html", form=_DummyForm())
            if User.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
                return render_template("registration.html", form=_DummyForm())
            try:
                hash_ = bcrypt.generate_password_hash(password).decode("utf-8")
                u = User(name=name, email=email, password=hash_, role=role)
                db.session.add(u)
                db.session.commit()
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                logger.exception("Registration failed")
                flash(f"Registration error: {e}", "danger")
                return render_template("registration.html", form=_DummyForm())
        return render_template("registration.html", form=_DummyForm())

    @app.route("/login", methods=["GET", "POST"])
    def login():
        class _DummyField:
            def __init__(self, name, ftype="text", value=""):
                self.name = name; self.type = ftype; self.value = value
            def __call__(self, **kwargs):
                from markupsafe import Markup
                attrs = {"type": self.type, "name": self.name, "id": kwargs.pop("id", self.name),
                         "value": kwargs.pop("value", self.value), **kwargs}
                parts = []
                for k, v in attrs.items():
                    if v is None or v is False: continue
                    parts.append(k.replace("_","-") if v is True else f'{k.replace("_","-")}="{v}"')
                return Markup(f"<input {' '.join(parts)}>")

        class _DummyForm:
            def __init__(self):
                self.email=_DummyField("email","email"); self.password=_DummyField("password","password")
                self.name=_DummyField("name"); self.role=_DummyField("role","hidden")
            def hidden_tag(self):
                from markupsafe import Markup
                return Markup("")

        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = (request.form.get("password") or "")
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("Invalid email or password", "danger")
                return render_template("login.html", form=_DummyForm())
            # bcrypt (upgrade legacy plaintext if any)
            if user.password.startswith("$2"):
                valid = bcrypt.check_password_hash(user.password, password)
            else:
                valid = (user.password == password)
                if valid:
                    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
                    db.session.commit()
            if not valid:
                flash("Invalid email or password", "danger")
                return render_template("login.html", form=_DummyForm())
            login_user(user)
            if user.role == "seeker":
                has_bio = SeekerData.query.filter_by(email=user.email).first()
                return redirect(url_for("seeker_dashboard" if has_bio else "seeker_data"))
            return redirect(url_for("company_dashboard"))
        return render_template("login.html", form=_DummyForm())

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        # keeping your original flash category
        flash("You have been logged out.", "danger")
        return redirect(url_for("login"))
