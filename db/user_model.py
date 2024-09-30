from db.init_db import create_connection, execute_sql
from werkzeug.security import generate_password_hash

class UserModel:
    @staticmethod
    def clear_login_token(user_id):
        conn = create_connection()
        execute_sql(conn, "UPDATE users SET login_token = NULL WHERE id = ?", (user_id,))
        conn.close()
        return True

    @staticmethod
    def get_users_for_organization(organization_id):
        conn = create_connection()
        users = execute_sql(conn, "SELECT id, username, role FROM users WHERE organization_id = ?", (organization_id,))
        users = [{"id": user[0], "username": user[1], "role": user[2]} for user in users]
        conn.close()
        return users

    def get_user_by_login_token(login_token):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, role, organization_id FROM users WHERE login_token = ?", (login_token,))
        conn.close()

        if user:
            return {
                "id": user[0][0],
                "username": user[0][1],
                "role": user[0][2],
                "organization_id": user[0][3]
            }
        return None

    @staticmethod
    def get_all_users():
        conn = create_connection()
        users = execute_sql(conn, "SELECT id, username, role, organization_id FROM users")
        users = [{"id": user[0], "username": user[1], "role": user[2], "organization_id": user[3]} for user in users]
        conn.close()
        return users

    @staticmethod
    def get_user(user_id):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, role, organization_id, login_token FROM users WHERE id = ?", (user_id,))
        print(f"sql result user: {user}")
        user = {"id": user[0][0], "username": user[0][1], "role": user[0][2], "organization_id": user[0][3], "login_token": user[0][4]} if user else None


        if user['organization_id'] is not None:
            org_result = execute_sql(conn, "SELECT name FROM organizations WHERE id = ?", (user['organization_id'],))
            user['organization_name'] = org_result[0][0] if org_result else None
        else:
            user['organization_name'] = 'platform admin'
        conn.close()

        return user if user else None

    @staticmethod
    def create_user(username, password, role, organization_id=-1):
        conn = create_connection()
        hashed_password = generate_password_hash(password)

        try:
            execute_sql(conn, "INSERT INTO users (username, password_hash, role, organization_id) VALUES (?, ?, ?, ?)", 
                        (username, hashed_password, role, organization_id))
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def update_user(user_id, username, role, password=None):
        conn = create_connection()
        update_fields = ["username = ?", "role = ?"]
        params = [username, role, user_id]

        if password:
            update_fields.append("password_hash = ?")
            hashed_password = generate_password_hash(password)
            params.insert(-1, hashed_password)

        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"

        try:
            execute_sql(conn, update_query, tuple(params))
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def delete_user(user_id):
        conn = create_connection()
        execute_sql(conn, "DELETE FROM users WHERE id = ?", (user_id,))
        conn.close()
        return True

    @staticmethod
    def get_user_by_username(username):
        conn = create_connection()
        user = execute_sql(conn, "SELECT id, username, password_hash, organization_id, role FROM users WHERE username = ?", (username,))
        user = {"id": user[0][0], "username": user[0][1], "password_hash": user[0][2], "organization_id": user[0][3], "role": user[0][4]} if user else None
        conn.close()
        return user if user else None

    @staticmethod
    def update_login_token(user_id, login_token):
        conn = create_connection()
        execute_sql(conn, "UPDATE users SET login_token = ? WHERE id = ?", (login_token, user_id))
        conn.close()
        return True

    @staticmethod
    def update_username(user_id, new_username):
        conn = create_connection()
        execute_sql(conn, "UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
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