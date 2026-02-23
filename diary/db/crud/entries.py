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

from uuid import UUID
from psycopg2.extras import RealDictCursor


def get_entry_by_id(entry_id: UUID, user_id: UUID) -> dict | None:
    query = """
        SELECT 
            e.id,
            e.user_id,
            e.entry_date,
            e.content,
            e.mood,
            e.llm_allowed,
            e.created_at,
            e.updated_at,
            t.id   AS tag_id,
            t.name AS tag_name,
            t.color,
            t.favourite,
            t.llm_default_allowed
        FROM entries e
        LEFT JOIN entry_tags et
            ON et.entry_id = e.id
           AND et.user_id = e.user_id
        LEFT JOIN tags t
            ON t.id = et.tag_id
           AND t.user_id = e.user_id
        WHERE e.id = %s
          AND e.user_id = %s
        ORDER BY t.position NULLS LAST;
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (entry_id, user_id))
            rows = cur.fetchall()

            if not rows:
                return None

            # Grunddaten aus erster Zeile
            first = rows[0]

            entry = {
                "id": first["id"],
                "user_id": first["user_id"],
                "entry_date": first["entry_date"],
                "content": first["content"],
                "mood": first["mood"],
                "llm_allowed": first["llm_allowed"],
                "created_at": first["created_at"],
                "updated_at": first["updated_at"],
                "tags": [],
            }

            # Tags sammeln (falls vorhanden)
            for row in rows:
                if row["tag_id"] is not None:
                    entry["tags"].append({
                        "id": row["tag_id"],
                        "name": row["tag_name"],
                        "color": row["color"],
                        "favourite": row["favourite"],
                        "llm_default_allowed": row["llm_default_allowed"],
                    })

            return entry


# def get_entry_by_id(entry_id: UUID, user_id: UUID) -> dict | None:
#     query = """
#     SELECT *
#     FROM entries
#     WHERE id = %s
#       AND user_id = %s;
#     """

#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute(query, (entry_id, user_id))
#             return cur.fetchone()
        
def list_entries_by_user(
    user_id: UUID,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    mood_min: int | None = None,
    mood_max: int | None = None,
    llm_allowed: bool | None = None,
    tag_ids: list[UUID] | None = None,
    include_untagged: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:

    conditions = ["e.user_id = %s"]
    values = [user_id]

    joins = ""
    distinct = ""

    # ----------------------------------------
    # Basis-Filter
    # ----------------------------------------

    if from_date is not None:
        conditions.append("e.entry_date >= %s")
        values.append(from_date)

    if to_date is not None:
        conditions.append("e.entry_date <= %s")
        values.append(to_date)

    if mood_min is not None:
        conditions.append("e.mood >= %s")
        values.append(mood_min)

    if mood_max is not None:
        conditions.append("e.mood <= %s")
        values.append(mood_max)

    if llm_allowed is not None:
        conditions.append("e.llm_allowed = %s")
        values.append(llm_allowed)

    # ----------------------------------------
    # Tag-Logik
    # ----------------------------------------

    if tag_ids is not None:
        joins = """
        LEFT JOIN entry_tags et
          ON e.id = et.entry_id
         AND e.user_id = et.user_id
        """
        distinct = "DISTINCT"

        if tag_ids and include_untagged:
            conditions.append(
                "(et.tag_id = ANY(%s::uuid[]) OR et.entry_id IS NULL)"
            )
            values.append(tag_ids)

        elif tag_ids:
            conditions.append("et.tag_id = ANY(%s::uuid[])")
            values.append(tag_ids)

        elif include_untagged:
            conditions.append("et.entry_id IS NULL")

        else:
            conditions.append("FALSE")

    # ----------------------------------------
    # Query
    # ----------------------------------------

    query = f"""
    SELECT
        e.*,
        COALESCE(
            json_agg(
                DISTINCT jsonb_build_object(
                    'id', t.id,
                    'name', t.name
                )
            ) FILTER (WHERE t.id IS NOT NULL),
            '[]'
        ) AS tags
    FROM entries e
    LEFT JOIN entry_tags et
    ON e.id = et.entry_id
    AND e.user_id = et.user_id
    LEFT JOIN tags t
    ON et.tag_id = t.id
    AND et.user_id = t.user_id
    WHERE {" AND ".join(conditions)}
    GROUP BY e.id
    ORDER BY e.entry_date DESC, e.created_at DESC
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
