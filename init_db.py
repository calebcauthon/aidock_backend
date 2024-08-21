import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('context_docs.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS context_docs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      url TEXT NOT NULL,
                      document_name TEXT NOT NULL,
                      document_text TEXT NOT NULL)''')
    except Error as e:
        print(e)

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