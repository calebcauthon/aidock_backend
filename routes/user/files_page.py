from flask import Blueprint, render_template
from routes.shared.auth import user_required
from db.file_model import FileModel
from db.organization_model import OrganizationModel

files_page = Blueprint('files_page', __name__)

@files_page.route('/user/files')
@user_required
def user_files(user):
    # Get the user's organization
    organization_id = user['organization_id']
    
    # Get files for the organization
    files = FileModel.get_files_for_organization(organization_id)
    organization = OrganizationModel.get_organization(organization_id)
    
    return render_template('user_files.html', files=files, user=user, organization=organization)
