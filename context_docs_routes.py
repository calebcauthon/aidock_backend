from flask import request, jsonify, Blueprint
import sqlite3
from sqlite3 import Error
from flask import send_from_directory

context_docs = Blueprint('context_docs', __name__, static_folder='lavendel_frontend')


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('context_docs.db')
        return conn
    except Error as e:
        print(e)
    return conn

@context_docs.route('/', methods=['GET'])
def get_context_docs():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM context_docs")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": row[0], "url": row[1], "document_name": row[2], "document_text": row[3]} for row in rows])

@context_docs.route('/', methods=['POST'])
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

@context_docs.route('/<int:doc_id>', methods=['PUT'])
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

@context_docs.route('/<int:doc_id>', methods=['DELETE'])
def delete_context_doc(doc_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM context_docs WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Context document deleted successfully"})


@context_docs.route('/edit_doc/<int:doc_id>')
def edit_doc_page(doc_id):
    return send_from_directory(context_docs.static_folder, 'edit_doc.html')

@context_docs.route('/docs')
def serve_docs():
    return send_from_directory(context_docs.static_folder, 'context_docs.html')

@context_docs.route('/<int:doc_id>', methods=['GET'])
def get_context_doc(doc_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM context_docs WHERE id=?", (doc_id,))
    doc = cur.fetchone()
    conn.close()
    
    if doc:
        doc_data = {
            "id": doc[0],
            "url": doc[1],
            "document_name": doc[2],
            "document_text": doc[3]
        }
        return jsonify(doc_data)
    else:
        return jsonify({"error": "Document not found"}), 404

