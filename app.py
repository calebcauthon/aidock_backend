from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import anthropic
from flask_cors import CORS
from prompt import get_system_prompt
from context_docs_routes import context_docs, create_connection
from prompt_routes import prompt_routes  # Add this import
from init_db import create_table
from datetime import datetime
import psycopg2
from psycopg2 import sql

app = Flask(__name__, static_folder='lavendel_frontend')
app.template_folder = 'lavendel_frontend'
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

# Register the context_docs blueprint
app.register_blueprint(context_docs, url_prefix='/context_docs')

# Register the prompt_routes blueprint
app.register_blueprint(prompt_routes)

@app.route('/hello')
def hello_world():
    return "Hello, World!"

@app.route('/ask', methods=['POST'])
def ask_claude():
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
        system_prompt = get_system_prompt(url, page_title, selected_text, active_element, scroll_position)
        
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
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("INSERT INTO prompt_history (url, prompt, response) VALUES (%s, %s, %s)"),
                    (url, f"SYSTEM PROMPT: {system_prompt} | USER QUESTION: {question}", answer)
                )
            conn.commit()
            conn.close()

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def prompt_history():
    conn = create_connection()
    if conn is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM prompt_history ORDER BY timestamp DESC")
            history = cur.fetchall()
        conn.close()
        return render_template('prompt_history.html', history=history)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

@app.route('/context_docs/<int:doc_id>', methods=['GET'])
def get_context_document(doc_id):
    conn = create_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM context_docs WHERE id = %s", (doc_id,))
                doc = cur.fetchone()
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

@app.route('/authenticate', methods=['POST'])
def authenticate():
    return jsonify({
        "status": "success",
        "message": "Authentication successful"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)