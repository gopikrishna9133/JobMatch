import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database import db
from ..models import Resource
from ..utils.security import company_required
from ..utils.file_utils import allowed_file, random_filename

def register(app):

    @app.route("/resources")
    @login_required
    def resources():
        videos = Resource.query.filter_by(resource_type="Video").order_by(Resource.created_at.desc()).all()
        books = Resource.query.filter_by(resource_type="Book").order_by(Resource.created_at.desc()).all()
        websites = Resource.query.filter_by(resource_type="Website").order_by(Resource.created_at.desc()).all()
        is_company = current_user.role == "company"
        return render_template("resources.html", videos=videos, books=books, websites=websites, is_company=is_company)

    @app.route("/resources/add", methods=["GET", "POST"])
    @login_required
    @company_required
    def add_resource():
        if request.method == "POST":
            rtype = request.form.get("resource_type")
            title = request.form.get("title")
            urlv = request.form.get("url")
            desc = request.form.get("description")
            image_file = request.files.get("image")
            image_path = None
            if image_file and allowed_file(image_file.filename):
                newname = random_filename(secure_filename(image_file.filename))
                full = os.path.join(app.config["UPLOAD_FOLDER"], newname)
                image_file.save(full)
                image_path = url_for("static", filename=f"uploads/{newname}")
            res = Resource(resource_type=rtype, title=title, url=urlv, description=desc, image_path=image_path)
            db.session.add(res)
            db.session.commit()
            flash("Resource added successfully!", "success")
            return redirect(url_for("resources"))
        return render_template("add_resource.html")

    @app.route("/resources/<int:id>/edit", methods=["GET", "POST"])
    @login_required
    @company_required
    def edit_resource(id):
        resource = Resource.query.get_or_404(id)
        if request.method == "POST":
            resource.resource_type = request.form.get("resource_type", resource.resource_type)
            resource.title = request.form.get("title", resource.title)
            resource.url = request.form.get("url", resource.url)
            resource.description = request.form.get("description", resource.description)
            if request.form.get("remove_current_image") == "true":
                resource.image_path = None
            image_file = request.files.get("image")
            if image_file and allowed_file(image_file.filename):
                newname = random_filename(secure_filename(image_file.filename))
                full = os.path.join(app.config["UPLOAD_FOLDER"], newname)
                image_file.save(full)
                resource.image_path = url_for("static", filename=f"uploads/{newname}")
            db.session.commit()
            flash("Resource updated successfully!", "success")
            return redirect(url_for("resources"))
        return render_template("edit_resource.html", resource=resource)

    @app.route("/resources/<int:id>/delete", methods=["POST"])
    @login_required
    @company_required
    def delete_resource(id):
        resource = Resource.query.get_or_404(id)
        db.session.delete(resource)
        db.session.commit()
        flash("Resource deleted successfully!", "success")
        return redirect(url_for("resources"))
