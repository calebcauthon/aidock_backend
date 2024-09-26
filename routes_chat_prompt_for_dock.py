from flask import Blueprint, request, jsonify
from db.init_db import create_connection
from routes_auth_helpers import authenticate_user_with_token
from prompting.claude import prompt_claude
from db.prompt_history import save_prompt_history

chat_prompt_routes = Blueprint('chat_prompt_routes', __name__)

@chat_prompt_routes.route('/ask', methods=['POST'])
@authenticate_user_with_token
def ask_claude(user):
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        prompt_data = {
            'user': user,
            'url': data.get('url'),
            'page_title': data.get('pageTitle'),
            'selected_text': data.get('selectedText'),
            'active_element': data.get('activeElement'),
            'scroll_position': data.get('scrollPosition'),
            'conversation_messages': data.get('conversationMessages', []),
            'question': question
        }
        
        answer = prompt_claude(prompt_data)
        
        save_prompt_history(prompt_data['url'], prompt_data, question, answer, user['id'])

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500