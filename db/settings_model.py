from db.init_db import create_connection, execute_sql

class SettingsModel:
    @staticmethod
    def get_organization_settings(organization_id):
        conn = create_connection()
        settings = execute_sql(conn, "SELECT name, value FROM organization_settings WHERE organization_id = ?", (organization_id,))
        conn.close()
        return [{"name": setting[0], "value": setting[1]} for setting in settings]

    @staticmethod
    def update_organization_setting(organization_id, name, value):
        conn = create_connection()
        execute_sql(conn, "INSERT OR REPLACE INTO organization_settings (organization_id, name, value) VALUES (?, ?, ?)", (organization_id, name, value))
        conn.close()
        return True

    @staticmethod
    def get_default_settings():
        conn = create_connection()
        settings = execute_sql(conn, "SELECT name, default_value FROM default_settings")
        conn.close()
        return [{"name": setting[0], "default_value": setting[1]} for setting in settings]

    @staticmethod
    def add_default_setting(name, default_value):
        conn = create_connection()
        execute_sql(conn, "INSERT INTO default_settings (name, default_value) VALUES (?, ?)", (name, default_value))
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