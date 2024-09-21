from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from init_db import create_connection, execute_sql
from functools import wraps

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def platform_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'platform_admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, password_hash, role, organization_id FROM users WHERE username = ?", (username,))
        conn.close()
        
        password_hash = user[0][2]
        if user and check_password_hash(password_hash, password):
            session['user_id'] = user[0][0]
            session['role'] = user[0][3]
            session['organization_id'] = user[0][4]

            flash('Logged in successfully.', 'success')


            return redirect(url_for('organization_routes.list_organizations'))
        else:
            flash(f'Invalid username or password, username: {username}, password: [{password}]', 'error')
    
    return render_template('login.html')



@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))