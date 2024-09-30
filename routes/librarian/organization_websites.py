from flask import Blueprint, render_template, request, jsonify
from db.organization_model import OrganizationModel
from routes.shared.auth import librarian_required

librarian_websites_bp = Blueprint('librarian_websites', __name__)

@librarian_websites_bp.route('/librarian/websites', methods=['GET'])
@librarian_required
def organization_websites_page(librarian_user):
    org_id = librarian_user['organization_id']
    org_model = OrganizationModel()
    websites = org_model.get_organization_websites(org_id)
    return render_template('librarian_websites.html', websites=websites, librarian_user=librarian_user)

@librarian_websites_bp.route('/api/librarian/websites/add', methods=['POST'])
@librarian_required
def add_organization_website(librarian_user):
    org_id = librarian_user['organization_id']
    website_url = request.json.get('website_url')
    org_model = OrganizationModel()
    success = org_model.add_organization_website(org_id, website_url)
    return jsonify({'success': success})

@librarian_websites_bp.route('/api/librarian/websites/remove', methods=['POST'])
@librarian_required
def remove_organization_website(librarian_user):
    org_id = librarian_user['organization_id']
    website_url = request.json.get('website_url')
    org_model = OrganizationModel()
    success = org_model.remove_organization_website(org_id, website_url)
    return jsonify({'success': success})