import os
import sqlite3
from sqlite3 import Error
import psycopg2
from psycopg2 import sql

def create_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        return psycopg2.connect(db_url)
    else:
        # Fallback to SQLite
        import sqlite3
        return sqlite3.connect('lavendel.db')


def execute_sql(conn, sql, params=None):
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")

        conn.rollback()
        raise e


def create_table(conn):


    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS context_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                document_name TEXT NOT NULL,
                document_text TEXT NOT NULL,
                organization_id INTEGER NOT NULL
            )
        """)
        
        # Create prompt_history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                user_id INTEGER NOT NULL
            )
        """)

        conn.commit()
        print(f"Prompt history and context docs table possibly created")
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                login_token TEXT,
                organization_id INTEGER
            )
        """)
        conn.commit()
        print(f"Users table possibly created")

        # Create organizations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()
        print(f"Organizations table possibly created")

        cur.close()
    except (sqlite3.Error, psycopg2.Error) as e:
        print(f"Database error: {e}")

def main():
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        print("Database initialized successfully.")
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()