from db.init_db import create_connection, execute_sql

class ConversationModel:
    @staticmethod
    def get_conversations_for_organization(org_id):
        conn = create_connection()
        query = """
        SELECT ph.id, ph.timestamp, ph.url, ph.prompt, ph.response
        FROM prompt_history ph
        JOIN users u ON ph.user_id = u.id
        WHERE u.organization_id = ?
          AND ph.prompt NOT LIKE '%Question:%Question:%QUESTION:%'
        ORDER BY ph.timestamp DESC
        """
        conversations = execute_sql(conn, query, (org_id,))
        conn.close()

        if conversations:
            return [
                {
                    "id": conv[0],
                    "timestamp": conv[1],
                    "url": conv[2],
                    "prompt": conv[3],
                    "response": conv[4]
                }
                for conv in conversations
            ]
        return []

    @staticmethod
    def get_conversations_for_user(user_id):
        conn = create_connection()
        query = """
        SELECT id, timestamp, url, prompt, response
        FROM prompt_history
        WHERE prompt LIKE '%Question:%'
          AND prompt NOT LIKE '%Question:%Question:%'
          AND prompt LIKE '%User: {"id": ' || ? || ',%'
        ORDER BY timestamp DESC
        """
        conversations = execute_sql(conn, query, (user_id,))
        conn.close()

        if conversations:
            return [
                {
                    "id": conv[0],
                    "timestamp": conv[1],
                    "url": conv[2],
                    "prompt": conv[3],
                    "response": conv[4]
                }
                for conv in conversations
            ]
        return []

    @staticmethod
    def getTotalPromptHistoryEntriesForOrganization(organization_id):
        conn = create_connection()
        query = """
        SELECT COUNT(*)
        FROM prompt_history ph
        JOIN users u ON ph.user_id = u.id
        WHERE u.organization_id = ?
        """
        count = execute_sql(conn, query, (organization_id,))[0][0]
        conn.close()

        return count



    @staticmethod
    def get_conversation(conversation_id):
        conn = create_connection()
        query = """
        SELECT id, timestamp, url, prompt, response
        FROM prompt_history
        WHERE id = ?
          AND prompt LIKE '%Question:%'
          AND prompt NOT LIKE '%Question:%Question:%'
        """
        conversation = execute_sql(conn, query, (conversation_id,))
        conn.close()

        if conversation:
            return {
                "id": conversation[0][0],
                "timestamp": conversation[0][1],
                "url": conversation[0][2],
                "prompt": conversation[0][3],
                "response": conversation[0][4]
            }
        return None

    @staticmethod
    def get_conversation_count_for_user(user_id):
        conn = create_connection()
        query = """
        SELECT COUNT(*)
        FROM prompt_history
        WHERE prompt LIKE '%Question:%'
          AND prompt NOT LIKE '%Question:%Question:%'
          AND prompt LIKE '%User: {"id": ' || ? || ',%'
        """
        count = execute_sql(conn, query, (user_id,))[0][0]
        conn.close()

        return count

    @staticmethod
    def get_recent_conversations(limit=10):
        conn = create_connection()
        query = """
        SELECT id, timestamp, url, prompt, response
        FROM prompt_history
        WHERE prompt LIKE '%Question:%'
          AND prompt NOT LIKE '%Question:%Question:%'
        ORDER BY timestamp DESC
        LIMIT ?
        """
        conversations = execute_sql(conn, query, (limit,))
        conn.close()

        if conversations:
            return [
                {
                    "id": conv[0],
                    "timestamp": conv[1],
                    "url": conv[2],
                    "prompt": conv[3],
                    "response": conv[4]
                }
                for conv in conversations
            ]
        return []