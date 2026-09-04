from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_message(
    chat_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
) -> dict:
    query = """
    INSERT INTO messages (chat_id, user_id, role, content)
    VALUES (%s, %s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, user_id, role, content))
            return cur.fetchone()

# ==============================
# READ
# ==============================

def list_messages(
    chat_id: UUID,
    user_id: UUID,
) -> list[dict]:
    query = """
    SELECT *
    FROM messages
    WHERE chat_id = %s
      AND user_id = %s
    ORDER BY created_at ASC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, user_id))
            return cur.fetchall()

def get_message(
    message_id: UUID,
    user_id: UUID,
) -> dict | None:
    query = """
    SELECT *
    FROM messages
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (message_id, user_id))
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_message(
    message_id: UUID,
    user_id: UUID,
) -> None:
    query = """
    DELETE FROM messages
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (message_id, user_id))
