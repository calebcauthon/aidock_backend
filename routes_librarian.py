from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from routes_auth_helpers import librarian_required
from db.organization_model import OrganizationModel
from db.conversation_model import ConversationModel
from db.context_docs import ContextDocModel
from db.file_model import FileModel  # Add this import
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
        text_content=text_content
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

@librarian_routes.route('/librarian/files')
@librarian_required
def librarian_files(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    files = FileModel.get_files_for_organization(librarian['organization_id'])
    return render_template('librarian/librarian_files.html', librarian=librarian, organization=organization, files=files)
