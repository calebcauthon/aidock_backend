from init_db import create_connection, execute_sql
from werkzeug.security import generate_password_hash

class UserModel:
    @staticmethod
    def get_all_users():
        conn = create_connection()
        users = execute_sql(conn, "SELECT id, username, email FROM users")
        conn.close()
        return users

    @staticmethod
    def get_user(user_id):
        conn = create_connection()
        user = execute_sql(conn, f"SELECT id, username, email FROM users WHERE id = {user_id}")
        conn.close()
        return user[0] if user else None

    @staticmethod
    def create_user(username, email, password):
        conn = create_connection()
        hashed_password = generate_password_hash(password)
        try:
            execute_sql(conn, f"INSERT INTO users (username, email, password_hash) VALUES ('{username}', '{email}', '{hashed_password}')")
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def update_user(user_id, username=None, email=None):
        conn = create_connection()
        update_fields = []
        if username:
            update_fields.append(f"username = '{username}'")
        if email:
            update_fields.append(f"email = '{email}'")
        
        if update_fields:
            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = {user_id}"
            execute_sql(conn, update_query)
        conn.close()
        return True

    @staticmethod
    def delete_user(user_id):
        conn = create_connection()
        execute_sql(conn, f"DELETE FROM users WHERE id = {user_id}")
        conn.close()
        return True

    @staticmethod
    def get_user_by_username(username):
        conn = create_connection()
        user = execute_sql(conn, f"SELECT * FROM users WHERE username = '{username}'")
        conn.close()
        return user[0] if user else None

    @staticmethod
    def update_login_token(user_id, login_token):
        conn = create_connection()
        execute_sql(conn, f"UPDATE users SET login_token = '{login_token}' WHERE id = {user_id}")
        conn.close()
        return True