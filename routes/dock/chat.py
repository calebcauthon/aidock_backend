import os
from flask import Blueprint, request, jsonify
from routes.shared.auth import authenticate_user_with_token
from prompting.hub import execute_prompt
from db.prompt_history import save_prompt_history
import anthropic

chat = Blueprint('chat', __name__)

@chat.route('/ask', methods=['POST'])
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
        
        answer = execute_prompt('claude', prompt_data)
        
        save_prompt_history(prompt_data['url'], prompt_data, question, answer, user['id'])

        return jsonify({"answer": answer})
    except Exception as e:
        raise e
        return jsonify({"error": str(e)}), 500

prompt_routes = Blueprint('prompt_routes', __name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@prompt_routes.route('/prompt', methods=['POST'])
def prompt():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400

    try:
        prompt_text = f"""
        The user has asked the following question: {question}
        And the AI has answered: {answer}
        Come up with a short title to label this conversation and distinguish it from other conversations.
        Dont say 'question about', just get right to the abstract concept being discussed.
"""
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            system=prompt_text,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        summary = response.content[0].text.strip()

        return jsonify({"title": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
