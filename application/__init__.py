import os
from flask import Flask
from .config import get_config
from .database import db, bcrypt, login_manager

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(get_config())

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        from . import models
        db.create_all()

    from .routes import (
        common_routes,
        auth_routes,
        seeker_routes,
        company_routes,
        resource_routes,
        chatbot_routes
    )

    common_routes.register(app)
    auth_routes.register(app)
    seeker_routes.register(app)
    company_routes.register(app)
    resource_routes.register(app)
    chatbot_routes.register(app)

    return app
