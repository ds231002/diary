import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from ds_toolkit.files import ensure_parent

def get_sentence_transformer(
    model: str = "BAAI/bge-m3",
) -> SentenceTransformer:
    return SentenceTransformer(model)

def embed_texts(
    texts: list[str],
    embedder,
):
    return embedder.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

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

def search_similar_chunks(
    query: str,
    index,
    chunks: list[str],
    embedder,
    k: int=5
):
    embedding = embed_texts([query], embedder)

    scores, indices = index.search(
        embedding.astype(np.float32),
        k,
    )

    return [
        (chunks[i], float(scores[0][j]))
        for j, i in enumerate(indices[0])
        if i != -1
    ]