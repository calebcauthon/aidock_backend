from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
import os
from flask_cors import CORS
from routes_context_docs_for_platform_admin import context_docs, create_connection
from routes_title_prompt_for_dock import prompt_routes
from routes_user_crud_for_platform_admin import user_routes
from routes_organization_crud_for_platform_admin import organization_routes
from db.init_db import create_table
import psycopg2
from routes_authentication_for_dock import auth
from db.prompt_history import Datastore as PromptHistoryDatastore
from routes_librarian import librarian_routes
from routes_chat_prompt_for_dock import chat_prompt_routes

app = Flask(__name__, static_folder='static')
app.template_folder = 'templates'
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

CORS(app)

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
app.register_blueprint(librarian_routes)
app.register_blueprint(chat_prompt_routes)

app.secret_key = os.environ.get("SECRET_KEY", "your_fallback_secret_key")

@app.route('/hello')
def hello_world():
    return "Hello, World!"

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