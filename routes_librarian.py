from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from routes_auth_helpers import librarian_required
from db.organization_model import OrganizationModel
from db.conversation_model import ConversationModel
from db.context_docs import ContextDocModel
from db.file_model import FileModel  # Add this import
from db.user_model import UserModel
from flask_login import current_user, login_required
import os

librarian_routes = Blueprint('librarian', __name__)

@librarian_routes.route('/librarian')
@librarian_required
def librarian_home(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    recent_conversations = ConversationModel.get_conversations_for_organization(librarian['organization_id'])
    total_prompt_history_count = ConversationModel.getTotalPromptHistoryEntriesForOrganization(librarian['organization_id'])
    conversation_and_question_count_for_all_users = ConversationModel.get_conversation_and_question_count_for_all_users(librarian['organization_id'])

    return render_template('librarian/librarian_home.html', librarian=librarian, organization=organization, recent_conversations=recent_conversations, total_prompt_history_count=total_prompt_history_count, conversation_and_question_count_for_all_users=conversation_and_question_count_for_all_users)

@librarian_routes.route('/librarian/upload', methods=['POST'])
@librarian_required
def upload_file(librarian):
    if 'file' not in request.files:
        return redirect(url_for('librarian.librarian_files'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('librarian.librarian_files'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Read the content of the file
    with open(file_path, 'rb') as f:
        binary_content = f.read()
    
    # Try to read the file as text
    try:
        with open(file_path, 'r') as f:
            text_content = f.read()
    except UnicodeDecodeError:
        text_content = None  # File is not readable as text
    
    # Add the file to the files table
    FileModel.add_file(
        organization_id=librarian['organization_id'],
        user_upload_id=librarian['id'],
        binary_content=binary_content,
        text_content=text_content,
        file_name=filename,
        file_size=os.path.getsize(file_path)
    )

    # Add the file to context docs if it's readable as text
    if text_content:
        ContextDocModel.add_context_doc(
            organization_id=librarian['organization_id'],
            url='*',  # Using '*' to make it available for all URLs
            document_name=filename,
            document_text=text_content
        )

    return redirect(url_for('librarian.librarian_files'))

@librarian_routes.route('/librarian-files')
@librarian_required
def librarian_files(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    files = FileModel.get_files_for_organization(librarian['organization_id'])
    return render_template('librarian/librarian_files.html', librarian=librarian, organization=organization, files=files)

@librarian_routes.route('/librarian/files', methods=['GET'])
@librarian_required
def get_organization_files(librarian):
    org_id = librarian['organization_id']
    
    files = FileModel.get_files_for_organization(org_id)
    users = UserModel.get_all_users()
    users_dict = {user['id']: user['username'] for user in users}
    print(f"users_dict: {users_dict}")
    
    file_list = []
    for file in files:
        file_list.append({
            'id': file['id'],
            'name': file['file_name'],
            'size': file['file_size'],
            'upload_date': file['timestamp_of_upload'],
            'uploaded_by': file['user_upload_id'],
            'user_name': users_dict[file['user_upload_id']]
        })
    
    return jsonify(file_list)

@librarian_routes.route('/librarian/delete_file/<int:file_id>', methods=['POST'])
@librarian_required
def delete_file(librarian,file_id):
    file = FileModel.get_file_by_id(file_id)
    
    if file and file['organization_id'] == librarian['organization_id']:
        if FileModel.delete_file(file_id):
            return jsonify({'success': True, 'message': 'File deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete file'}), 500
    else:
        return jsonify({'success': False, 'message': 'File not found or you do not have permission to delete it'}), 404
