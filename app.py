from flask import Flask, request, jsonify, send_from_directory
import os
import anthropic
from flask_cors import CORS
from prompt import get_system_prompt
from context_docs_routes import context_docs, create_connection
from init_db import create_table

app = Flask(__name__, static_folder='lavendel_frontend')
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
        return jsonify({"answer": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_doc/<int:doc_id>')
def edit_doc_page(doc_id):
    return send_from_directory(app.static_folder, 'edit_doc.html')

@app.route('/docs')
def serve_docs():
    return send_from_directory(app.static_folder, 'context_docs.html')

if __name__ == '__main__':
    app.run(debug=True)