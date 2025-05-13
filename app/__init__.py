from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import models, routes
        db.create_all()
        app.register_blueprint(routes.bp)

    return app
