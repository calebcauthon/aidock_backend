from flask import Blueprint, render_template, request, jsonify
from db.settings_model import SettingsModel
from ..shared.auth import librarian_required

librarian_settings = Blueprint('librarian_settings', __name__)

@librarian_settings.route('/settings', methods=['GET'])
@librarian_required
def settings_page(librarian):
    organization_id = librarian['organization_id']
    settings = SettingsModel.get_organization_settings(organization_id)
    return render_template('librarian/settings.html', settings=settings, librarian=librarian)

@librarian_settings.route('/api/settings', methods=['POST'])
@librarian_required
def update_setting(librarian):
    organization_id = librarian['organization_id']
    data = request.json
    name = data.get('name')
    value = data.get('value')
    
    if not name or value is None:
        return jsonify({"success": False, "message": "Name and value are required"}), 400

    SettingsModel.update_organization_setting(organization_id, name, value)
    return jsonify({"success": True, "message": "Setting updated successfully"})