from uuid import UUID
from db.database import get_connection
from typing import Optional
from datetime import date

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

_UNSET = object()

def update_chat(
    chat_id: UUID,
    user_id: UUID,
    *,
    title: Optional[str] = _UNSET,
    folder_id: Optional[UUID] = _UNSET,
    start_date: Optional[date] = _UNSET,
    end_date: Optional[date] = _UNSET,
    summary: Optional[str] = _UNSET,
) -> dict:

    fields = []
    values = []

    if title is not _UNSET:
        fields.append("title = %s")
        values.append(title)

    if folder_id is not _UNSET:
        fields.append("folder_id = %s")
        values.append(folder_id)

    if start_date is not _UNSET:
        fields.append("start_date = %s")
        values.append(start_date)

    if end_date is not _UNSET:
        fields.append("end_date = %s")
        values.append(end_date)

    if summary is not _UNSET:
        fields.append("summary = %s")
        values.append(summary)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE chats
    SET {", ".join(fields)}
    WHERE id = %s
      AND user_id = %s
    RETURNING *;
    """

    values.extend([chat_id, user_id])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
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
