import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")

    # SQLite path under /database/
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{os.path.join(ROOT_DIR, 'database', 'users.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Static uploads path
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10MB

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False

def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return ProdConfig if env == "production" else DevConfig
