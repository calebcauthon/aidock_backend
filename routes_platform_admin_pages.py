from flask import Blueprint, render_template, jsonify, request
from db.prompt_history import Datastore as PromptHistoryDatastore
from db.init_db import create_connection
import psycopg2

platform_admin_pages = Blueprint('platform_admin_pages', __name__)

@platform_admin_pages.route('/history')
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

@platform_admin_pages.route('/context_docs/<int:doc_id>', methods=['GET'])
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
                    'scope': doc[4],
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

@platform_admin_pages.route('/api/organization/<int:org_id>/websites', methods=['GET'])
def get_organization_websites(org_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url FROM organization_websites WHERE organization_id = ?", (org_id,))
            websites = [{'id': row[0], 'url': row[1]} for row in cursor.fetchall()]
            cursor.close()
            return jsonify(websites)
        except (psycopg2.Error) as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

@platform_admin_pages.route('/api/organization/<int:org_id>/websites', methods=['POST'])
def add_organization_website(org_id):
    conn = create_connection()
    if conn is not None:
        try:
            data = request.json
            url = data.get('url')
            if not url:
                return jsonify({"success": False, "message": "URL is required"}), 400
            
            cursor = conn.cursor()
            cursor.execute("INSERT INTO organization_websites (organization_id, url) VALUES (?, ?)", (org_id, url))
            conn.commit()
            cursor.close()
            return jsonify({"success": True, "message": "Website added successfully"})
        except (psycopg2.Error) as e:
            conn.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

@platform_admin_pages.route('/api/organization/<int:org_id>/websites/<int:website_id>', methods=['DELETE'])
def remove_organization_website(org_id, website_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM organization_websites WHERE id = ? AND organization_id = ?", (website_id, org_id))
            conn.commit()
            cursor.close()
            return jsonify({"success": True, "message": "Website removed successfully"})
        except (psycopg2.Error) as e:
            conn.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500

@platform_admin_pages.route('/api/websites', methods=['GET'])
def check_website():
    current_url = request.args.get('url')
    if not current_url:
        return jsonify({"error": "URL parameter is required"}), 400

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT organization_id FROM organization_websites WHERE ? LIKE '%' || url || '%'", (current_url,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return jsonify({"is_organization_website": True, "organization_id": result[0]})
            else:
                return jsonify({"is_organization_website": False})
        except (psycopg2.Error) as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({"error": "Unable to connect to the database"}), 500
