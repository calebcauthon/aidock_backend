from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
from db.user_model import UserModel
from db.init_db import create_connection, execute_sql
from routes_authentication_for_dock import platform_admin_required

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/', methods=['GET'])
@platform_admin_required
def list_users():
    users = UserModel.get_all_users()
    return render_template('superuser_ui/users.html', users=users)

@user_routes.route('/<int:user_id>', methods=['GET'])

def get_user(user_id):
    user = UserModel.get_user(user_id)
    if user:
        return render_template('superuser_ui/user_detail.html', user=user)
    return jsonify({"error": "User not found"}), 404

@user_routes.route('/create', methods=['GET', 'POST'])
@platform_admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        organization_id = request.form.get('organization_id')
        
        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
        
        try:
            UserModel.create_user(username, email, password, role, organization_id)
            return redirect(url_for('user_routes.list_users'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('superuser_ui/create_user.html')

@user_routes.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@platform_admin_required
def edit_user(user_id):
    user = UserModel.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        organization_id = request.form.get('organization_id')
        new_password = request.form.get('new_password')
        
        try:
            UserModel.update_user(user_id, username, email, role, organization_id)
            
            # Update password if a new one is provided
            if new_password:
                UserModel.update_password(user_id, new_password)
            
            return redirect(url_for('user_routes.list_users'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('superuser_ui/edit_user.html', user=user)

@user_routes.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        UserModel.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user = UserModel.get_user_by_username(username)
    
    if user and check_password_hash(user['password_hash'], password):
        login_token = str(uuid.uuid4())
        UserModel.update_login_token(user['id'], login_token)
        return jsonify({"message": "Authentication successful", "token": login_token}), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

@user_routes.route('/initialize_super_user', methods=['GET'])
def initialize_super_user():
    try:
        # Check if there are any existing users
        existing_users = UserModel.get_all_users()
        
        if not existing_users:
            # If no users exist, create a super user
            username = "admin"
            email = "admin@example.com"
            password = "changeme"
            role = "platform_admin"
            
            # Create the super user
            UserModel.create_user(username, email, password, role)

            return jsonify({"message": "Super user initialized successfully"}), 201
        else:
            return jsonify({"message": "Users already exist. Super user not created."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to initialize super user: {str(e)}"}), 500
