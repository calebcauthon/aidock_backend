import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

import subprocess
import json
from db.init_db import create_connection

def get_login_token(username):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT login_token FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
    return None

def send_list_files_request(login_token):
    curl_command = [
        'curl', '-X', 'GET', 'http://localhost:5000/user-files',
        '-H', f'Login-Token: {login_token}'
    ]
    
    result = subprocess.run(curl_command, capture_output=True, text=True)
    return result.stdout

def main():
    if len(sys.argv) != 2:
        print("Usage: python list_files_request.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    login_token = get_login_token(username)
    print(f"login_token: {login_token}")
    
    response = send_list_files_request(login_token)
    print(f"response: {response}")
    
    if response:
        print("\u2705 Response received successfully")
        try:
            response_data = json.loads(response)
            if 'files' in response_data and isinstance(response_data['files'], list):
                print(f"\u2705 Files list found in the response. Total files: {len(response_data['files'])}")
                for file in response_data['files']:
                    print(f"  - {file['file_name']} (ID: {file['id']})")
            else:
                print("\u274C No valid files list found in the response")
        except json.JSONDecodeError:
            print("\u274C Failed to parse the response as JSON")
    else:
        print("\u274C No response received")

if __name__ == "__main__":
    main()