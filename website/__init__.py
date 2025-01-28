from flask import Flask
from datetime import timedelta
import secrets
import os

def create_app():
    app = Flask(__name__)



    app.config.update(
        SECRET_KEY='dev', #weak
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        SESSION_COOKIE_SECURE=False,  # Change to True for production with HTTPS
        SESSION_COOKIE_HTTPONLY=False,
        SESSION_COOKIE_SAMESITE=None,#'Lax'
        DEBUG=True  # Enable debug mode for development
    )

    # Import and register blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
