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
    description: str | None = None,
    color: str | None = None,
    position: int | None = None,
    favourite: bool = False,
) -> dict:
    query = """
    INSERT INTO tags (user_id, name, description, color, position, favourite)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (user_id, name, description, color, position, favourite),
            )
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
    include_favourites_first: bool = True,
) -> list[dict]:

    order_clause = """
        ORDER BY favourite DESC,
                 position NULLS LAST,
                 name
    """ if include_favourites_first else """
        ORDER BY position NULLS LAST,
                 name
    """

    query = f"""
    SELECT *
    FROM tags
    WHERE user_id = %s
    {order_clause};
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
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
    description: Optional[str] = _UNSET,
    color: Optional[str] = _UNSET,
    position: Optional[int] = _UNSET,
    favourite: Optional[bool] = _UNSET,
) -> dict:

    fields = []
    values = []

    if name is not _UNSET:
        fields.append("name = %s")
        values.append(name)

    if description is not _UNSET:
        fields.append("description = %s")
        values.append(description)

    if color is not _UNSET:
        fields.append("color = %s")
        values.append(color)

    if position is not _UNSET:
        fields.append("position = %s")
        values.append(position)

    if favourite is not _UNSET:
        fields.append("favourite = %s")
        values.append(favourite)

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
