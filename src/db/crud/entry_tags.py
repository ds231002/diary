from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def add_tag_to_entry(
    entry_id: UUID,
    tag_id: UUID,
    user_id: UUID,
) -> None:
    query = """
    INSERT INTO entry_tags (entry_id, tag_id, user_id)
    VALUES (%s, %s, %s)
    ON CONFLICT DO NOTHING;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id, tag_id, user_id))

# ==============================
# READ
# ==============================

def list_tags_for_entry(
    entry_id: UUID,
    user_id: UUID,
) -> list[dict]:
    query = """
    SELECT t.*
    FROM tags t
    JOIN entry_tags et
      ON et.tag_id = t.id
     AND et.user_id = t.user_id
    WHERE et.entry_id = %s
      AND et.user_id = %s
    ORDER BY t.position NULLS LAST, t.name;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id, user_id))
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

def sync_entry_tags(
    entry_id: UUID,
    user_id: UUID,
    tag_ids: list[UUID],
    *,
    conn=None,
) -> None:
    if conn is None:
        with get_connection() as conn:
            return sync_entry_tags(
                entry_id,
                user_id,
                tag_ids,
                conn=conn,
            )

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM entry_tags
            WHERE entry_id = %s
              AND user_id = %s;
            """,
            (entry_id, user_id),
        )

        for tag_id in tag_ids:
            cur.execute(
                """
                INSERT INTO entry_tags (entry_id, tag_id, user_id)
                VALUES (%s, %s, %s);
                """,
                (entry_id, tag_id, user_id),
            )

# ==============================
# DELETE
# ==============================

def remove_tag_from_entry(
    entry_id: UUID,
    tag_id: UUID,
    user_id: UUID,
) -> None:
    query = """
    DELETE FROM entry_tags
    WHERE entry_id = %s
      AND tag_id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id, tag_id, user_id))
