from db.init_db import create_connection

class FileModel:
    @staticmethod
    def update_file_name(file_id, new_file_name):
        conn = create_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE files
                SET file_name = ?
                WHERE id = ?
            """, (new_file_name, file_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating file name: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()


    @staticmethod
    def get_file_by_id(file_id):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, organization_id, user_upload_id, timestamp_of_upload, binary_content, text_content, file_name, file_size
            FROM files
            WHERE id = ?
        """, (file_id,))
        file = cur.fetchone()
        cur.close()
        conn.close()
        
        if file:
            return {
                'id': file[0],
                'organization_id': file[1],
                'user_upload_id': file[2],
                'timestamp_of_upload': file[3],
                'binary_content': file[4],
                'text_content': file[5],
                'file_name': file[6],
                'file_size': file[7]
            }
        return None

    @staticmethod
    def add_file(organization_id, user_upload_id, binary_content, text_content, file_name, file_size):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO files (organization_id, user_upload_id, binary_content, text_content, file_name, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (organization_id, user_upload_id, binary_content, text_content, file_name, file_size))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_files_for_organization(organization_id):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_upload_id, timestamp_of_upload, file_name, file_size
            FROM files
            WHERE organization_id = ?
            ORDER BY timestamp_of_upload DESC
        """, (organization_id,))
        files = cur.fetchall()
        files_dict = [
            {
                'id': file[0],
                'user_upload_id': file[1],
                'timestamp_of_upload': file[2],
                'file_name': file[3],
                'file_size': file[4]
            }
            for file in files
        ]
        cur.close()
        conn.close()
        return files_dict

    @staticmethod
    def get_all_files():
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, organization_id, user_upload_id, timestamp_of_upload, text_content, file_name, file_size
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
                'text_content': file[4],
                'file_name': file[5],
                'file_size': file[6]
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

    @staticmethod
    def get_file_content(file_id):
        conn = create_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT file_name, text_content, binary_content FROM files WHERE id = ?", (file_id,))
            result = cur.fetchone()
            if result:
                name, text_content, binary_content = result
                return {
                    'name': name,
                    'text_content': text_content,
                    'binary_content': binary_content
                }
            else:
                return None
        except Exception as e:
            print(f"Error retrieving file content: {e}")
            return None
        finally:
            cur.close()
            conn.close()