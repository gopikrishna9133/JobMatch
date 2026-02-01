import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(ROOT_DIR, "database.db")

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))

class DevConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{DB_PATH}"
    )

class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{DB_PATH}"
    )

def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return ProdConfig if env == "production" else DevConfig
