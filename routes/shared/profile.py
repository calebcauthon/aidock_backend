from flask import Blueprint, render_template, jsonify, request
from routes.shared.auth import user_required
from db.user_model import UserModel

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

@profile_routes.route('/api/profile/update', methods=['POST'])
@user_required
def update_profile(user):
    data = request.json
    new_username = data.get('username')
    new_password = data.get('password')

    if not new_username:
        return jsonify({'success': False, 'message': 'Username cannot be empty'}), 400

    current_user = UserModel.get_user(user['id'])

    if current_user['username'] != new_username:
        existing_user = UserModel.get_user_by_username(new_username)
        if existing_user:
            return jsonify({'success': False, 'message': 'Username already taken'}), 400
        UserModel.update_username(current_user['id'], new_username)

    if new_password:
        UserModel.update_password(current_user['id'], new_password)

    try:
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
