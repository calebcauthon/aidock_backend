from db.init_db import create_connection, execute_sql
from werkzeug.security import generate_password_hash

class UserModel:
    @staticmethod
    def get_user_by_login_token(login_token):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, email, role, organization_id FROM users WHERE login_token = ?", (login_token,))
        conn.close()

        if user:
            return {
                "id": user[0][0],
                "username": user[0][1],
                "email": user[0][2],
                "role": user[0][3],
                "organization_id": user[0][4]
            }
        return None


    @staticmethod
    def get_all_users():
        conn = create_connection()
        users = execute_sql(conn, "SELECT id, username, email, role, organization_id FROM users")
        users = [{"id": user[0], "username": user[1], "email": user[2], "role": user[3], "organization_id": user[4]} for user in users]
        conn.close()

        return users

    @staticmethod
    def get_user(user_id):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, email, role, organization_id FROM users WHERE id = ?", (user_id,))
        user = {"id": user[0][0], "username": user[0][1], "email": user[0][2], "role": user[0][3], "organization_id": user[0][4]} if user else None
        conn.close()

        return user if user else None

    @staticmethod
    def create_user(username, email, password, role, organization_id=-1):
        conn = create_connection()
        hashed_password = generate_password_hash(password)

        try:
            execute_sql(conn, "INSERT INTO users (username, email, password_hash, role, organization_id) VALUES (?, ?, ?, ?, ?)", 
                        (username, email, hashed_password, role, organization_id))
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def update_user(user_id, username=None, email=None, role=None, organization_id=None):
        conn = create_connection()
        update_fields = []
        params = []
        if username:
            update_fields.append("username = ?")
            params.append(username)
        if email:
            update_fields.append("email = ?")
            params.append(email)
        if role:
            update_fields.append("role = ?")
            params.append(role)
        if organization_id:
            update_fields.append("organization_id = ?")
            params.append(organization_id)
        
        if update_fields:

            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            params.append(user_id)
            execute_sql(conn, update_query, tuple(params))
        conn.close()
        return True

    @staticmethod
    def delete_user(user_id):
        conn = create_connection()
        execute_sql(conn, "DELETE FROM users WHERE id = ?", (user_id,))
        conn.close()
        return True

    @staticmethod
    def get_user_by_username(username):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
        user = {"id": user[0][0], "username": user[0][1], "email": user[0][2], "password_hash": user[0][3]} if user else None
        conn.close()

        return user if user else None

    @staticmethod
    def update_login_token(user_id, login_token):
        conn = create_connection()
        execute_sql(conn, "UPDATE users SET login_token = ? WHERE id = ?", (login_token, user_id))
        conn.close()
        return True

    @staticmethod
    def update_password(user_id, new_password):
        conn = create_connection()
        if conn is not None:
            try:
                password_hash = generate_password_hash(new_password)
                execute_sql(conn, "UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
                conn.close()
            except Exception as e:
                conn.close()
                raise e
        else:
            raise Exception("Unable to connect to the database")