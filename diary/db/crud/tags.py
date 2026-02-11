from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_tag(
    user_id: UUID,
    name: str,
    *,
    color: str | None = None,
    position: int | None = None,
    favourite: bool = False,
) -> dict:
    query = """
    INSERT INTO tags (user_id, name, color, position, favourite)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (user_id, name, color, position, favourite),
            )
            return cur.fetchone()

# ==============================
# READ
# ==============================

def get_tag_by_id(tag_id: UUID) -> dict | None:
    query = "SELECT * FROM tags WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (tag_id,))
            return cur.fetchone()

def list_tags_by_user(
    user_id: UUID,
    *,
    include_favourites: bool | None = None,
) -> list[dict]:
    conditions = ["user_id = %s"]
    values = [user_id]

    if include_favourites is True:
        conditions.append("favourite = TRUE")
    elif include_favourites is False:
        conditions.append("favourite = FALSE")

    query = f"""
    SELECT *
    FROM tags
    WHERE {" AND ".join(conditions)}
    ORDER BY position NULLS LAST, name;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

def update_tag(
    tag_id: UUID,
    *,
    name: str | None = None,
    color: str | None = None,
    position: int | None = None,
    favourite: bool | None = None,
) -> dict:
    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)

    if color is not None:
        fields.append("color = %s")
        values.append(color)

    if position is not None:
        fields.append("position = %s")
        values.append(position)

    if favourite is not None:
        fields.append("favourite = %s")
        values.append(favourite)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE tags
    SET {", ".join(fields)}
    WHERE id = %s
    RETURNING *;
    """

    values.append(tag_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_tag(tag_id: UUID) -> None:
    query = "DELETE FROM tags WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (tag_id,))
