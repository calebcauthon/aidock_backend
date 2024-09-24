from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from db.init_db import create_connection, execute_sql
from functools import wraps

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, password_hash, role, organization_id FROM users WHERE username = ?", (username,))
        conn.close()

        if not user:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        password_hash = user[0][2]
        if user and check_password_hash(password_hash, password):
            session['user_id'] = user[0][0]
            session['role'] = user[0][3]
            session['organization_id'] = user[0][4]

            flash('Logged in successfully.', 'success')
            return redirect(url_for('librarian.librarian_home'))
        else:
            flash(f'Invalid username or password, username: {username}, password: [{password}]', 'error')
    
    return render_template('login.html')



@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))