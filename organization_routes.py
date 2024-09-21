from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from init_db import create_connection, execute_sql
from auth import platform_admin_required

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

            return redirect(url_for('organization_routes.list_organizations'))
    return render_template('organizations/create.html')

@organization_routes.route('/<int:org_id>/edit', methods=['GET', 'POST'])
@platform_admin_required
def edit_organization(org_id):
    conn = create_connection()
    if conn is not None:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            
            execute_sql(conn, "UPDATE organizations SET name = ?, description = ? WHERE id = ?", (name, description, org_id))
            conn.close()
            return redirect(url_for('organization_routes.list_organizations'))
        else:
            organization = execute_sql(conn, "SELECT * FROM organizations WHERE id = ?", (org_id,))
            conn.close()
            return render_template('organizations/edit.html', organization=organization[0] if organization else None)
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