import os
import logging
from datetime import datetime

from flask import (
    render_template, redirect, url_for, flash, request, jsonify, send_file
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..database import db
from ..models import (
    JobPost, ActiveApplication, AcceptedApplication, RejectedApplication,
    SeekerData, CompanyData
)
from ..utils.security import seeker_required
from ..utils.file_utils import allowed_file, random_filename
from .. import bcrypt  # bcrypt is initialized in application/__init__.py

logger = logging.getLogger(__name__)


def register(app):
    # -------------------------------------------------
    # Seeker Dashboard (shell; lists load via /api)
    # -------------------------------------------------
    @app.route("/seeker_dashboard")
    @login_required
    @seeker_required
    def seeker_dashboard():
        return render_template("seeker_dashboard.html")

    # -------------------------------------------------
    # Seeker Bio (initial form used by old flow)
    # -------------------------------------------------
    @app.route("/seeker_data", methods=["GET", "POST"])
    @login_required
    @seeker_required
    def seeker_data():
        if request.method == "POST":
            full_name = (request.form.get("full_name") or current_user.name).strip()
            email = current_user.email
            phone = (request.form.get("phone") or "").strip()
            education = (request.form.get("education") or "").strip()
            experience = (request.form.get("experience") or "").strip()
            skills = (request.form.get("skills") or "").strip()

            filename = None
            resume_file = request.files.get("resume")
            if resume_file and allowed_file(resume_file.filename):
                filename = random_filename(secure_filename(resume_file.filename))
                resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            sd = SeekerData(
                full_name=full_name, email=email, phone=phone,
                education=education, experience=experience, skills=skills,
                resume_path=filename
            )
            db.session.add(sd)
            db.session.commit()
            flash("Bio data submitted successfully!", "success")
            return redirect(url_for("seeker_dashboard"))

        info = SeekerData.query.filter_by(email=current_user.email).first()
        return render_template("seekerdata.html", seeker=info)

    # -------------------------------------------------
    # Unified Profile (view + edit + password)
    # – used by seeker_dashboard.html -> url_for('profile')
    # -------------------------------------------------
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if request.method == "POST":
            action = request.form.get("action")
            if action == "details":
                if current_user.role == "seeker":
                    sd = SeekerData.query.filter_by(email=current_user.email).first()
                    if not sd:
                        sd = SeekerData(full_name=current_user.name, email=current_user.email, phone="")
                        db.session.add(sd)

                    sd.full_name = (request.form.get("full_name") or sd.full_name or "").strip()
                    sd.phone = (request.form.get("phone") or sd.phone or "").strip()
                    sd.education = request.form.get("education") or sd.education
                    sd.experience = request.form.get("experience") or sd.experience
                    sd.skills = request.form.get("skills") or sd.skills

                    # Optional resume upload
                    resume_file = request.files.get("resume")
                    if resume_file and allowed_file(resume_file.filename):
                        if sd.resume_path:
                            try:
                                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], sd.resume_path))
                            except Exception:
                                pass
                        newname = random_filename(secure_filename(resume_file.filename))
                        resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], newname))
                        sd.resume_path = newname

                    # Keep display name in sync
                    current_user.name = sd.full_name
                else:
                    cd = CompanyData.query.filter_by(email=current_user.email).first()
                    if not cd:
                        cd = CompanyData(email=current_user.email)
                        db.session.add(cd)
                    cd.contact_name = request.form.get("contact_name") or cd.contact_name
                    cd.company_name = request.form.get("company_name") or cd.company_name
                    cd.phone = request.form.get("phone") or cd.phone
                    cd.website = request.form.get("website") or cd.website
                    if cd.contact_name:
                        current_user.name = cd.contact_name

                try:
                    db.session.commit()
                    flash("Profile updated successfully!", "success")
                except Exception as e:
                    db.session.rollback()
                    logger.exception("Profile update failed")
                    flash(f"Error updating profile: {e}", "danger")

            elif action == "password":
                current_pw = request.form.get("current_password", "")
                new_pw = request.form.get("new_password", "")
                confirm_pw = request.form.get("confirm_password", "")

                if not bcrypt.check_password_hash(current_user.password, current_pw):
                    flash("Current password is incorrect.", "danger")
                elif len(new_pw) < 6:
                    flash("New password must be at least 6 characters.", "danger")
                elif new_pw != confirm_pw:
                    flash("New password and confirm password do not match.", "danger")
                else:
                    try:
                        current_user.password = bcrypt.generate_password_hash(new_pw).decode("utf-8")
                        db.session.commit()
                        flash("Password updated successfully!", "success")
                    except Exception as e:
                        db.session.rollback()
                        logger.exception("Password update failed")
                        flash(f"Could not update password: {e}", "danger")

            return redirect(url_for("profile"))

        # GET -> render profile page with role-specific data
        if current_user.role == "seeker":
            sd = SeekerData.query.filter_by(email=current_user.email).first()
            resume_url = None
            if sd and sd.resume_path:
                resume_url = url_for("view_resume", email=current_user.email)

            profile_obj = type("Obj", (object,), {
                "full_name": getattr(sd, "full_name", None) or current_user.name,
                "email": current_user.email,
                "phone": getattr(sd, "phone", ""),
                "education": getattr(sd, "education", ""),
                "experience": getattr(sd, "experience", ""),
                "skills": getattr(sd, "skills", ""),
                "resume_path": getattr(sd, "resume_path", None),
            })()
            return render_template("profile.html", role="seeker", profile=profile_obj, resume_url=resume_url)

        cd = CompanyData.query.filter_by(email=current_user.email).first()
        posts_count = JobPost.query.filter_by(email=current_user.email).count()
        profile_obj = type("Obj", (object,), {
            "email": current_user.email,
            "contact_name": current_user.name if not cd else (cd.contact_name or current_user.name),
            "company_name": "" if not cd else (cd.company_name or ""),
            "phone": "" if not cd else (cd.phone or ""),
            "website": "" if not cd else (cd.website or ""),
            "jobs_posted": posts_count,
        })()
        return render_template("profile.html", role="company", profile=profile_obj, resume_url=None)

    @app.route("/view_resume/<email>")
    @login_required
    def view_resume(email):
        seeker = SeekerData.query.filter_by(email=email).first()
        if seeker and seeker.resume_path:
            path = os.path.join(app.config["UPLOAD_FOLDER"], seeker.resume_path)
            if os.path.exists(path):
                return send_file(path, as_attachment=False)
        if request.args.get("silent") == "1":
            return ("Resume not found", 404)
        flash("Resume not found", "danger")
        return redirect(url_for("company_dashboard" if current_user.role == "company" else "seeker_dashboard"))

    # -------------------------------------------------
    # Job listings page (Apply disabled if already applied)
    # -------------------------------------------------
    @app.route("/applications", methods=["GET"], endpoint="applications")
    @app.route("/job_listings", methods=["GET"], endpoint="job_listings")
    @login_required
    @seeker_required
    def job_listings():
        q = (request.args.get("q") or "").strip().lower()
        employment_type = request.args.get("employment_type")
        salary_from = request.args.get("salary_from", type=int)
        salary_to = request.args.get("salary_to", type=int)

        query = JobPost.query
        if q:
            like = f"%{q}%"
            query = query.filter(
                db.or_(
                    JobPost.job_title.ilike(like),
                    JobPost.company_name.ilike(like),
                    JobPost.location.ilike(like),
                )
            )
        if employment_type:
            query = query.filter_by(employment_type=employment_type)
        if salary_from is not None:
            query = query.filter((JobPost.salary_from >= salary_from) | (JobPost.salary_from.is_(None)))
        if salary_to is not None:
            query = query.filter((JobPost.salary_to <= salary_to) | (JobPost.salary_to.is_(None)))

        jobs = query.all()

        # -------- compute “already has a status” sets (email-based schema) --------
        user_email = current_user.email

        act = ActiveApplication.query.filter_by(seeker_email=user_email).all()
        acc = AcceptedApplication.query.filter_by(seeker_email=user_email).all()
        rej = RejectedApplication.query.filter_by(seeker_email=user_email).all()

        def resolve_job_id(row):
            # Prefer job_post_id column if it exists in your table
            jid = getattr(row, "job_post_id", None)
            if jid:
                return jid
            # Fallback: best-effort by title (for legacy rows that store only title)
            j = JobPost.query.filter_by(job_title=row.job_title).first()
            return j.id if j else None

        # set of job IDs with *any* status
        applied_ids = {
            jid for rows in (act, acc, rej) for jid in (resolve_job_id(r) for r in rows) if jid
        }
        # set of titles as a secondary safety net (in case ID not stored)
        applied_titles = {
            r.job_title for rows in (act, acc, rej) for r in rows if getattr(r, "job_title", None)
        }
        # -------------------------------------------------------------------------

        return render_template(
            "applications.html",
            jobs=jobs,
            applied_ids=applied_ids,
            applied_titles=applied_titles  # <- new
        )


    # -------------------------------------------------
    # Apply for a job (canonical + legacy alias)
    # -------------------------------------------------
    @app.route("/apply/<int:job_post_id>", methods=["POST"], endpoint="apply_for_job")
    @app.route("/apply_job/<int:job_post_id>", methods=["POST"], endpoint="apply_job")  # keep old templates working
    @login_required
    @seeker_required
    def apply_for_job(job_post_id):
        def _wants_json() -> bool:
            return "application/json" in (request.headers.get("Accept", "")).lower()

        user_email = current_user.email
        user_name = current_user.name

        # Duplicate check
        existing = ActiveApplication.query.filter_by(
            seeker_email=user_email, job_post_id=job_post_id
        ).first()
        if existing:
            msg = "You have already applied for this job."
            if _wants_json():
                return jsonify(success=False, message=msg), 409
            flash(msg, "warning")
            return redirect(request.referrer or url_for("applications"))

        job = JobPost.query.get(job_post_id)
        if not job:
            msg = "Job post not found."
            if _wants_json():
                return jsonify(success=False, message=msg), 404
            flash(msg, "danger")
            return redirect(request.referrer or url_for("applications"))

        if not bool(getattr(job, "is_open", 1)):
            msg = "This job is closed."
            if _wants_json():
                return jsonify(success=False, message=msg), 403
            flash(msg, "danger")
            return redirect(request.referrer or url_for("applications"))

        app_row = ActiveApplication(
            seeker_name=user_name,
            seeker_email=user_email,
            job_post_id=job_post_id,
            job_title=job.job_title,
            applied_at=datetime.utcnow(),
        )
        try:
            db.session.add(app_row)
            db.session.commit()
            msg = "Application submitted successfully!"
            if _wants_json():
                return jsonify(success=True, message=msg), 201
            flash(msg, "success")
        except Exception as e:
            db.session.rollback()
            logger.exception("apply_for_job failed")
            msg = f"Could not submit application: {e}"
            if _wants_json():
                return jsonify(success=False, message=msg), 500
            flash(msg, "danger")

        return redirect(url_for("applications"))

    # -------------------------------------------------
    # Dashboard data API (accepted / rejected / under review)
    # -------------------------------------------------
    @app.route("/api/seeker_status", methods=["GET"])
    @login_required
    @seeker_required
    def seeker_status():
        user_email = current_user.email
        search = (request.args.get("search") or "").strip().lower()
        filters = (request.args.get("filters") or "").split(",") if request.args.get("filters") else []
        sort = (request.args.get("sort") or "asc").lower()

        accepted_apps = AcceptedApplication.query.filter_by(seeker_email=user_email).all()
        rejected_apps = RejectedApplication.query.filter_by(seeker_email=user_email).all()
        active_apps   = ActiveApplication.query.filter_by(seeker_email=user_email).all()

        def pack_rows(raw, status_key):
            out = []
            for r in raw:
                # Enrich with job details by title
                job = JobPost.query.filter_by(job_title=r.job_title).first()
                out.append({
                    "job_title": r.job_title,
                    "company_name": (job.company_name if job else "Unknown Company"),
                    "applied_at": r.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "job_post_id": job.id if job else None,
                    "job_description": job.job_description if job else "",
                    "key_responsibilities": job.key_responsibilities if job else "",
                    "status": status_key,
                })
            return out

        accepted = pack_rows(accepted_apps, "accepted")
        rejected = pack_rows(rejected_apps, "rejected")
        under_review = pack_rows(active_apps, "under_review")

        def apply_search(rows):
            if not search:
                return rows
            return [r for r in rows if search in r["job_title"].lower() or search in r["company_name"].lower()]

        def sortrows(rows):
            return sorted(rows, key=lambda x: x["applied_at"], reverse=(sort == "desc"))

        accepted = sortrows(apply_search(accepted))
        rejected = sortrows(apply_search(rejected))
        under_review = sortrows(apply_search(under_review))

        def filt(rows, key):
            if filters and key not in filters:
                return []
            return rows

        return jsonify({
            "accepted": filt(accepted, "accepted"),
            "rejected": filt(rejected, "rejected"),
            "under_review": filt(under_review, "under_review"),
        })
