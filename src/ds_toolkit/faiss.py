import faiss
import numpy as np
from pathlib import Path

from ds_toolkit.files import ensure_parent
from ds_toolkit.embeddings import embed_texts


def build_faiss_index(
    chunks: list[str],
    embedder,
):
    embeddings = embed_texts(chunks, embedder)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))

    return index

def save_index(
    index,
    path: str | Path = "faiss.index"
) -> Path:
    path = ensure_parent(path)
    faiss.write_index(index, path)
    return path

def load_index(path: str | Path):
    return faiss.read_index(str(path))

def search_index(
    query_embedding: np.ndarray,
    index,
    k: int = 5,
):
    scores, indices = index.search(
        query_embedding.astype(np.float32),
        k,
    )

    return scores, indices