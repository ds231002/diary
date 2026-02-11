from uuid import UUID
from datetime import date
from db.database import get_connection
from db.crud.entry_tags import sync_entry_tags

# ==============================
# CREATE
# ==============================

def create_entry(
    user_id: UUID,
    *,
    start_date: date,
    content: str,
    end_date: date | None = None,
    mood: int | None = None,
    tag_ids: list[UUID] | None = None,
) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO entries (user_id, start_date, end_date, content, mood)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (user_id, start_date, end_date, content, mood),
            )
            entry = cur.fetchone()

            if tag_ids:
                sync_entry_tags(entry["id"], tag_ids, conn=conn)

            return entry

# ==============================
# READ
# ==============================

def get_entry_by_id(entry_id: UUID) -> dict | None:
    query = "SELECT * FROM entries WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id,))
            return cur.fetchone()

def list_entries_by_user(
    user_id: UUID,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    mood_min: int | None = None,
    mood_max: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    conditions = ["user_id = %s"]
    values = [user_id]

    if from_date is not None:
        conditions.append("start_date >= %s")
        values.append(from_date)

    if to_date is not None:
        conditions.append("start_date <= %s")
        values.append(to_date)

    if mood_min is not None:
        conditions.append("mood >= %s")
        values.append(mood_min)

    if mood_max is not None:
        conditions.append("mood <= %s")
        values.append(mood_max)

    query = f"""
    SELECT *
    FROM entries
    WHERE {" AND ".join(conditions)}
    ORDER BY start_date DESC, created_at DESC
    LIMIT %s OFFSET %s;
    """

    values.extend([limit, offset])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchall()
        
# ==============================
# UPDATE
# ==============================

def update_entry(
    entry_id: UUID,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    content: str | None = None,
    mood: int | None = None,
) -> dict:
    fields = []
    values = []

    if start_date is not None:
        fields.append("start_date = %s")
        values.append(start_date)

    if end_date is not None:
        fields.append("end_date = %s")
        values.append(end_date)

    if content is not None:
        fields.append("content = %s")
        values.append(content)

    if mood is not None:
        fields.append("mood = %s")
        values.append(mood)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE entries
    SET {", ".join(fields)}
    WHERE id = %s
    RETURNING *;
    """

    values.append(entry_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_entry(entry_id: UUID) -> None:
    query = "DELETE FROM entries WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id,))
