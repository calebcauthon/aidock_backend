from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from db.init_db import create_connection, execute_sql
from ..shared.auth import platform_admin_required
from db.organization_model import OrganizationModel
from db.settings_model import SettingsModel


organization_routes = Blueprint('organization_routes', __name__)

@organization_routes.route('/', methods=['GET'])
@platform_admin_required
def list_organizations():
    conn = create_connection()
    if conn is not None:
        organizations_result = execute_sql(conn, "SELECT id, name, description FROM organizations ORDER BY name")
        organizations = [{"id": org[0], "name": org[1], "description": org[2]} for org in organizations_result]
        print(organizations)
        conn.close()
        return render_template('organizations/list.html', organizations=organizations)
    return jsonify({"error": "Unable to connect to the database"}), 500

@organization_routes.route('/create', methods=['GET', 'POST'])
@platform_admin_required
def create_organization():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        conn = create_connection()
        if conn is not None:
            execute_sql(conn, "INSERT INTO organizations (name, description) VALUES (?, ?)", (name, description))
            result = execute_sql(conn, "SELECT * FROM organizations WHERE name = ?", (name,))
            org_id = result[0][0]
            conn.close()

            # Create organization settings
            SettingsModel.create_organization_settings(org_id)

            return redirect(url_for('organization_routes.list_organizations'))
    return render_template('organizations/create.html')

@organization_routes.route('/<int:org_id>/edit', methods=['GET', 'POST'])
@platform_admin_required
def edit_organization(org_id):
    conn = create_connection()
    if conn is not None:
        if request.method == 'POST':
            data = request.json
            name = data.get('name')
            description = data.get('description')
            
            execute_sql(conn, "UPDATE organizations SET name = ?, description = ? WHERE id = ?", (name, description, org_id))
            conn.close()
            return redirect(url_for('organization_routes.list_organizations'))
        else:
            organization = execute_sql(conn, "SELECT * FROM organizations WHERE id = ?", (org_id,))
            
            # Fetch organization settings
            settings = SettingsModel.get_organization_settings(org_id)
            
            conn.close()
            return render_template('organizations/edit.html', 
                                   organization=organization[0] if organization else None,
                                   settings=settings)
    return jsonify({"error": "Unable to connect to the database"}), 500

@organization_routes.route('/<int:org_id>/delete', methods=['POST'])
@platform_admin_required
def delete_organization(org_id):
    conn = create_connection()
    if conn is not None:
        execute_sql(conn, "DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.close()
        return redirect(url_for('organization_routes.list_organizations'))
    return jsonify({"error": "Unable to connect to the database"}), 500

@organization_routes.route('/<int:org_id>', methods=['GET'])
@platform_admin_required
def view_organization(org_id):
    conn = create_connection()
    if conn is not None:
        organization = execute_sql(conn, "SELECT * FROM organizations WHERE id = ?", (org_id,))
        if organization:
            # Fetch users belonging to this organization
            users = execute_sql(conn, "SELECT id, username, email, role FROM users WHERE organization_id = ?", (org_id,))
            conn.close()
            return render_template('superuser_ui/view_organization.html', organization=organization[0], users=users)
    conn.close()
    return jsonify({"error": "Organization not found"}), 404

platform_admin_pages = Blueprint('platform_admin_pages', __name__)
@platform_admin_pages.route('/api/organization/<int:org_id>/websites', methods=['GET'])
@platform_admin_required
def get_organization_websites(org_id):
    print(f"org_id: {org_id}")
    try:
        websites = OrganizationModel.get_organization_websites(org_id)
        return jsonify(websites)
    except Exception as e:
        raise e
        return jsonify({"error": str(e)}), 500

@platform_admin_pages.route('/api/organization/<int:org_id>/websites', methods=['POST'])
@platform_admin_required
def add_organization_website(org_id):
    try:
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"success": False, "message": "URL is required"}), 400
        
        OrganizationModel.add_organization_website(org_id, url)
        return jsonify({"success": True, "message": "Website added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@platform_admin_pages.route('/api/organization/<int:org_id>/websites/<int:website_id>', methods=['DELETE'])
@platform_admin_required
def remove_organization_website(org_id, website_id):
    try:
        entry = OrganizationModel.get_organization_website_entry(website_id)
        url = entry['url']
        OrganizationModel.remove_organization_website(org_id, url)
        return jsonify({"success": True, "message": "Website removed successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@platform_admin_pages.route('/api/organization/<int:org_id>/refresh-settings', methods=['POST'])
@platform_admin_required
def refresh_organization_settings(org_id):
    try:
        # Get all default settings
        default_settings = SettingsModel.get_default_settings()
        
        # Get current organization settings
        current_settings = SettingsModel.get_organization_settings(org_id)
        current_setting_names = {setting['name'] for setting in current_settings}
        
        # Add missing settings
        for default_setting in default_settings:
            if default_setting['name'] not in current_setting_names:
                SettingsModel.update_organization_setting(org_id, default_setting['name'], default_setting['default_value'])
        
        return jsonify({"success": True, "message": "Settings refreshed successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
