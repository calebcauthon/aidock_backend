import sys
import os
import base64

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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_chat_request(login_token):
    # Read and encode the image
    image_path = os.path.join(project_root, 'tests', 'e2e', 'sales_flow.png')
    base64_image = encode_image(image_path)

    curl_command = [
        'curl', '-X', 'POST', 'http://localhost:5000/ask',
        '-H', 'Content-Type: application/json',
        '-H', f'Login-Token: {login_token}',
        '-d', json.dumps({
            "question": "Which roles are part of the workshop phase?",
            "url": "https://example.com/page",
            "pageTitle": "Example Page",
            "selectedText": "Some selected text on the page",
            "activeElement": "body > div.content > p",
            "scrollPosition": 500,
            "conversationMessages": [
                {
                    "type": "user",
                    "content": [
                        {"type": "text", "text": "Here's a sales flow diagram:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        }
                    ],
                },
                {
                    "type": "user",
                    "content": "Which roles are part of the workshop phase?"
                }
            ]
        })
    ]
    
    result = subprocess.run(curl_command, capture_output=True, text=True)
    return result.stdout

def main():
    if len(sys.argv) != 2:
        print("Usage: python chat_request.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    login_token = get_login_token(username)
    print(f"username: {username}, login_token: {login_token}")
    response = send_chat_request(login_token)
    print(f"response: {response}")
    if response:

        print("\u2705 Response received successfully")
        try:
            response_data = json.loads(response)
            if 'answer' in response_data and isinstance(response_data['answer'], str) and len(response_data['answer']) > 0:
                print("\u2705 Answer found in the response")
            else:
                print("\u274C No valid answer found in the response")
        except json.JSONDecodeError:
            print("\u274C Failed to parse the response as JSON")
    else:
        print("\u274C No response received")

if __name__ == "__main__":
    main()