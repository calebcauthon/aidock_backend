from flask import Blueprint, render_template
from routes_auth_helpers import librarian_required
from db.organization_model import OrganizationModel

librarian_routes = Blueprint('librarian', __name__)

@librarian_routes.route('/librarian')
@librarian_required
def librarian_home(librarian):
    organization = OrganizationModel.get_organization(librarian['organization_id'])
    return render_template('librarian/librarian_home.html', librarian=librarian, organization=organization)
