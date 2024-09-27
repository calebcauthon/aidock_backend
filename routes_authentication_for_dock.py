from flask import Blueprint, request, redirect, url_for, render_template, flash, session, jsonify
from werkzeug.security import check_password_hash
from db.user_model import UserModel
from db.organization_model import OrganizationModel
import uuid

auth_dock = Blueprint('auth_dock', __name__)

@auth_dock.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user = UserModel.get_user_by_username(username)
    
    if user and check_password_hash(user['password_hash'], password):
        organization = OrganizationModel.get_organization(user['organization_id'])
        login_token = str(uuid.uuid4())
        UserModel.update_login_token(user['id'], login_token)
        return jsonify({
            "message": "Authentication successful",
            "token": login_token,
            "role": user['role'],
            "organization_id": user['organization_id'],
            "organization_name": organization['name'] if organization else None
        }), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

@auth_dock.route('/verify', methods=['POST'])
def verify_token():
    data = request.json
    login_token = data.get('token')
    
    if not login_token:
        return jsonify({"error": "Missing login token"}), 400
    
    user = UserModel.get_user_by_login_token(login_token)
    
    if user:
        return jsonify({"isValid": True}), 200
    else:
        return jsonify({"isValid": False}), 200