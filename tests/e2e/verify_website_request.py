import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

import subprocess
import json
from db.organization_model import OrganizationModel
from db.user_model import UserModel

def send_verify_website_request(url, org_name, username):
    # Get organization ID from name
    org = OrganizationModel.get_organization_by_name(org_name)
    if not org:
        print(f"Organization '{org_name}' not found")
        sys.exit(1)
    org_id = org['id']

    # Get user ID from username
    user = UserModel.get_user_by_username(username)
    if not user:
        print(f"User '{username}' not found")
        sys.exit(1)
    user_id = user['id']

    base_url = f'http://localhost:5000/api/websites?url={url}&organization_id={org_id}&user_id={user_id}'
    
    curl_command = [
        'curl', '-X', 'GET', base_url,
        '-H', 'Content-Type: application/json'
    ]
    
    result = subprocess.run(curl_command, capture_output=True, text=True)
    return result.stdout

def main():
    if len(sys.argv) != 4:
        print("Usage: python verify_website_request.py <url> <organization_name> <username>")
        sys.exit(1)
    
    url = sys.argv[1]
    org_name = sys.argv[2]
    username = sys.argv[3]
    
    response = send_verify_website_request(url, org_name, username)
    print(f"Response: {response}")
    
    if response:
        print("\u2705 Response received successfully")
        try:
            response_data = json.loads(response)
            if 'is_organization_website' in response_data:
                print("\u2705 Website verification status found in the response")
                if response_data['is_organization_website']:
                    print("\u2705 Website is verified as an organization website")
                    if 'organization_id' in response_data:
                        print(f"\u2705 Organization ID: {response_data['organization_id']}")
                    else:
                        print("\u274C Organization ID not found in the response")
                else:
                    print("\u2705 Website is not an organization website")
            else:
                print("\u274C Website verification status not found in the response")
        except json.JSONDecodeError:
            print("\u274C Failed to parse the response as JSON")
    else:
        print("\u274C No response received")


if __name__ == "__main__":
    main()