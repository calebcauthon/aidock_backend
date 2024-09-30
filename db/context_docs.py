import re
from typing import List
from db.init_db import execute_sql, create_connection

def get_relevant_context_docs(organization_id: int, url: str) -> List[str]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT text_content, file_name
        FROM files 
        WHERE organization_id = ?
    """, (organization_id,))
    rows = cur.fetchall()
    conn.close()
    
    relevant_docs = [
        {
            "id": "",
            "url": "",
            "document_name": row[1],
            "document_text": row[0]
        }
        for row in rows
    ]
    return relevant_docs if relevant_docs else []
