from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
import flask
from werkzeug.security import check_password_hash
from db.user_model import UserModel
import uuid
from controllers.login import login_controller
from controllers.logout import logout_controller
from functools import wraps

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller({
        'flask': flask,
        'UserModel': UserModel,
        'check_password_hash': check_password_hash,
        'uuid': uuid,
        'set_librarian_session': set_librarian_session,
        'session': session
    })

@auth.route('/logout')
def logout():
    return logout_controller({
        'flask': flask,
        'UserModel': UserModel,
        'session': session
    })

@auth.route('/verify', methods=['POST'])
def verify_token():
    data = request.json
    login_token = data.get('token')
    
    if not login_token:
        return jsonify({"error": "Missing login token"}), 400
    
    user = UserModel.get_user_by_login_token(login_token)
    
    if user:
        return jsonify({"isValid": True}), 200
    else:
        return jsonify({"isValid": False}), 200

def authenticate_user_with_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        login_token = request.headers.get('login_token')
        if not login_token:
            return jsonify({"error": "No login token provided"}), 401
        
        user = UserModel.get_user_by_login_token(login_token)
        if not user:
            return jsonify({"error": "Invalid login token"}), 401
        
        return func(user, *args, **kwargs)
    return wrapper

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and session.get('role') not in ['user', 'librarian', 'platform_admin']:
            flash('You do not have user permission to access this page.', 'error')
            return redirect(url_for('auth.login'))

        user = UserModel.get_user(session['user_id'])
        return f(user, *args, **kwargs)
    return decorated_function

def platform_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'platform_admin':
            flash('You do not have admin permission to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def set_librarian_session(user):
    session['user_id'] = user['id']
    session['role'] = user['role']
    session['organization_id'] = user['organization_id']

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if login_token is provided in the URL
        login_token = request.args.get('login_token')

        if login_token:
            user = UserModel.get_user_by_login_token(login_token)
            if user and user['role'] == 'librarian':
                set_librarian_session(user)
            else:
                flash('Invalid or unauthorized login token.', 'error')
                return redirect(url_for('auth.login'))
        
        # Check if user is already logged in and has librarian role
        if 'user_id' not in session or session.get('role') != 'librarian':
            flash('You do not have librarian permission to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = UserModel.get_user(session['user_id'])
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(user, *args, **kwargs)
    return decorated_function
