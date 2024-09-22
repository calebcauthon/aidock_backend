from db.init_db import create_connection, execute_sql

class OrganizationModel:
    @staticmethod
    def get_organization(org_id):
        conn = create_connection()
        org = execute_sql(conn, "SELECT id, name, description FROM organizations WHERE id = ?", (org_id,))
        conn.close()

        if org:
            return {
                "id": org[0][0],
                "name": org[0][1],
                "description": org[0][2]
            }
        return None

    @staticmethod
    def get_all_organizations():
        conn = create_connection()
        orgs = execute_sql(conn, "SELECT id, name, description FROM organizations")
        orgs = [{"id": org[0], "name": org[1], "description": org[2]} for org in orgs]
        conn.close()

        return orgs

    @staticmethod
    def create_organization(name, description):
        conn = create_connection()
        try:
            execute_sql(conn, "INSERT INTO organizations (name, description) VALUES (?, ?)", 
                        (name, description))
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def update_organization(org_id, name=None, description=None):
        conn = create_connection()
        update_fields = []
        params = []
        if name:
            update_fields.append("name = ?")
            params.append(name)
        if description:
            update_fields.append("description = ?")
            params.append(description)
        
        if update_fields:
            update_query = f"UPDATE organizations SET {', '.join(update_fields)} WHERE id = ?"
            params.append(org_id)
            execute_sql(conn, update_query, tuple(params))
        conn.close()
        return True

    @staticmethod
    def delete_organization(org_id):
        conn = create_connection()
        execute_sql(conn, "DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.close()
        return True