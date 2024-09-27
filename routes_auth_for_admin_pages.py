from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash
from db.init_db import create_connection, execute_sql
from routes_auth_helpers import set_librarian_session

auth_admin = Blueprint('auth_admin', __name__)

@auth_admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, password_hash, role, organization_id FROM users WHERE username = ?", (username,))
        conn.close()

        if not user:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth_admin.login'))
        
        password_hash = user[0][2]
        if user and check_password_hash(password_hash, password):
            set_librarian_session(user[0])

            flash('Logged in successfully.', 'success')
            if session['role'] == 'platform_admin':
                return redirect(url_for('platform_admin_pages.prompt_history'))
            else:
                return redirect(url_for('librarian.librarian_home'))
        else:
            flash(f'Invalid username or password, username: {username}, password: [{password}]', 'error')
    
    return render_template('login.html')

@auth_admin.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth_admin.login'))