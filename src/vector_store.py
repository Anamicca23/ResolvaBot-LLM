"""
vector_store.py
---------------
Portable vector store using FAISS (no Docker required).
Stores all RAPTOR nodes (embeddings + metadata) in memory,
with optional save/load to disk.
"""

from __future__ import annotations
import os
import pickle
import numpy as np
import faiss

from raptor_index import RaptorNode
from embeddings import EMBEDDING_DIM


class VectorStore:
    """
    In-memory FAISS index backed by a list of RaptorNode objects.
    Uses inner-product (cosine) search because embeddings are L2-normalized.
    """

    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(dim)
        self.nodes: list[RaptorNode] = []

    # ── Indexing ──────────────────────────────────────────────────────────────
    def add_nodes(self, nodes: list[RaptorNode]) -> None:
        """Add a list of RaptorNode objects to the FAISS index."""
        if not nodes:
            return
        embeddings = np.stack([n.embedding for n in nodes]).astype("float32")
        # FAISS expects C-contiguous float32
        embeddings = np.ascontiguousarray(embeddings)
        self.index.add(embeddings)
        self.nodes.extend(nodes)

    def clear(self) -> None:
        """Reset the index."""
        self.index = faiss.IndexFlatIP(self.dim)
        self.nodes = []

    # ── Search ────────────────────────────────────────────────────────────────
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        level_filter: int | None = None,
    ) -> list[dict]:
        """
        Search for the top-k most similar nodes.
        Optionally filter by RAPTOR level (0 = original chunks).
        Returns list of dicts with keys: text, page, level, score.
        """
        if self.index.ntotal == 0:
            return []

        q = np.ascontiguousarray(
            query_embedding.reshape(1, -1).astype("float32")
        )
        # Over-fetch so we can filter by level
        k = min(self.index.ntotal, top_k * 3 if level_filter is not None else top_k)
        scores, idxs = self.index.search(q, k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0 or idx >= len(self.nodes):
                continue
            node = self.nodes[idx]
            if level_filter is not None and node.level != level_filter:
                continue
            results.append({
                "text": node.text,
                "page": node.page,
                "level": node.level,
                "node_id": node.node_id,
                "score": float(score),
            })
            if len(results) >= top_k:
                break

        return results

    # ── Persistence ───────────────────────────────────────────────────────────
    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        faiss.write_index(self.index, path + ".faiss")
        with open(path + ".meta", "wb") as f:
            pickle.dump(self.nodes, f)
        print(f"Vector store saved to {path}.faiss / .meta")

    def load(self, path: str) -> None:
        self.index = faiss.read_index(path + ".faiss")
        with open(path + ".meta", "rb") as f:
            self.nodes = pickle.load(f)
        print(f"Loaded {len(self.nodes)} nodes from {path}")

    @property
    def total_nodes(self) -> int:
        return len(self.nodes)


if __name__ == "__main__":
    from embeddings import generate_embeddings
    store = VectorStore()
    from raptor_index import RaptorNode
    import numpy as np

    dummy_nodes = [
        RaptorNode(i, f"Sample text {i}", generate_embeddings([f"Sample text {i}"])[0], 0, page=i)
        for i in range(5)
    ]
    store.add_nodes(dummy_nodes)
    q = generate_embeddings(["Sample text 2"])[0]
    results = store.search(q, top_k=3)
    for r in results:
        print(r)
