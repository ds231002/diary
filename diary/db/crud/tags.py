from uuid import UUID
from typing import Optional
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_tag(
    user_id: UUID,
    *,
    name: str,
    llm_default_allowed: bool | None = None,
) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:

            fields = ["user_id", "name"]
            values = [user_id, name]
            placeholders = ["%s", "%s"]

            if llm_default_allowed is not None:
                fields.append("llm_default_allowed")
                values.append(llm_default_allowed)
                placeholders.append("%s")

            query = f"""
            INSERT INTO tags ({", ".join(fields)})
            VALUES ({", ".join(placeholders)})
            RETURNING *;
            """

            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# READ
# ==============================

def get_tag_by_id(tag_id: UUID, user_id: UUID) -> dict | None:
    query = """
    SELECT *
    FROM tags
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (tag_id, user_id))
            return cur.fetchone()


def list_tags_by_user(
    user_id: UUID,
    *,
    llm_default_allowed: bool | None = None,
) -> list[dict]:

    conditions = ["user_id = %s"]
    values = [user_id]

    if llm_default_allowed is not None:
        conditions.append("llm_default_allowed = %s")
        values.append(llm_default_allowed)

    query = f"""
    SELECT *
    FROM tags
    WHERE {" AND ".join(conditions)}
    ORDER BY name ASC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

_UNSET = object()

def update_tag(
    tag_id: UUID,
    user_id: UUID,
    *,
    name: Optional[str] = _UNSET,
    llm_default_allowed: Optional[bool] = _UNSET,
) -> dict:

    fields = []
    values = []

    if name is not _UNSET:
        fields.append("name = %s")
        values.append(name)

    if llm_default_allowed is not _UNSET:
        fields.append("llm_default_allowed = %s")
        values.append(llm_default_allowed)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE tags
    SET {", ".join(fields)}
    WHERE id = %s
      AND user_id = %s
    RETURNING *;
    """

    values.extend([tag_id, user_id])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_tag(tag_id: UUID, user_id: UUID) -> None:
    query = """
    DELETE FROM tags
    WHERE id = %s
      AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (tag_id, user_id))
