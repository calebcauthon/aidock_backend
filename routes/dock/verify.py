from flask import Blueprint, request, jsonify
from db.organization_model import OrganizationModel

verify_website = Blueprint('verify_website', __name__)

@verify_website.route('/api/websites', methods=['GET'])
def check_website():
    current_url = request.args.get('url')
    org_id = request.args.get('organization_id')
    user_id = request.args.get('user_id')
    if not current_url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        organization_id = OrganizationModel.check_website(current_url, org_id, user_id)
        if organization_id:
            return jsonify({"is_organization_website": True, "organization_id": organization_id})
        else:
            return jsonify({"is_organization_website": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
