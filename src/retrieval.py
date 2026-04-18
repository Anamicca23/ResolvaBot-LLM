"""
retrieval.py
------------
Hybrid retrieval combining:
  1. BM25 (keyword search via Whoosh)
  2. Dense Passage Retrieval (DPR / SBERT dense vectors via FAISS)

Results are merged and re-ranked using a Reciprocal Rank Fusion (RRF) score.
Query expansion via WordNet synonyms is also applied.
"""

from __future__ import annotations
import os
import tempfile
import shutil

import nltk
from nltk.corpus import wordnet

from whoosh import index as whoosh_index, scoring
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser, OrGroup
from whoosh.writing import AsyncWriter

from embeddings import embed_single
from vector_store import VectorStore

# Ensure NLTK data is available
for pkg in ("wordnet", "omw-1.4", "punkt", "punkt_tab"):
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass


# ── Query expansion ───────────────────────────────────────────────────────────
def expand_query(query: str, max_synonyms: int = 10) -> str:
    """
    Expand a query with WordNet synonyms.
    Returns the original query + synonyms as a space-separated string.
    """
    tokens = nltk.word_tokenize(query.lower())
    synonyms = set(tokens)
    for token in tokens:
        for synset in wordnet.synsets(token):
            for lemma in synset.lemmas():
                word = lemma.name().replace("_", " ")
                synonyms.add(word)
                if len(synonyms) >= max_synonyms + len(tokens):
                    break
    expanded = " ".join(synonyms)
    return expanded


# ── BM25 index ────────────────────────────────────────────────────────────────
class BM25Index:
    """Wraps a Whoosh index for BM25F keyword retrieval."""

    SCHEMA = Schema(
        chunk_id=ID(stored=True, unique=True),
        page=NUMERIC(stored=True),
        level=NUMERIC(stored=True),
        content=TEXT(stored=True),
    )

    def __init__(self, index_dir: str | None = None):
        self._temp = index_dir is None
        self._dir = index_dir or tempfile.mkdtemp(prefix="resolvabot_bm25_")
        self._ix = None

    def build(self, chunks: list[dict]) -> None:
        """Build the Whoosh index from a list of chunk dicts."""
        if os.path.exists(self._dir):
            shutil.rmtree(self._dir)
        os.makedirs(self._dir, exist_ok=True)

        self._ix = whoosh_index.create_in(self._dir, self.SCHEMA)
        writer = self._ix.writer()
        for chunk in chunks:
            writer.add_document(
                chunk_id=str(chunk.get("chunk_id", chunk.get("node_id", 0))),
                page=chunk.get("page", -1),
                level=chunk.get("level", 0),
                content=chunk["text"],
            )
        writer.commit()

    def search(self, query_str: str, top_k: int = 10) -> list[dict]:
        """BM25F search. Returns list of result dicts."""
        if self._ix is None:
            if whoosh_index.exists_in(self._dir):
                self._ix = whoosh_index.open_dir(self._dir)
            else:
                return []

        expanded = expand_query(query_str)
        qp = QueryParser("content", schema=self._ix.schema, group=OrGroup)
        try:
            q = qp.parse(expanded)
        except Exception:
            q = qp.parse(query_str)

        with self._ix.searcher(weighting=scoring.BM25F()) as searcher:
            hits = searcher.search(q, limit=top_k)
            return [
                {
                    "chunk_id": int(h["chunk_id"]),
                    "page": h["page"],
                    "level": h["level"],
                    "text": h["content"],
                    "bm25_score": h.score,
                }
                for h in hits
            ]

    def __del__(self):
        if self._temp and os.path.exists(self._dir):
            shutil.rmtree(self._dir, ignore_errors=True)


# ── Reciprocal Rank Fusion re-ranking ────────────────────────────────────────
def _rrf_merge(
    bm25_results: list[dict],
    dense_results: list[dict],
    k: int = 60,
    top_k: int = 10,
) -> list[dict]:
    """
    Merge BM25 and dense results using Reciprocal Rank Fusion.
    RRF score = 1/(k + rank_bm25) + 1/(k + rank_dense)
    """
    scores: dict[str, float] = {}
    data: dict[str, dict] = {}

    for rank, r in enumerate(bm25_results, start=1):
        key = r["text"][:100]  # use text prefix as unique key
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        data[key] = r

    for rank, r in enumerate(dense_results, start=1):
        key = r["text"][:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        if key not in data:
            data[key] = r

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for key, rrf_score in ranked[:top_k]:
        item = data[key].copy()
        item["rrf_score"] = rrf_score
        results.append(item)
    return results


# ── Hybrid retriever ──────────────────────────────────────────────────────────
class HybridRetriever:
    """
    Combines BM25 + FAISS dense retrieval with RRF re-ranking.
    """

    def __init__(self, bm25_index: BM25Index, vector_store: VectorStore):
        self.bm25 = bm25_index
        self.vs = vector_store

    def retrieve(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Retrieve relevant chunks using hybrid BM25 + dense search.
        Returns re-ranked results sorted by RRF score.
        """
        # BM25 retrieval
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        # Dense (SBERT) retrieval
        q_emb = embed_single(query)
        dense_results = self.vs.search(q_emb, top_k=top_k * 2, level_filter=0)

        # Merge with RRF
        merged = _rrf_merge(bm25_results, dense_results, top_k=top_k)
        return merged


if __name__ == "__main__":
    print("Query expansion test:")
    print(expand_query("algorithm sorting"))
