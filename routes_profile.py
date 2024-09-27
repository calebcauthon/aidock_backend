from flask import Blueprint, render_template, jsonify
from routes_auth_helpers import user_required

profile_routes = Blueprint('profile', __name__)

@profile_routes.route('/profile')
@user_required
def profile(user):
    return render_template('profile.html', user=user)

@profile_routes.route('/api/profile')
@user_required
def api_profile(user):
    return jsonify({
        'username': user['username'],
        'role': user['role']
    })