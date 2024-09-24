from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes_auth_helpers import platform_admin_required
from db.file_model import FileModel
from db.organization_model import OrganizationModel
from db.user_model import UserModel

files_routes = Blueprint('files', __name__)

@files_routes.route('/files')
@platform_admin_required
def list_files():
    organizations = OrganizationModel.get_all_organizations()
    organizations_dict = {org['id']: org['name'] for org in organizations}

    users = UserModel.get_all_users()
    users_dict = {user['id']: user['username'] for user in users}
    files = FileModel.get_all_files()
    return render_template('superuser_ui/files.html', organizations=organizations_dict, users=users_dict, files=files)

@files_routes.route('/files/delete/<int:file_id>', methods=['POST'])
@platform_admin_required
def delete_file(file_id):
    print(f"Deleting file with ID: {file_id}")
    if FileModel.delete_file(file_id):
        flash('File deleted successfully', 'success')
    else:
        flash('Failed to delete file', 'error')
    return redirect(url_for('files.superuser_files'))