from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import anthropic
from flask_cors import CORS
from prompt import get_system_prompt
from context_docs_routes import context_docs, create_connection
from init_db import create_table
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='lavendel_frontend')
app.template_folder = 'lavendel_frontend'
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Initialize database
conn = create_connection()
if conn is not None:
    create_table(conn)
    conn.close()
else:
    print("Error! Cannot create the database connection.")

# Register the context_docs blueprint
app.register_blueprint(context_docs, url_prefix='/context_docs')

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

    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        system_prompt = get_system_prompt(url, page_title, selected_text, active_element, scroll_position)
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
            c = conn.cursor()
            c.execute('''INSERT INTO prompt_history (url, prompt, response)
                         VALUES (?, ?, ?)''', (url, f"SYSTEM PROMPT: {system_prompt} | USER QUESTION: {question}", answer))
            conn.commit()
            conn.close()

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def prompt_history():
    conn = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute('''SELECT * FROM prompt_history ORDER BY timestamp DESC''')
        history = c.fetchall()
        conn.close()
        return render_template('prompt_history.html', history=history)
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

@app.route('/edit_doc/<int:doc_id>')
def edit_doc_page(doc_id):
    return send_from_directory(app.static_folder, 'edit_doc.html')

@app.route('/docs')
def serve_docs():
    return send_from_directory(app.static_folder, 'context_docs.html')

if __name__ == '__main__':
    app.run(debug=True)