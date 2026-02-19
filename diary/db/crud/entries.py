from uuid import UUID
from datetime import date
from typing import Optional
from db.database import get_connection
from db.crud.entry_tags import sync_entry_tags

# ==============================
# CREATE
# ==============================

def create_entry(
    user_id: UUID,
    *,
    content: str,
    entry_date: date | None = None,
    mood: int | None = None,
    tag_ids: list[UUID] | None = None,
    llm_allowed: bool | None = None,
) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:

            fields = ["user_id", "content"]
            values = [user_id, content]
            placeholders = ["%s", "%s"]

            if entry_date is not None:
                fields.append("entry_date")
                values.append(entry_date)
                placeholders.append("%s")

            if mood is not None:
                fields.append("mood")
                values.append(mood)
                placeholders.append("%s")

            if llm_allowed is not None:
                fields.append("llm_allowed")
                values.append(llm_allowed)
                placeholders.append("%s")

            query = f"""
            INSERT INTO entries ({", ".join(fields)})
            VALUES ({", ".join(placeholders)})
            RETURNING *;
            """

            cur.execute(query, values)
            entry = cur.fetchone()

            if tag_ids:
                sync_entry_tags(
                    entry_id=entry["id"],
                    user_id=user_id,
                    tag_ids=tag_ids,
                    conn=conn,
                )

            return entry

# ==============================
# READ
# ==============================

def get_entry_by_id(entry_id: UUID, user_id: UUID) -> dict | None:
    query = """
    SELECT *
    FROM entries
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id, user_id))
            return cur.fetchone()

def list_entries_by_user(
    user_id: UUID,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    mood_min: int | None = None,
    mood_max: int | None = None,
    llm_allowed: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:

    conditions = ["user_id = %s"]
    values = [user_id]

    if from_date is not None:
        conditions.append("entry_date >= %s")
        values.append(from_date)

    if to_date is not None:
        conditions.append("entry_date <= %s")
        values.append(to_date)

    if mood_min is not None:
        conditions.append("mood >= %s")
        values.append(mood_min)

    if mood_max is not None:
        conditions.append("mood <= %s")
        values.append(mood_max)

    if llm_allowed is not None:
        conditions.append("llm_allowed = %s")
        values.append(llm_allowed)

    query = f"""
    SELECT *
    FROM entries
    WHERE {" AND ".join(conditions)}
    ORDER BY entry_date DESC, created_at DESC
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

_UNSET = object()

def update_entry(
    entry_id: UUID,
    user_id: UUID,
    *,
    content: Optional[str] = _UNSET,
    entry_date: Optional[date] = _UNSET,
    mood: Optional[int] = _UNSET,
    llm_allowed: Optional[bool] = _UNSET,
) -> dict:

    fields = []
    values = []

    if entry_date is not _UNSET:
        fields.append("entry_date = %s")
        values.append(entry_date)

    if content is not _UNSET:
        fields.append("content = %s")
        values.append(content)

    if mood is not _UNSET:
        if mood is None:
            fields.append("mood = NULL")
        else:
            fields.append("mood = %s")
            values.append(mood)

    if llm_allowed is not _UNSET:
        fields.append("llm_allowed = %s")
        values.append(llm_allowed)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE entries
    SET {", ".join(fields)}
    WHERE id = %s
      AND user_id = %s
    RETURNING *;
    """

    values.extend([entry_id, user_id])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()


# ==============================
# DELETE
# ==============================

def delete_entry(entry_id: UUID, user_id: UUID) -> None:
    query = """
    DELETE FROM entries
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (entry_id, user_id))
