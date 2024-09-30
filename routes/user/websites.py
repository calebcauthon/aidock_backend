from flask import Blueprint, render_template, jsonify, request
from db.organization_model import OrganizationModel
from routes.shared.auth import user_required, authenticate_user_with_token

websites_bp = Blueprint('websites', __name__)

@websites_bp.route('/websites')
@user_required
def user_websites(user):
    websites = OrganizationModel.get_all_websites_for_organization(user['organization_id'])
    user_websites = OrganizationModel.get_user_websites(user['id'])

    for website in websites:
        user_website = next((uw for uw in user_websites if uw[1] == website['url']), None)
        if user_website and not user_website[2]:
            website['is_active'] = False
        else:
            website['is_active'] = True
    return render_template('user_websites.html', websites=websites, user=user, user_websites=user_websites)

@websites_bp.route('/api/user/websites/toggle', methods=['POST'])
@authenticate_user_with_token
def toggle_website(user):
    data = request.json
    website_url = data.get('website_url')
    is_active = data.get('is_active')

    if website_url is not None and is_active is not None:
        success = OrganizationModel.toggle_user_website(user['id'], website_url, is_active)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update website status'}), 500
    else:
        return jsonify({'success': False, 'message': 'Invalid request data'}), 400

@websites_bp.route('/api/user/websites/add', methods=['POST'])
@user_required
def add_website(user):
    data = request.json
    website_url = data.get('website_url')

    if website_url:
        success = OrganizationModel.add_user_website(user['id'], website_url)
        if success:
            return jsonify({'success': True, 'message': 'Website added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add website'}), 500
    else:
        return jsonify({'success': False, 'message': 'Website URL is required'}), 400

@websites_bp.route('/api/user/websites/remove', methods=['POST'])
@user_required
def remove_website(user):
    data = request.json
    website_url = data.get('website_url')

    if website_url:
        success = OrganizationModel.remove_user_website(user['id'], website_url)
        if success:
            return jsonify({'success': True, 'message': 'Website removed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to remove website'}), 500
    else:
        return jsonify({'success': False, 'message': 'Website URL is required'}), 400