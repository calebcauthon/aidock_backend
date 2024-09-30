from flask import Blueprint
from .shared.auth import auth
from .dock.chat import chat, prompt_routes
from .admin.files import files
from .librarian.files import librarian
from .librarian.users import librarian_users_routes
from .shared.profile import profile_routes
from .admin.organization import organization_routes, platform_admin_pages
from .admin.history import history
from .admin.users import user_routes
from .dock.verify import verify_website

def register_routes(app):
    app.register_blueprint(auth)
    app.register_blueprint(chat)
    app.register_blueprint(files)
    app.register_blueprint(librarian)
    app.register_blueprint(librarian_users_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(organization_routes, url_prefix='/organizations')
    app.register_blueprint(platform_admin_pages)
    app.register_blueprint(prompt_routes)
    app.register_blueprint(history)
    app.register_blueprint(user_routes, url_prefix='/users')
    app.register_blueprint(verify_website)
