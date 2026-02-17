from uuid import UUID
from datetime import date
from typing import Optional
from db.database import get_connection

# ==============================
# CREATE
# ==============================

def create_user_profile(
    user_id: UUID,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    birth_date: date | None = None,
    summary: str | None = None,
) -> dict:
    query = """
    INSERT INTO user_profiles (
        user_id,
        first_name,
        last_name,
        birth_date,
        summary
    )
    VALUES (%s, %s, %s, %s, %s)
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (user_id, first_name, last_name, birth_date, summary),
            )
            return cur.fetchone()

# ==============================
# READ
# ==============================

def get_user_profile(user_id: UUID) -> dict | None:
    query = """
    SELECT *
    FROM user_profiles
    WHERE user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return cur.fetchone()

# ==============================
# UPDATE
# ==============================

_UNSET = object()

def update_user_profile(
    user_id: UUID,
    *,
    first_name: Optional[str] = _UNSET,
    last_name: Optional[str] = _UNSET,
    birth_date: Optional[date] = _UNSET,
    summary: Optional[str] = _UNSET,
) -> dict:

    fields = []
    values = []

    if first_name is not _UNSET:
        fields.append("first_name = %s")
        values.append(first_name)

    if last_name is not _UNSET:
        fields.append("last_name = %s")
        values.append(last_name)

    if birth_date is not _UNSET:
        fields.append("birth_date = %s")
        values.append(birth_date)

    if summary is not _UNSET:
        fields.append("summary = %s")
        values.append(summary)

    if not fields:
        raise ValueError("No fields to update")

    query = f"""
    UPDATE user_profiles
    SET {", ".join(fields)}
    WHERE user_id = %s
    RETURNING *;
    """

    values.append(user_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone()

# ==============================
# UPSERT
# ==============================

def upsert_user_profile(
    user_id: UUID,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    birth_date: date | None = None,
    summary: str | None = None,
) -> dict:
    query = """
    INSERT INTO user_profiles (
        user_id,
        first_name,
        last_name,
        birth_date,
        summary
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        birth_date = EXCLUDED.birth_date,
        summary = EXCLUDED.summary
    RETURNING *;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (user_id, first_name, last_name, birth_date, summary),
            )
            return cur.fetchone()

# ==============================
# DELETE
# ==============================

def delete_user_profile(user_id: UUID) -> None:
    query = """
    DELETE FROM user_profiles
    WHERE user_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
