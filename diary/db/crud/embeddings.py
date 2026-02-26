# app/crud/embeddings.py

import os
from dotenv import load_dotenv
from typing import List
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# def search_similar_entries(user_id, query_text, n=5, start_date=None, end_date=None, tags=None):

#     query_embedding = generate_embedding(query_text)

#     sql = """
#         SELECT *,
#                embedding <-> %s AS distance
#         FROM entries
#         WHERE user_id = %s
#           AND embedding IS NOT NULL
#     """

#     params = [query_embedding, user_id]

#     if start_date:
#         sql += " AND entry_date >= %s"
#         params.append(start_date)

#     if end_date:
#         sql += " AND entry_date <= %s"
#         params.append(end_date)

#     if tags:
#         sql += " AND entry_tags && %s"
#         params.append(tags)

#     sql += " ORDER BY embedding <-> %s LIMIT %s"
#     params.extend([query_embedding, n])

#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute(sql, params)
#             return cur.fetchall()


# def update_embedding_for_entry(entry):
#     """
#     Updates embedding field of an entry object.
#     Does NOT commit to DB.
#     """

#     if not entry.llm_allowed:
#         entry.embedding = None
#         return

#     try:
#         entry.embedding = generate_embedding(entry.content)
#     except Exception as e:
#         print("Embedding generation failed:", e)
#         entry.embedding = None