from uuid import UUID
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_folder(
    user_id: UUID,
    name: str,
    position: int | None = None,
) -> dict:
    query = """
    INSERT INTO folders (user_id, name, position)
    VALUES (%s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id, name, position))
            return cur.fetchone()

# ==============================
# READ
# ==============================

def get_folder(folder_id: UUID, user_id: UUID) -> dict | None:
    query = """
    SELECT *
    FROM folders
    WHERE id = %s AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (folder_id, user_id))
            return cur.fetchone()


def list_folders(user_id: UUID) -> list[dict]:
    query = """
    SELECT *
    FROM folders
    WHERE user_id = %s
    ORDER BY position NULLS LAST, created_at;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

# ==============================
# UPDATE
# ==============================

def update_folder(
    folder_id: UUID,
    user_id: UUID,
    *,
    name: str,
    position: int | None,
) -> dict | None:
    query = """
    UPDATE folders
    SET name = %s,
        position = %s
    WHERE id = %s AND user_id = %s
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name, position, folder_id, user_id))
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_folder(folder_id: UUID, user_id: UUID) -> None:
    query = """
    DELETE FROM folders
    WHERE id = %s AND user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (folder_id, user_id))
