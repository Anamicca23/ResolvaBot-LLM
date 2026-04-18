"""
embeddings.py
-------------
Generates vector embeddings for text chunks using Sentence-BERT (SBERT).
Uses 'all-MiniLM-L6-v2' (384-dim) as the default model.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# Cached model instance (loaded once per process)
_model: SentenceTransformer | None = None
EMBEDDING_DIM = 384
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Load (or return cached) SBERT model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model


def generate_embeddings(texts: list[str], model_name: str = DEFAULT_MODEL,
                        batch_size: int = 64, show_progress: bool = False) -> np.ndarray:
    """
    Encode a list of strings into dense vectors.
    Returns numpy array of shape (N, EMBEDDING_DIM).
    """
    model = get_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,  # L2-normalize for cosine similarity via dot product
    )
    return embeddings


def embed_single(text: str) -> np.ndarray:
    """Embed a single string. Returns 1-D array."""
    return generate_embeddings([text])[0]


if __name__ == "__main__":
    sample_texts = ["What is machine learning?", "How do algorithms work?"]
    embs = generate_embeddings(sample_texts, show_progress=True)
    print(f"Embeddings shape: {embs.shape}")
    print(f"Sample norm: {np.linalg.norm(embs[0]):.4f}")
