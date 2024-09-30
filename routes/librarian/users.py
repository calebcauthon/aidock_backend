from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from routes.shared.auth import librarian_required
from db.user_model import UserModel
from db.organization_model import OrganizationModel

librarian_users_routes = Blueprint('librarian_users', __name__)

@librarian_users_routes.route('/librarian/users')
@librarian_required
def librarian_users(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    users = UserModel.get_users_for_organization(librarian['organization_id'])
    return render_template('librarian/librarian_users.html', librarian=librarian, organization=organization, users=users)

@librarian_users_routes.route('/librarian/users/create', methods=['GET', 'POST'])
@librarian_required
def create_user(librarian):
    if request.method == 'POST':
        # Add user creation logic here
        UserModel.create_user(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
            role=request.form['role'],
            organization_id=librarian['organization_id']
        )
        return redirect(url_for('librarian_users.librarian_users'))
    return render_template('librarian/librarian_user_create.html', librarian=librarian)

@librarian_users_routes.route('/librarian/users/<int:user_id>/edit', methods=['GET', 'POST'])
@librarian_required
def edit_user(librarian, user_id):
    user = UserModel.get_user(user_id)
    if user['organization_id'] != librarian['organization_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        # Add user update logic here
        update_data = {
            'user_id': user_id,
            'username': request.form['username'],
            'email': request.form['email'],
            'role': request.form['role']
        }
        
        # Only update password if a new one is provided
        new_password = request.form.get('password')
        if new_password:
            update_data['password'] = new_password

        UserModel.update_user(**update_data)
        return redirect(url_for('librarian_users.librarian_users'))

    organization = OrganizationModel.get_organization(librarian['organization_id'])
    return render_template('librarian/librarian_user_edit.html', librarian=librarian, user=user, organization=organization)

@librarian_users_routes.route('/librarian/users/<int:user_id>/delete', methods=['POST'])
@librarian_required
def delete_user(librarian, user_id):
    user = UserModel.get_user(user_id)
    if user['organization_id'] != librarian['organization_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    UserModel.delete_user(user_id)
    return jsonify({'message': 'User deleted successfully'})
    return jsonify({'message': 'User deleted successfully'})