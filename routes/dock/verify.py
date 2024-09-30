from flask import Blueprint, request, jsonify
from db.organization_model import OrganizationModel
from db.user_model import UserModel
verify_website = Blueprint('verify_website', __name__)

@verify_website.route('/api/websites', methods=['GET'])
def check_website():
    current_url = request.args.get('url')
    org_id = request.args.get('organization_id')
    user_id = request.args.get('user_id')
    username = request.args.get('username')

    if not current_url or not org_id or (not user_id and not username):
        return jsonify({"error": "URL, organization_id, and either user_id or username parameters are required"}), 400

    if not current_url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        if username and not user_id:
            user = UserModel.get_user_by_username(username)
            if not user:
                return jsonify({"error": "User not found"}), 404
            user_id = user['id']

        organization_id = OrganizationModel.check_website(current_url, org_id, user_id)
        if organization_id:
            return jsonify({"is_organization_website": True, "organization_id": organization_id})
        else:
            return jsonify({"is_organization_website": False})
    except Exception as e:
        raise e