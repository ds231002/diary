from ds_toolkit.embeddings import embed_texts
from ds_toolkit.faiss import search_index


def search_nearest_chunks(
    query: str,
    index,
    chunks: list[str],
    embedder,
    k: int = 5,
) -> list[tuple[str, float]]:
    query_embedding = embed_texts(
        [query],
        embedder,
    )

    scores, indices = search_index(
        query_embedding,
        index,
        k=k,
    )

    return [
        (chunks[i], float(scores[0][j]))
        for j, i in enumerate(indices[0])
        if i != -1
    ]