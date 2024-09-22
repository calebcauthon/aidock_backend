from flask import Blueprint, render_template
from routes_auth_helpers import librarian_required
from db.organization_model import OrganizationModel
from db.conversation_model import ConversationModel

librarian_routes = Blueprint('librarian', __name__)

@librarian_routes.route('/librarian')
@librarian_required
def librarian_home(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    recent_conversations = ConversationModel.get_conversations_for_organization(librarian['organization_id'])
    total_prompt_history_count = ConversationModel.getTotalPromptHistoryEntriesForOrganization(librarian['organization_id'])
    return render_template('librarian/librarian_home.html', librarian=librarian, organization=organization, recent_conversations=recent_conversations, total_prompt_history_count=total_prompt_history_count)
