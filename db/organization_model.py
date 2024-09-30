from db.init_db import create_connection, execute_sql

class OrganizationModel:
    @staticmethod
    def get_organization_by_name(name):
        conn = create_connection()
        org = execute_sql(conn, "SELECT id, name, description FROM organizations WHERE name = ?", (name,))
        conn.close()

        if org:
            return {
                "id": org[0][0],
                "name": org[0][1],
                "description": org[0][2]
            }
        return None

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
    def check_website(current_url, org_id, user_id):
        conn = create_connection()
        
        # Step 1: Check if it's an organization website
        org_query = "SELECT id FROM organization_websites WHERE ? LIKE '%' || url || '%' AND organization_id = ?"
        org_result = execute_sql(conn, org_query, (current_url, org_id))
        
        if org_result:
            # Step 2: Check for user override
            user_query = "SELECT is_active FROM user_websites WHERE ? LIKE '%' || website_url || '%' AND user_id = ?"
            user_result = execute_sql(conn, user_query, (current_url, user_id))
            
            if user_result:
                # User override exists, return based on is_active
                conn.close()
                return org_id if user_result[0][0] else None
            else:
                # No user override, return org_id
                conn.close()
                return org_id
        else:
            # Step 3: Check user_websites for non-org sites
            user_query = "SELECT is_active FROM user_websites WHERE ? LIKE '%' || website_url || '%' AND user_id = ?"
            user_result = execute_sql(conn, user_query, (current_url, user_id))
            
            conn.close()
            return org_id if user_result and user_result[0][0] else None

    @staticmethod
    def get_all_websites_for_organization(organization_id):
        conn = create_connection()
        query = """
            SELECT ow.id, ow.url, 'organization' as type
            FROM organization_websites ow
            WHERE ow.organization_id = ?
        """
        websites = execute_sql(conn, query, (organization_id,))
        conn.close()
        return [{'id': row[0], 'url': row[1], 'type': row[2]} for row in websites]


    @staticmethod
    def get_user_websites(user_id):
        conn = create_connection()
        websites = execute_sql(conn, 'SELECT id, website_url, is_active FROM user_websites WHERE user_id = ?', (user_id,))
        conn.close()
        return websites

    @staticmethod
    def toggle_user_website(user_id, website_url, is_active):
        conn = create_connection()
        execute_sql(conn, 'DELETE FROM user_websites WHERE user_id = ? AND website_url = ?', (user_id, website_url))
        execute_sql(conn, 'INSERT INTO user_websites (user_id, website_url, is_active) VALUES (?, ?, ?)', (user_id, website_url, is_active))
        conn.close()
        return True

    @staticmethod
    def add_user_website(user_id, website_url):
        conn = create_connection()
        # Check if the user_id/website combination already exists
        existing_website = execute_sql(conn, 'SELECT id FROM user_websites WHERE user_id = ? AND website_url = ?', (user_id, website_url))
        
        if not existing_website:
            execute_sql(conn, '''\
                INSERT OR IGNORE INTO user_websites (user_id, website_url)
                    VALUES (?, ?)
                ''', (user_id, website_url))
        conn.close()
        return True

    @staticmethod
    def remove_user_website(user_id, website_url):
        conn = create_connection()
        execute_sql(conn, 'DELETE FROM user_websites WHERE user_id = ? AND website_url = ?', (user_id, website_url))
        conn.close()
        return True