from flask import request, jsonify, Blueprint, render_template
import sqlite3
from sqlite3 import Error
from flask import send_from_directory
from flask_cors import CORS
from db.init_db import create_connection
from routes_auth_helpers import platform_admin_required

context_docs = Blueprint('context_docs', __name__, static_folder='lavendel_frontend')
CORS(context_docs)

@context_docs.route('/', methods=['GET'])
@platform_admin_required
def get_context_docs():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, url, document_name, document_text, organization_id FROM context_docs")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": row[0], "url": row[1], "document_name": row[2], "document_text": row[3], "organization_id": row[4]} for row in rows])

@context_docs.route('/', methods=['POST'])
@platform_admin_required
def add_context_doc():
    data = request.get_json()
    url = data.get('url')
    document_name = data.get('document_name')
    document_text = data.get('document_text')
    organization_id = data.get('organization_id')
    
    missing_fields = []
    if not url:
        missing_fields.append("url")
    if not document_name:
        missing_fields.append("document_name")
    if not document_text:
        missing_fields.append("document_text")
    
    if not organization_id:
        missing_fields.append("organization_id")
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO context_docs (url, document_name, document_text, organization_id) VALUES (?, ?, ?, ?)",
                (url, document_name, document_text, organization_id))
    conn.commit()

    new_id = cur.lastrowid
    conn.close()
    
    return jsonify({"id": new_id, "message": "Context document added successfully"}), 201

@context_docs.route('/<int:doc_id>', methods=['PUT'])
@platform_admin_required
def update_context_doc(doc_id):
    data = request.get_json()
    url = data.get('url')
    document_name = data.get('document_name')
    document_text = data.get('document_text')
    organization_id = data.get('organization_id')
    
    if not all([url, document_name, document_text, organization_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("UPDATE context_docs SET url=?, document_name=?, document_text=?, organization_id=? WHERE id=?",
                (url, document_name, document_text, organization_id, doc_id))
    conn.commit()

    conn.close()
    
    return jsonify({"message": "Context document updated successfully"})

@context_docs.route('/<int:doc_id>', methods=['DELETE'])
@platform_admin_required
def delete_context_doc(doc_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM context_docs WHERE id=%s", (doc_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Context document deleted successfully"})

@context_docs.route('/edit_doc/<int:doc_id>')
@platform_admin_required
def edit_doc_page(doc_id):
    return render_template('superuser_ui/edit_doc.html', doc_id=doc_id)

@context_docs.route('/docs')
@platform_admin_required
def serve_docs():
    return render_template('superuser_ui/context_docs.html')

@context_docs.route('/<int:doc_id>', methods=['GET'])
@platform_admin_required
def get_context_doc(doc_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, url, document_name, document_text, organization_id FROM context_docs WHERE id=?", (doc_id,))
    doc = cur.fetchone()
    conn.close()

    
    if doc:
        doc_data = {
            "id": doc[0],
            "url": doc[1],
            "document_name": doc[2],
            "document_text": doc[3],
            "organization_id": doc[4]
        }
        return jsonify(doc_data)

    else:
        return jsonify({"error": "Document not found"}), 404

@context_docs.route('/<int:doc_id>', methods=['DELETE'])
@platform_admin_required
def delete_context_document(doc_id):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('DELETE FROM context_docs WHERE id = %s', (doc_id,))
            conn.commit()
            if c.rowcount > 0:
                return jsonify({"success": True, "message": "Document deleted successfully"})
            else:
                return jsonify({"success": False, "error": "Document not found"}), 404
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"success": False, "error": "Unable to connect to the database"}), 500
