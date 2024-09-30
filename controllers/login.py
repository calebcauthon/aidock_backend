def login_controller(dependencies):
    session = dependencies['session']
    flask = dependencies['flask']
    set_librarian_session = dependencies['set_librarian_session']
    request = flask.request
    UserModel = dependencies['UserModel']
    check_password_hash = dependencies['check_password_hash']
    uuid = dependencies['uuid']
    flash = flask.flash
    redirect = flask.redirect
    url_for = flask.url_for

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = UserModel.get_user_by_username(username)

        if not user:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        password_hash = user['password_hash']
        if user and check_password_hash(password_hash, password):
            login_token = str(uuid.uuid4())
            UserModel.update_login_token(user['id'], login_token)

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
    
    return flask.render_template('login.html')