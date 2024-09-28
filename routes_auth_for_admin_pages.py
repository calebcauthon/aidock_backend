from flask import Blueprint, request, redirect, url_for, render_template, flash, session
import flask
from werkzeug.security import check_password_hash
from routes_auth_helpers import set_librarian_session
from db.user_model import UserModel
import uuid
from controllers.login import login_controller
from controllers.logout import logout_controller

auth_admin = Blueprint('auth_admin', __name__)

@auth_admin.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller({
        'flask': flask,
        'UserModel': UserModel,
        'check_password_hash': check_password_hash,
        'uuid': uuid,
        'set_librarian_session': set_librarian_session,
        'session': session
    })

@auth_admin.route('/logout')
def logout():
    return logout_controller({
        'flask': flask,
        'UserModel': UserModel,
        'session': session
    })