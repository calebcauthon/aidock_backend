from flask import Blueprint, render_template, jsonify, request
from db.organization_model import OrganizationModel
from routes.shared.auth import user_required, authenticate_user_with_token

websites_bp = Blueprint('websites', __name__)

@websites_bp.route('/websites')
@user_required
def user_websites(user):
    websites = OrganizationModel.get_user_websites(user['id'])
    overrides = OrganizationModel.get_user_website_overrides(user['id'])

    # Create a dictionary of website statuses
    website_statuses = {website['id']: True for website in websites}

    # Update statuses based on overrides
    for override in overrides:
        if not override['is_active']:
            website_statuses[override['id']] = False
    
    # Update the websites list with the correct status
    for website in websites:
        website['is_active'] = website_statuses[website['id']]

    return render_template('user_websites.html', websites=websites, user=user)

@websites_bp.route('/api/user/websites/toggle', methods=['POST'])
@authenticate_user_with_token
def toggle_website(user):
    data = request.json
    website_id = data.get('website_id')
    is_active = data.get('is_active')

    if website_id is not None and is_active is not None:
        success = OrganizationModel.toggle_user_website(user['id'], website_id, is_active)
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
    website_id = data.get('website_id')

    if website_id:
        success = OrganizationModel.add_user_website(user['id'], website_id)
        if success:
            return jsonify({'success': True, 'message': 'Website added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add website'}), 500
    else:
        return jsonify({'success': False, 'message': 'Website ID is required'}), 400

@websites_bp.route('/api/user/websites/remove', methods=['POST'])
@user_required
def remove_website(user):
    data = request.json
    website_id = data.get('website_id')

    if website_id:
        success = OrganizationModel.remove_user_website(user['id'], website_id)
        if success:
            return jsonify({'success': True, 'message': 'Website removed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to remove website'}), 500
    else:
        return jsonify({'success': False, 'message': 'Website ID is required'}), 400