from flask import Flask, request, jsonify, send_from_directory, render_template, url_for, redirect, session
import os
from flask_cors import CORS
from db.init_db import create_table
import psycopg2
from db.user_model import UserModel
from routes import register_routes

app = Flask(__name__, static_folder='static')
app.template_folder = 'templates'
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'files')
# Define allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


# Database connection function
def create_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        return psycopg2.connect(db_url)
    else:
        # Fallback to SQLite
        import sqlite3
        return sqlite3.connect(os.environ.get('SQLITE_FILEPATH', 'lavendel.db'))

# Initialize database
conn = create_connection()
if conn is not None:
    create_table(conn)
    conn.close()
else:
    print("Error! Cannot create the database connection.")

register_routes(app)

app.secret_key = os.environ.get("SECRET_KEY", "your_fallback_secret_key")

@app.route('/me', methods=['GET'])
def get_session_user_info():
    user_info = {
        "user_id": session.get('user_id'),
        "role": session.get('role'),
        "organization_id": session.get('organization_id')
    }

    if session.get('user_id'):
        user = UserModel.get_user(session['user_id'])
        login_token = user['login_token']
        user_info['login_token'] = login_token
        user_info['username'] = user['username']

    return jsonify(user_info)

@app.route('/')
def home():
    return redirect(url_for('platform_admin_pages.prompt_history'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)