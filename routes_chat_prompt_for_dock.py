from flask import Blueprint, request, jsonify
from db.init_db import create_connection
from routes_auth_helpers import authenticate_user_with_token
from helpers_for_inference.prompt import get_system_prompt
from prompting.claude import prompt_claude
from db.prompt_history import save_prompt_history

chat_prompt_routes = Blueprint('chat_prompt_routes', __name__)

@chat_prompt_routes.route('/ask', methods=['POST'])
@authenticate_user_with_token
def ask_claude(user):
    data = request.get_json()
    question = data.get('question')
    url = data.get('url')
    page_title = data.get('pageTitle')
    selected_text = data.get('selectedText')
    active_element = data.get('activeElement')
    scroll_position = data.get('scrollPosition')
    conversation_messages = data.get('conversationMessages', [])

    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        system_prompt = construct_system_prompt(user, url, page_title, selected_text, active_element, scroll_position, conversation_messages)
        
        answer = prompt_claude(system_prompt, question)
        
        save_prompt_history(url, system_prompt, question, answer, user['id'])

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def construct_system_prompt(user, url, page_title, selected_text, active_element, scroll_position, conversation_messages):
    system_prompt = get_system_prompt(user['organization_id'], url, page_title, selected_text, active_element, scroll_position)
    system_prompt += f"User: {user}"
    
    conversation_context = "\n\nPrevious conversation:\n"
    for msg in conversation_messages:
        conversation_context += f"{msg['type'].capitalize()}: {msg['content']}\n"
    
    system_prompt += conversation_context
    return system_prompt