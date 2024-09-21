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


def execute_sql(conn, sql):
    cur = conn.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()
        conn.commit()
        return [dict(zip([column[0] for column in cur.description], row)) for row in result]
    finally:
        cur.close()

def create_table(conn):


    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS context_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                document_name TEXT NOT NULL,
                document_text TEXT NOT NULL
            )
        """)
        
        # Create prompt_history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL
            )
        """)
        conn.commit()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                login_token TEXT
            )
        """)
        conn.commit()

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