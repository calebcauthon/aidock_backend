from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash
from routes_auth_helpers import set_librarian_session
from db.user_model import UserModel

auth_admin = Blueprint('auth_admin', __name__)

@auth_admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = UserModel.get_user_by_username(username)

        if not user:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth_admin.login'))
        
        password_hash = user['password_hash']
        if user and check_password_hash(password_hash, password):
            set_librarian_session(user)

            flash('Logged in successfully.', 'success')
            if session['role'] == 'platform_admin':
                return redirect(url_for('platform_admin_pages.prompt_history'))
            elif session['role'] == 'librarian':
                return redirect(url_for('librarian.librarian_home'))
            else:
                return redirect(url_for('profile.profile'))
        else:
            flash(f'Invalid username or password, username: {username}, password: [{password}]', 'error')
    
    return render_template('login.html')

@auth_admin.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth_admin.login'))