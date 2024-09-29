from flask import Blueprint
from .auth import auth_admin

def register_routes(app):
    app.register_blueprint(auth_admin)
