from flask import Blueprint, render_template, request, jsonify
from db.settings_model import SettingsModel
from ..shared.auth import platform_admin_required

admin_settings = Blueprint('admin_settings', __name__)

@admin_settings.route('/settings', methods=['GET'])
@platform_admin_required
def settings_page():
    settings = SettingsModel.get_default_settings()
    return render_template('admin/settings.html', settings=settings)

@admin_settings.route('/api/settings', methods=['POST'])
@platform_admin_required
def add_setting():
    data = request.json
    name = data.get('name')
    default_value = data.get('default_value')
    description = data.get('description')
    
    if not name or default_value is None:
        return jsonify({"success": False, "message": "Name and default value are required"}), 400

    SettingsModel.add_default_setting(name, default_value, description)
    return jsonify({"success": True, "message": "Setting added successfully"})

@admin_settings.route('/api/settings/<name>', methods=['PUT'])
@platform_admin_required
def update_setting(name):
    data = request.json
    default_value = data.get('default_value')
    description = data.get('description')
    
    if default_value is None:
        return jsonify({"success": False, "message": "Default value is required"}), 400

    SettingsModel.update_default_setting(name, default_value, description)
    return jsonify({"success": True, "message": "Setting updated successfully"})