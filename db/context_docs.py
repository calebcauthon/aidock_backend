import re
from typing import List
from routes_context_docs_for_platform_admin import create_connection
from db.init_db import execute_sql

def get_relevant_context_docs(organization_id: int, url: str) -> List[str]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, url, document_name, document_text FROM context_docs WHERE organization_id = ?", (organization_id,))
    rows = cur.fetchall()
    conn.close()
    
    relevant_docs = [
        {
            "id": row[0],
            "url": row[1],
            "document_name": row[2],
            "document_text": row[3]
        }
        for row in rows if row[1] in url or row[1] == '*'
    ]
    return relevant_docs if relevant_docs else []


class ContextDocModel:
    @staticmethod
    def add_context_doc(organization_id: int, url: str, document_name: str, document_text: str):
        conn = create_connection()
        query = """
        INSERT INTO context_docs (organization_id, url, document_name, document_text)
        VALUES (?, ?, ?, ?)
        """
        execute_sql(conn, query, (organization_id, url, document_name, document_text))
        conn.close()
