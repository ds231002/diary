from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def add_tag_to_chat(
    chat_id: UUID,
    tag_id: UUID,
    user_id: UUID,
) -> None:
    query = """
    INSERT INTO chat_tags (chat_id, tag_id, user_id)
    VALUES (%s, %s, %s)
    ON CONFLICT DO NOTHING;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, tag_id, user_id))

# ==============================
# READ
# ==============================

def list_tags_for_chat(
    chat_id: UUID,
    user_id: UUID,
) -> list[dict]:
    query = """
    SELECT t.*
    FROM tags t
    JOIN chat_tags ct
      ON ct.tag_id = t.id
     AND ct.user_id = t.user_id
    WHERE ct.chat_id = %s
      AND ct.user_id = %s
    ORDER BY t.position NULLS LAST, t.name;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, user_id))
            return cur.fetchall()

# ==============================
# UPDATE (sync)
# ==============================

def sync_chat_tags(
    chat_id: UUID,
    user_id: UUID,
    tag_ids: list[UUID],
    *,
    conn=None,
) -> None:
    if conn is None:
        with get_connection() as conn:
            return sync_chat_tags(
                chat_id,
                user_id,
                tag_ids,
                conn=conn,
            )

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM chat_tags
            WHERE chat_id = %s
              AND user_id = %s;
            """,
            (chat_id, user_id),
        )

        for tag_id in tag_ids:
            cur.execute(
                """
                INSERT INTO chat_tags (chat_id, tag_id, user_id)
                VALUES (%s, %s, %s);
                """,
                (chat_id, tag_id, user_id),
            )

# ==============================
# DELETE
# ==============================

def remove_tag_from_chat(
    chat_id: UUID,
    tag_id: UUID,
    user_id: UUID,
) -> None:
    query = """
    DELETE FROM chat_tags
    WHERE chat_id = %s
      AND tag_id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (chat_id, tag_id, user_id))
