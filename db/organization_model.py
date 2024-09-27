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
        query = "SELECT id, name FROM organizations"
        organizations = execute_sql(conn, query)
        orgs = [{"id": org[0], "name": org[1]} for org in organizations]
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

    @staticmethod
    def get_organization_websites(org_id):
        conn = create_connection()
        query = "SELECT id, url FROM organization_websites WHERE organization_id = ?"
        websites = execute_sql(conn, query, (org_id,))
        conn.close()
        return [{'id': row[0], 'url': row[1]} for row in websites]

    @staticmethod
    def add_organization_website(org_id, url):
        conn = create_connection()
        try:
            execute_sql(conn, "INSERT INTO organization_websites (organization_id, url) VALUES (?, ?)", 
                        (org_id, url))
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def remove_organization_website(org_id, website_id):
        conn = create_connection()
        execute_sql(conn, "DELETE FROM organization_websites WHERE id = ? AND organization_id = ?", 
                    (website_id, org_id))
        conn.close()
        return True

    @staticmethod
    def check_website(current_url):
        conn = create_connection()
        query = "SELECT organization_id FROM organization_websites WHERE ? LIKE '%' || url || '%'"
        result = execute_sql(conn, query, (current_url,))
        conn.close()
        return result[0][0] if result else None