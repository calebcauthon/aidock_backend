def logout_controller(dependencies):
    flask = dependencies['flask']
    UserModel = dependencies['UserModel']
    session = dependencies['session']

    UserModel.clear_login_token(session.get('user_id'))
    session.clear()
    flask.flash('Logged out successfully.', 'success')
    return flask.redirect(flask.url_for('auth.login'))
