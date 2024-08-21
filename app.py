from flask import Flask, request, jsonify, send_from_directory
import os
import anthropic
from flask_cors import CORS
from prompt import get_system_prompt
import sqlite3
from sqlite3 import Error

app = Flask(__name__, static_folder='lavendel_frontend')
CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Database setup
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('context_docs.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS context_docs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      url TEXT NOT NULL,
                      document_name TEXT NOT NULL,
                      document_text TEXT NOT NULL)''')
    except Error as e:
        print(e)

# Initialize database
conn = create_connection()
if conn is not None:
    create_table(conn)
    conn.close()
else:
    print("Error! Cannot create the database connection.")

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

@app.route('/context_docs', methods=['GET'])
def get_context_docs():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM context_docs")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": row[0], "url": row[1], "document_name": row[2], "document_text": row[3]} for row in rows])

@app.route('/context_docs', methods=['POST'])
def add_context_doc():
    data = request.get_json()
    url = data.get('url')
    document_name = data.get('document_name')
    document_text = data.get('document_text')
    
    if not all([url, document_name, document_text]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO context_docs (url, document_name, document_text) VALUES (?, ?, ?)",
                (url, document_name, document_text))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    
    return jsonify({"id": new_id, "message": "Context document added successfully"}), 201

@app.route('/context_docs/<int:doc_id>', methods=['PUT'])
def update_context_doc(doc_id):
    data = request.get_json()
    url = data.get('url')
    document_name = data.get('document_name')
    document_text = data.get('document_text')
    
    if not all([url, document_name, document_text]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("UPDATE context_docs SET url=?, document_name=?, document_text=? WHERE id=?",
                (url, document_name, document_text, doc_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Context document updated successfully"})

@app.route('/context_docs/<int:doc_id>', methods=['DELETE'])
def delete_context_doc(doc_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM context_docs WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Context document deleted successfully"})

@app.route('/edit_doc/<int:doc_id>')
def edit_doc_page(doc_id):
    return send_from_directory(app.static_folder, 'edit_doc.html')

@app.route('/docs')
def serve_docs():
    return send_from_directory(app.static_folder, 'context_docs.html')

if __name__ == '__main__':
    app.run(debug=True)