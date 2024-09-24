from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from routes_auth_helpers import librarian_required
from db.organization_model import OrganizationModel
from db.conversation_model import ConversationModel
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
    print("Request: ", request)
    print("Request files: ", request.files.getlist('file'))

    if 'file' not in request.files:
        return redirect(url_for('librarian.librarian_files'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('librarian.librarian_files'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Read the content of the file
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Add the file to context docs
    from db.context_docs import ContextDocModel
    ContextDocModel.add_context_doc(
        organization_id=librarian['organization_id'],
        url='*',  # Using '*' to make it available for all URLs
        document_name=filename,
        document_text=file_content
    )

    return redirect(url_for('librarian.librarian_files'))

@librarian_routes.route('/librarian/files')
@librarian_required
def librarian_files(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    # TODO: Fetch files data for the organization
    files = []  # Placeholder for files data
    return render_template('librarian/librarian_files.html', librarian=librarian, organization=organization, files=files)
