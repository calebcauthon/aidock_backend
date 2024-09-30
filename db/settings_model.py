from db.init_db import create_connection, execute_sql

class SettingsModel:
    @staticmethod
    def get_organization_settings(organization_id):
        conn = create_connection()
        settings = execute_sql(conn, """
            SELECT os.name, os.value, ds.description 
            FROM organization_settings os
            LEFT JOIN default_settings ds ON os.name = ds.name
            WHERE os.organization_id = ?
        """, (organization_id,))
        conn.close()
        return [{"name": setting[0], "value": setting[1], "description": setting[2]} for setting in settings]

    @staticmethod
    def update_organization_setting(organization_id, name, value):
        conn = create_connection()
        execute_sql(conn, "INSERT OR REPLACE INTO organization_settings (organization_id, name, value) VALUES (?, ?, ?)", (organization_id, name, value))
        conn.close()
        return True

    @staticmethod
    def get_default_settings():
        conn = create_connection()
        settings = execute_sql(conn, "SELECT name, default_value, description FROM default_settings")
        conn.close()
        return [{"name": setting[0], "default_value": setting[1], "description": setting[2]} for setting in settings]

    @staticmethod
    def add_default_setting(name, default_value, description):
        conn = create_connection()
        execute_sql(conn, "INSERT INTO default_settings (name, default_value, description) VALUES (?, ?, ?)", (name, default_value, description))
        conn.close()
        return True

    @staticmethod
    def update_default_setting(name, default_value, description):
        conn = create_connection()
        execute_sql(conn, "UPDATE default_settings SET default_value = ?, description = ? WHERE name = ?", (default_value, description, name))
        conn.close()
        return True

    @staticmethod
    def create_organization_settings(organization_id):
        default_settings = SettingsModel.get_default_settings()
        conn = create_connection()
        for setting in default_settings:
            execute_sql(conn, "INSERT INTO organization_settings (organization_id, name, value) VALUES (?, ?, ?)", 
                        (organization_id, setting['name'], setting['default_value']))
        conn.close()
        return True

    @staticmethod
    def update_organization_setting(org_id, setting_name, setting_value):
        conn = create_connection()
        if conn is not None:
            try:
                # First, delete the existing setting
                execute_sql(conn, """
                    DELETE FROM organization_settings
                    WHERE organization_id = ? AND name = ?
                """, (org_id, setting_name))
                
                # Then, insert the new setting
                execute_sql(conn, """
                    INSERT INTO organization_settings (organization_id, name, value)
                    VALUES (?, ?, ?)
                """, (org_id, setting_name, setting_value))
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            raise Exception("Unable to connect to the database")