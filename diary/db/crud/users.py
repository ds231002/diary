from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_user(user_name: str, is_demo: bool = False) -> UUID:
    query = """
    INSERT INTO users (user_name, is_demo)
    VALUES (%s, %s)
    RETURNING id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_name, is_demo))
            user_id = cur.fetchone()["id"]

    return user_id

# ==============================
# READ
# ==============================

def list_users(limit: int = 100, offset: int = 0) -> list[dict]:
    query = """
    SELECT *
    FROM users
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit, offset))
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

def update_user(
    user_id: UUID,
    *,
    user_name: str | None = None,
    is_demo: bool | None = None,
) -> dict:
    fields = []
    values = []

    if user_name is not None:
        fields.append("user_name = %s")
        values.append(user_name)

    if is_demo is not None:
        fields.append("is_demo = %s")
        values.append(is_demo)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE users
    SET {", ".join(fields)}
    WHERE id = %s
    RETURNING *;
    """

    values.append(user_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_user(user_id: UUID) -> None:
    query = "DELETE FROM users WHERE id = %s;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))