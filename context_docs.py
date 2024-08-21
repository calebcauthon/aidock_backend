import re
from typing import List
from context_docs_routes import create_connection

def get_relevant_context_docs(url: str) -> List[str]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT url, document_text FROM context_docs")
    rows = cur.fetchall()
    conn.close()
    
    relevant_docs = [row[1] for row in rows if url in row[0]]
    return relevant_docs if relevant_docs else []