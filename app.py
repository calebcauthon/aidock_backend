from flask import Flask, request, jsonify, send_from_directory, render_template, url_for

import os
import anthropic
from flask_cors import CORS
from helpers_for_inference.prompt import get_system_prompt
from routes_context_docs_for_platform_admin import context_docs, create_connection
from routes_title_prompt_for_dock import prompt_routes
from routes_user_crud_for_platform_admin import user_routes
from routes_organization_crud_for_platform_admin import organization_routes
from db.init_db import create_table
import psycopg2
from routes_authentication_for_dock import auth, login_required, platform_admin_required
from functools import wraps
from db.prompt_history import Datastore as PromptHistoryDatastore

app = Flask(__name__, static_folder='templates')
app.template_folder = 'templates'
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Database connection function
def create_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        return psycopg2.connect(db_url)
    else:
        # Fallback to SQLite
        import sqlite3
        return sqlite3.connect('lavendel.db')

# Initialize database
conn = create_connection()
if conn is not None:
    create_table(conn)
    conn.close()
else:
    print("Error! Cannot create the database connection.")

app.register_blueprint(context_docs, url_prefix='/context_docs')
app.register_blueprint(prompt_routes)
app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(organization_routes, url_prefix='/organizations')
app.register_blueprint(auth)

app.secret_key = os.environ.get("SECRET_KEY", "your_fallback_secret_key")

@app.route('/hello')
def hello_world():
    return "Hello, World!"

def authenticate_user_with_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        from functools import wraps
        from db.user_model import UserModel

        print("All headers:")
        for header, value in request.headers.items():
            print(f"{header}: {value}")
        login_token = request.headers.get('login_token')
        if not login_token:
            return jsonify({"error": "No login token provided"}), 401
        
        user = UserModel.get_user_by_login_token(login_token)
        if not user:
            return jsonify({"error": "Invalid login token"}), 401
        
        return func(user, *args, **kwargs)
    return wrapper

@app.route('/ask', methods=['POST'])
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

@app.route('/history')
def prompt_history():
    conn = create_connection()
    datastore = PromptHistoryDatastore(conn)

    offset = request.args.get('offset', type=int, default=0)
    limit = 1

    history = datastore.get_prompt_history(offset, limit)
    return render_template('superuser_ui/prompt_history.html', 
                            entry=history['entry'],
                            has_prev=history['has_prev'],
                            has_next=history['has_next'],
                            prev_offset=history['prev_offset'],
                            next_offset=history['next_offset'])

@app.route('/context_docs/<int:doc_id>', methods=['GET'])
def get_context_document(doc_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM context_docs WHERE id = ?", (doc_id,))
            doc = cursor.fetchone()
            cursor.close()
            if doc:
                return jsonify({
                    'id': doc[0],
                    'url': doc[1],
                    'document_name': doc[2],
                    'document_text': doc[3],
                    'scope': doc[4],  # Assuming you have a scope column
                    # Add other fields as necessary
                })
            else:
                return jsonify({"error": "Document not found"}), 404
        except (psycopg2.Error) as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)