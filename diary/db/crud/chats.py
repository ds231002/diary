from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_chat(
    user_id: UUID,
    folder_id: UUID | None = None,
    title: str | None = None,
    start_date=None,
    end_date=None,
    summary: str | None = None,
) -> dict:
    query = """
    INSERT INTO chats (
        user_id,
        folder_id,
        title,
        start_date,
        end_date,
        summary
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (user_id, folder_id, title, start_date, end_date, summary),
            )
            return cur.fetchone()

# ==============================
# READ
# ==============================

def get_chat(chat_id: UUID, user_id: UUID) -> dict | None:
    query = """
    SELECT *
    FROM chats
    WHERE id = %s AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, user_id))
            return cur.fetchone()

def list_chats(user_id: UUID) -> list[dict]:
    query = """
    SELECT *
    FROM chats
    WHERE user_id = %s
    ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

def list_chats_in_folder(user_id: UUID, folder_id: UUID) -> list[dict]:
    query = """
    SELECT *
    FROM chats
    WHERE user_id = %s AND folder_id = %s
    ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id, folder_id))
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

def update_chat(
    chat_id: UUID,
    user_id: UUID,
    *,
    title: str | None,
    folder_id: UUID | None,
    start_date=None,
    end_date=None,
    summary: str | None,
) -> dict | None:
    query = """
    UPDATE chats
    SET title = %s,
        folder_id = %s,
        start_date = %s,
        end_date = %s,
        summary = %s
    WHERE id = %s AND user_id = %s
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    title,
                    folder_id,
                    start_date,
                    end_date,
                    summary,
                    chat_id,
                    user_id,
                ),
            )
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_chat(chat_id: UUID, user_id: UUID) -> None:
    query = """
    DELETE FROM chats
    WHERE id = %s AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, user_id))
