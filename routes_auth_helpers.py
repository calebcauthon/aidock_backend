from flask import flash, redirect, url_for, session
from functools import wraps

def authenticate_user_with_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        from functools import wraps
        from db.user_model import UserModel

        login_token = request.headers.get('login_token')
        if not login_token:
            return jsonify({"error": "No login token provided"}), 401
        
        user = UserModel.get_user_by_login_token(login_token)
        if not user:
            return jsonify({"error": "Invalid login token"}), 401
        
        return func(user, *args, **kwargs)
    return wrapper

def platform_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'platform_admin':
            flash('You do not have admin permission to access this page.', 'error')
            return redirect(url_for('auth_admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'librarian':
            flash('You do not have librarian permission to access this page.', 'error')
            return redirect(url_for('auth_admin.login'))
        
        from db.user_model import UserModel
        user = UserModel.get_user(session['user_id'])
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth_admin.login'))
        
        return f(user, *args, **kwargs)
    return decorated_function
