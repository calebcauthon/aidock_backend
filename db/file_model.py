from db.init_db import create_connection

class FileModel:
    @staticmethod
    def add_file(organization_id, user_upload_id, binary_content, text_content):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO files (organization_id, user_upload_id, binary_content, text_content)
            VALUES (?, ?, ?, ?)
        """, (organization_id, user_upload_id, binary_content, text_content))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_files_for_organization(organization_id):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_upload_id, timestamp_of_upload
            FROM files
            WHERE organization_id = ?
            ORDER BY timestamp_of_upload DESC
        """, (organization_id,))
        files = cur.fetchall()
        cur.close()
        conn.close()
        return files

    @staticmethod
    def get_all_files():
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, organization_id, user_upload_id, timestamp_of_upload, text_content
            FROM files
            ORDER BY timestamp_of_upload DESC
        """)
        files = cur.fetchall()
        files_dict = [
            {
                'id': file[0],
                'organization_id': file[1],
                'user_upload_id': file[2],
                'timestamp_of_upload': file[3],
                'text_content': file[4]
            }
            for file in files
        ]
        cur.close()
        conn.close()
        return files_dict

    @staticmethod
    def delete_file(file_id):
        conn = create_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()