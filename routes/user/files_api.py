from flask import Blueprint, jsonify, abort
from routes.shared.auth import authenticate_user_with_token 
from db.file_model import FileModel
from db.user_model import UserModel

files_api = Blueprint('files_api', __name__)

@files_api.route('/user-files', methods=['GET'])
@authenticate_user_with_token
def list_user_files(user):
    try:
        # Get the user's organization
        organization_id = user['organization_id']
        files = FileModel.get_files_for_organization(organization_id)
        
        return jsonify({
            "files": files
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@files_api.route('/preview-file/<int:file_id>', methods=['GET'])
@authenticate_user_with_token
def preview_file(user, file_id):
    try:
        # Get the user's organization
        organization_id = user['organization_id']
        
        # Get the file
        file = FileModel.get_file_by_id(file_id)
        
        # Check if the file belongs to the user's organization
        if file['organization_id'] != organization_id:
            abort(403)  # Forbidden
        
        return jsonify({
            "name": file['file_name'],
            "content": file['text_content']
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
