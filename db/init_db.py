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
        return sqlite3.connect(os.environ.get('SQLITE_FILEPATH', 'lavendel.db'))


def execute_sql(conn, sql, params=None):
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
    except Exception as e:
        print(f"An error occurred: {e}")

        conn.rollback()
        raise e


def create_table(conn):


    try:
        cur = conn.cursor()
        
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
        print(f"Prompt history table possibly created")
        
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
        cur.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')

        # Create files table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                user_upload_id INTEGER NOT NULL,
                binary_content BLOB,
                text_content TEXT,
                file_name TEXT,
                file_size INTEGER,
                timestamp_of_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations (id),
                FOREIGN KEY (user_upload_id) REFERENCES users (id)
            )
        """)
        conn.commit()
        print("Files table possibly created")

        # Create organization_websites table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS organization_websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations (id)
            )
        """)
        conn.commit()
        print("Organization websites table possibly created")

        # Create user_websites table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                website_id INTEGER NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (website_id) REFERENCES organization_websites (id),
                UNIQUE(user_id, website_id)
            )
        """)
        conn.commit()
        print("User websites table possibly created")

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