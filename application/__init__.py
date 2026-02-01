import os
from flask import Flask
from .config import get_config
from .database import db, bcrypt, login_manager

def _ensure_path_exists(path: str):
    """Create parent directory for a file path if missing."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(get_config())

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Ensure uploads dir exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Ensure SQLite directory exists BEFORE first connection
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        db_file = db_uri.replace("sqlite:///", "", 1)
        _ensure_path_exists(db_file)

    # Create tables & (optional) schema guard
    with app.app_context():
        # IMPORTANT: import models BEFORE create_all()
        from . import models  # registers all models with SQLAlchemy

        from sqlalchemy import text

        # Create all tables now that models are imported
        db.create_all()

        # Only run ALTER if the table exists and is missing the column
        try:
            # Does the table exist?
            exists = db.session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='job_posts'")
            ).scalar()
            if exists:
                rows = db.session.execute(text("PRAGMA table_info(job_posts)")).fetchall()
                cols = {row[1] for row in rows}
                if "is_open" not in cols:
                    db.session.execute(text("ALTER TABLE job_posts ADD COLUMN is_open INTEGER DEFAULT 1"))
                    db.session.commit()
                    app.logger.info("Added is_open column to job_posts")
        except Exception as e:
            app.logger.warning(f"Schema check skipped: {e}")

    # Register route modules
    from .routes import (
        common_routes, auth_routes, seeker_routes,
        company_routes, resource_routes, chatbot_routes
    )
    common_routes.register(app)
    auth_routes.register(app)
    seeker_routes.register(app)
    company_routes.register(app)
    resource_routes.register(app)
    chatbot_routes.register(app)

    return app
