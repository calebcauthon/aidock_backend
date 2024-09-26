import sqlite3
import psycopg2
from db.init_db import create_connection, execute_sql

class Datastore:
    def __init__(self, db_connection):
        self.conn = db_connection

    def save_prompt_and_response(self, url, prompt, response):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO prompt_history (url, prompt, response) VALUES (?, ?, ?)",
                (url, prompt, response)
            )
            self.conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error saving prompt and response: {str(e)}")
            self.conn.rollback()

    def get_prompt_history(self, offset=0, limit=1):
        try:
            cursor = self.conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM prompt_history")
            total_count = cursor.fetchone()[0]

            # Get the current entry
            cursor.execute("SELECT * FROM prompt_history ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
            entry = cursor.fetchone()

            cursor.close()

            return {
                'entry': entry,
                'total_count': total_count,
                'has_prev': offset > 0,
                'has_next': offset + limit < total_count,
                'prev_offset': max(0, offset - limit),
                'next_offset': offset + limit
            }
        except Exception as e:
            print(f"Error retrieving prompt history: {str(e)}")
            return None

    def close_connection(self):
        if self.conn:
            self.conn.close()

def save_prompt_history(url, system_prompt, question, answer, user_id):
    conn = create_connection()
    if conn is not None:
        try:
            execute_sql(conn, 
                "INSERT INTO prompt_history (url, prompt, response, user_id) VALUES (?, ?, ?, ?)",
                (url, f"SYSTEM PROMPT: {system_prompt} | USER QUESTION: {question}", answer, user_id)
            )
        finally:
            conn.close()
