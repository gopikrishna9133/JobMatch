import os
import logging
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..database import db
from ..models import JobPost, ActiveApplication, AcceptedApplication, RejectedApplication, SeekerData
from ..utils.security import company_required
from ..utils.file_utils import allowed_file, random_filename

logger = logging.getLogger(__name__)

def register(app):

    @app.route("/company_dashboard")
    @login_required
    @company_required
    def company_dashboard():
        return render_template("company_dashboard.html")

    @app.route("/postcreation", methods=["GET", "POST"], endpoint="postcreation")
    @app.route("/post_creation", methods=["GET", "POST"])
    @login_required
    @company_required
    def post_creation():
        if request.method == "POST":
            try:
                job_title = request.form["job_title"]
                location = request.form["location"]
                employment_type = request.form["employment_type"]
                salary_from = int(request.form["salary_from"]) if request.form.get("salary_from") else None
                salary_to = int(request.form["salary_to"]) if request.form.get("salary_to") else None
                job_description = request.form["job_description"]
                key_responsibilities = request.form.get("key_responsibilities", "")
                company_name = request.form["company_name"]
                is_open_val = request.form.get("is_open", "1")
                is_open = 1 if str(is_open_val) == "1" else 0

                logo_filename = None
                logo_file = request.files.get("logo")
                if logo_file and allowed_file(logo_file.filename):
                    logo_filename = random_filename(secure_filename(logo_file.filename))
                    logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], logo_filename))

                post = JobPost(
                    job_title=job_title, location=location, employment_type=employment_type,
                    salary_from=salary_from, salary_to=salary_to,
                    job_description=job_description, key_responsibilities=key_responsibilities,
                    company_name=company_name, email=current_user.email,
                    logo_filename=logo_filename, is_open=is_open
                )
                db.session.add(post)
                db.session.commit()
                flash("Job posted successfully!", "success")
                return redirect(url_for("company_dashboard"))
            except Exception as e:
                db.session.rollback()
                app.logger.exception("Error creating job post")
                flash(f"Error posting job: {e}", "danger")
                return redirect(url_for("postcreation"))
        return render_template("postcreation.html")

    @app.route("/edit_job_post/<int:job_id>", methods=["GET", "POST"])
    @login_required
    @company_required
    def edit_job_post(job_id):
        job = JobPost.query.filter_by(id=job_id, email=current_user.email).first_or_404()
        if request.method == "POST":
            try:
                job.job_title = request.form["job_title"]
                job.location = request.form["location"]
                job.employment_type = request.form["employment_type"]
                job.salary_from = int(request.form["salary_from"]) if request.form.get("salary_from") else None
                job.salary_to = int(request.form["salary_to"]) if request.form.get("salary_to") else None
                job.job_description = request.form["job_description"]
                job.key_responsibilities = request.form.get("key_responsibilities", "")
                job.company_name = request.form["company_name"]
                logo_file = request.files.get("logo")
                if logo_file and allowed_file(logo_file.filename):
                    logo_filename = random_filename(secure_filename(logo_file.filename))
                    logo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], logo_filename))
                    job.logo_filename = logo_filename
                db.session.commit()
                flash("Job post updated successfully!", "success")
                return redirect(url_for("company_dashboard"))
            except Exception as e:
                db.session.rollback()
                logger.exception("Error updating job post")
                flash(f"Error updating job: {e}", "danger")
        return render_template("postcreation.html", job=job)

    @app.route('/api/job_posts', methods=['GET'])
    @login_required
    @company_required
    def api_job_posts():
        try:
            posts = JobPost.query.filter_by(email=current_user.email).all()
            out = []
            for p in posts:
                out.append({
                    "id": p.id,
                    "job_title": p.job_title,
                    "location": p.location,
                    "employment_type": p.employment_type,
                    "salary_from": p.salary_from or 0,
                    "salary_to": p.salary_to or 0,
                    "company_name": p.company_name,
                    "email": p.email,
                    "logo_filename": getattr(p, "logo_filename", None),
                    "is_open": bool(getattr(p, "is_open", 1)),
                })
            return jsonify(out)
        except Exception as e:
            app.logger.exception("Error in /api/job_posts")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/job_post/<int:post_id>/toggle', methods=['POST'])
    @login_required
    @company_required
    def api_job_post_toggle(post_id):
        data = request.get_json() or {}
        desired = data.get("is_open")
        if desired is None:
            return jsonify({"error": "is_open required"}), 400
        job = JobPost.query.get_or_404(post_id)
        if job.email != current_user.email:
            return jsonify({"error": "Forbidden"}), 403
        try:
            job.is_open = 1 if desired else 0
            db.session.commit()
            return jsonify({"success": True, "is_open": bool(desired)})
        except Exception as e:
            db.session.rollback()
            app.logger.exception("toggle failed")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/delete_job_post/<int:job_id>", methods=["POST"])
    @login_required
    @company_required
    def api_delete_job_post(job_id):
        job = JobPost.query.filter_by(id=job_id, email=current_user.email).first_or_404()
        try:
            db.session.delete(job)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            logger.exception("Delete job post failed")
            return jsonify({"success": False, "error": str(e)}), 500

    def _my_post_ids():
        id_rows = db.session.query(JobPost.id).filter(JobPost.email == current_user.email).all()
        return [pid for (pid,) in id_rows]

    @app.route("/api/active_applications", methods=["GET"])
    @login_required
    @company_required
    def api_active_applications():
        try:
            my_post_ids = _my_post_ids()
            if not my_post_ids:
                return jsonify([])
            rows = (
                ActiveApplication.query
                .filter(ActiveApplication.job_post_id.in_(my_post_ids))
                .order_by(ActiveApplication.applied_at.desc())
                .all()
            )
            jobs = JobPost.query.filter(JobPost.id.in_(my_post_ids)).all()
            jobs_by_id = {j.id: j for j in jobs}
            out = []
            for r in rows:
                job = jobs_by_id.get(r.job_post_id)
                sd = SeekerData.query.filter_by(email=r.seeker_email).first()
                resume_url = None
                if sd and sd.resume_path:
                    resume_url = url_for("view_resume", email=r.seeker_email)
                out.append({
                    "id": r.id,
                    "seeker_name": r.seeker_name,
                    "seeker_email": r.seeker_email,
                    "job_title": r.job_title,
                    "applied_at": r.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "job_post_id": r.job_post_id,
                    "company_name": job.company_name if job else "Unknown Company",
                    "profile": {
                        "education": getattr(sd, "education", "") if sd else "",
                        "experience": getattr(sd, "experience", "") if sd else "",
                        "skills": getattr(sd, "skills", "") if sd else "",
                    },
                    "resume_url": resume_url
                })
            return jsonify(out)
        except Exception:
            logger.exception("Error in /api/active_applications")
            return jsonify([]), 200

    @app.route("/api/accepted_applications", methods=["GET"])
    @login_required
    @company_required
    def api_accepted_applications():
        try:
            my_post_ids = _my_post_ids()
            if not my_post_ids:
                return jsonify([])
            my_titles = {p.job_title for p in JobPost.query.filter(JobPost.id.in_(my_post_ids)).all()}
            rows = (AcceptedApplication.query
                    .filter(AcceptedApplication.job_title.in_(my_titles))
                    .order_by(AcceptedApplication.applied_at.desc())
                    .all())
            out = []
            for r in rows:
                sd = SeekerData.query.filter_by(email=r.seeker_email).first()
                resume_url = None
                if sd and sd.resume_path:
                    resume_url = url_for("view_resume", email=r.seeker_email)
                out.append({
                    "seeker_name": r.seeker_name,
                    "seeker_email": r.seeker_email,
                    "job_title": r.job_title,
                    "applied_at": r.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "resume_url": resume_url,
                    "profile": {
                        "education": getattr(sd, "education", "") if sd else "",
                        "experience": getattr(sd, "experience", "") if sd else "",
                        "skills": getattr(sd, "skills", "") if sd else "",
                    }
                })
            return jsonify(out)
        except Exception:
            logger.exception("Error in /api/accepted_applications")
            return jsonify([]), 200

    @app.route("/api/accept", methods=["POST"])
    @login_required
    @company_required
    def api_accept():
        data = request.get_json(silent=True) or {}
        app_id = data.get("app_id")
        email = (data.get("email") or "").strip().lower()

        my_post_ids = _my_post_ids()
        if not my_post_ids:
            return jsonify({"success": False, "error": "No job posts"}), 400

        q = ActiveApplication.query.filter(ActiveApplication.job_post_id.in_(my_post_ids))
        if app_id:
            q = q.filter_by(id=app_id)
        elif email:
            q = q.filter_by(seeker_email=email)
        app_row = q.first()
        if not app_row:
            return jsonify({"success": False, "error": "Application not found"}), 404
        try:
            acc = AcceptedApplication(
                seeker_name=app_row.seeker_name,
                seeker_email=app_row.seeker_email,
                job_title=app_row.job_title,
                applied_at=app_row.applied_at
            )
            db.session.add(acc)
            db.session.delete(app_row)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            logger.exception("Accept failed")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/reject", methods=["POST"])
    @login_required
    @company_required
    def api_reject():
        data = request.get_json(silent=True) or {}
        app_id = data.get("app_id")
        email = (data.get("email") or "").strip().lower()

        my_post_ids = _my_post_ids()
        if not my_post_ids:
            return jsonify({"success": False, "error": "No job posts"}), 400

        q = ActiveApplication.query.filter(ActiveApplication.job_post_id.in_(my_post_ids))
        if app_id:
            q = q.filter_by(id=app_id)
        elif email:
            q = q.filter_by(seeker_email=email)
        app_row = q.first()
        if not app_row:
            return jsonify({"success": False, "error": "Application not found"}), 404
        try:
            rej = RejectedApplication(
                seeker_name=app_row.seeker_name,
                seeker_email=app_row.seeker_email,
                job_title=app_row.job_title,
                applied_at=app_row.applied_at
            )
            db.session.add(rej)
            db.session.delete(app_row)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            logger.exception("Reject failed")
            return jsonify({"success": False, "error": str(e)}), 500
