from flask import render_template
from datetime import datetime
from ..models import JobPost

def render_offer_letter(seeker, job_post_id=None, job_title=None, applied_at_str=""):
    job = None
    if job_post_id:
        job = JobPost.query.get(job_post_id)
    if not job and job_title:
        job = JobPost.query.filter_by(job_title=job_title).first()

    job_title_val = (job.job_title if job else job_title) or "Position"
    company_name  = (job.company_name if job and getattr(job, "company_name", None) else "Your Company")
    department    = getattr(job, "department", "") or ""
    today_str     = datetime.utcnow().strftime("%Y-%m-%d")

    return render_template(
        "offer_letter.html",
        job_title=job_title_val,
        company_name=company_name,
        seeker_name=getattr(seeker, "name", "Candidate"),
        seeker_email=getattr(seeker, "email", ""),
        department=department,
        applied_at=applied_at_str,
        today=today_str
    ), f"Offer_Letter_{company_name}_{job_title_val}_{today_str}.html".replace(" ", "_")
