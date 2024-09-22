from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from db.init_db import create_connection, execute_sql
from routes_auth_helpers import authenticate_user_with_token
from helpers_for_inference.prompt import get_system_prompt
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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
        system_prompt = get_system_prompt(user['organization_id'], url, page_title, selected_text, active_element, scroll_position)
        system_prompt += f"User: {user}"
        
        # Add conversation context to the system prompt
        conversation_context = "\n\nPrevious conversation:\n"
        for msg in conversation_messages:
            conversation_context += f"{msg['type'].capitalize()}: {msg['content']}\n"
        
        system_prompt += conversation_context

        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = response.content[0].text

        # Save prompt and response to history
        conn = create_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO prompt_history (url, prompt, response) VALUES (?, ?, ?)",
                (url, f"SYSTEM PROMPT: {system_prompt} | USER QUESTION: {question}", answer)
            )
            conn.commit()
            cur.close()
            conn.close()

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500