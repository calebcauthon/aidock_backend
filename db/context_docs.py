import re
from typing import List, Dict
from db.init_db import execute_sql, create_connection
import base64

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

def get_relevant_images(organization_id: int, url: str) -> List[Dict[str, str]]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT file_name, binary_content
        FROM files 
        WHERE organization_id = ? AND file_name LIKE '%.png' OR file_name LIKE '%.jpg' OR file_name LIKE '%.jpeg'
    """, (organization_id,))
    rows = cur.fetchall()
    conn.close()
    
    relevant_images = [
        {
            "document_name": row[0],
            "image_base64": base64.b64encode(row[1]).decode('utf-8')
        }
        for row in rows
    ]
    return relevant_images if relevant_images else []
