from flask_login import UserMixin
from .database import db
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="seeker")

class SeekerData(db.Model):
    __tablename__ = "seeker_data"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    education = db.Column(db.String(200))
    experience = db.Column(db.String(50))
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(200))

class CompanyData(db.Model):
    __tablename__ = "company_data"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_name = db.Column(db.String(100))
    company_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))

class JobPost(db.Model):
    __tablename__ = "job_posts"
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)
    salary_from = db.Column(db.Integer)
    salary_to = db.Column(db.Integer)
    job_description = db.Column(db.Text, nullable=False)
    key_responsibilities = db.Column(db.Text)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    logo_filename = db.Column(db.String(100))
    is_open = db.Column(db.Integer, default=1)

class ActiveApplication(db.Model):
    __tablename__ = "active_application"
    id = db.Column(db.Integer, primary_key=True)
    seeker_name = db.Column(db.String(100), nullable=False)
    seeker_email = db.Column(db.String(120), nullable=False, index=True)
    job_post_id = db.Column(db.Integer, db.ForeignKey("job_posts.id"), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class AcceptedApplication(db.Model):
    __tablename__ = "accepted_application"
    id = db.Column(db.Integer, primary_key=True)
    seeker_name = db.Column(db.String(100), nullable=False)
    seeker_email = db.Column(db.String(120), nullable=False, index=True)
    job_title = db.Column(db.String(200), nullable=False)
    applied_at = db.Column(db.DateTime, nullable=False)

class RejectedApplication(db.Model):
    __tablename__ = "rejected_application"
    id = db.Column(db.Integer, primary_key=True)
    seeker_name = db.Column(db.String(100), nullable=False)
    seeker_email = db.Column(db.String(120), nullable=False, index=True)
    job_title = db.Column(db.String(200), nullable=False)
    applied_at = db.Column(db.DateTime, nullable=False)

class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
