import numpy as np
from sentence_transformers import SentenceTransformer


def get_sentence_transformer(
    model: str = "BAAI/bge-m3",
) -> SentenceTransformer:
    return SentenceTransformer(model)

def embed_texts(
    texts: list[str],
    embedder,
) -> np.ndarray:
    return embedder.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )