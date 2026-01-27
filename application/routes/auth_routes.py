import logging
from flask import jsonify, render_template, request, redirect, flash, url_for
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

    @app.post("/api/forgot/check")
    def api_forgot_check():
        email = (request.form.get("email") or "").strip().lower()
        if not email:
            return jsonify({"ok": False, "error": "Email required"}), 400
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"ok": True, "exists": False})
        return jsonify({"ok": True, "exists": True, "role": user.role})

    @app.post("/api/forgot/reset")
    def api_forgot_reset():
        email = (request.form.get("email") or "").strip().lower()
        new_pw = request.form.get("new_password") or ""
        confirm = request.form.get("confirm_password") or ""

        if not email or not new_pw or not confirm:
            return jsonify({"ok": False, "error": "All fields are required"}), 400
        if new_pw != confirm:
            return jsonify({"ok": False, "error": "Passwords do not match"}), 400
        if len(new_pw) < 6:
            return jsonify({"ok": False, "error": "Password must be at least 6 characters"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"ok": False, "error": "Email not found"}), 404

        if bcrypt.check_password_hash(user.password, new_pw):
            return jsonify({"ok": False, "error": "New password cannot be the same as your current password"}), 400

        try:
            user.password = bcrypt.generate_password_hash(new_pw).decode("utf-8")
            db.session.commit()
            return jsonify({"ok": True, "message": "Password updated"})
        except Exception as e:
            db.session.rollback()
            app.logger.exception("forgot/reset failed")
            return jsonify({"ok": False, "error": "Server error"}), 500

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "danger")
        return redirect(url_for("login"))
