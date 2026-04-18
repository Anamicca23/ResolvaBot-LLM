"""
raptor_index.py
---------------
RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.

Steps:
  1. Embed all text chunks.
  2. Cluster with Gaussian Mixture Models (GMM, soft clustering).
  3. Summarize each cluster using an LLM (GPT-3.5-turbo).
  4. Re-embed the summaries.
  5. Recursively cluster+summarize until only 1 cluster remains.

Returns a flat list of all nodes (original chunks + summaries at all levels)
suitable for storing in the vector index.
"""

from __future__ import annotations
import os
import numpy as np
from dataclasses import dataclass, field
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import normalize
from dotenv import load_dotenv

load_dotenv()

from embeddings import generate_embeddings

# ── OpenAI client (modern SDK ≥ 1.0) ─────────────────────────────────────────
from openai import OpenAI
_oai_client: OpenAI | None = None

def _get_openai_client() -> OpenAI:
    global _oai_client
    if _oai_client is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("sk-your"):
            raise ValueError(
                "OPENAI_API_KEY is not set. Please add it to your .env file."
            )
        _oai_client = OpenAI(api_key=api_key)
    return _oai_client


# ── Data model ────────────────────────────────────────────────────────────────
@dataclass
class RaptorNode:
    node_id: int
    text: str
    embedding: np.ndarray
    level: int          # 0 = original chunk, 1+ = summary levels
    page: int = -1      # source page (only for level-0 nodes)
    cluster: int = -1   # cluster label assigned at this level


# ── LLM summarization ─────────────────────────────────────────────────────────
def _summarize_cluster(texts: list[str]) -> str:
    """Use GPT-3.5-turbo to summarize a list of text chunks."""
    combined = "\n\n".join(texts[:20])  # cap at 20 chunks to stay under token limit
    client = _get_openai_client()
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise technical summarizer. "
                        "Summarize the following text passages into a single, "
                        "coherent paragraph capturing the key ideas."
                    ),
                },
                {"role": "user", "content": combined},
            ],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback: truncated concatenation (still useful for retrieval)
        return combined[:500]


# ── GMM clustering ────────────────────────────────────────────────────────────
def _cluster_embeddings(embeddings: np.ndarray, n_components: int | None = None) -> np.ndarray:
    """
    Cluster embeddings with GMM (soft clustering).
    Returns hard labels via argmax of responsibilities.
    """
    n = len(embeddings)
    if n < 2:
        return np.zeros(n, dtype=int)

    # Automatically choose n_components if not provided
    if n_components is None:
        n_components = max(2, min(10, n // 5))

    n_components = min(n_components, n)
    normed = normalize(embeddings, norm="l2")

    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type="full",
        random_state=42,
        max_iter=200,
        n_init=3,
    )
    gmm.fit(normed)
    labels = gmm.predict(normed)
    return labels


# ── Single RAPTOR level ───────────────────────────────────────────────────────
def _build_level(
    nodes: list[RaptorNode],
    level: int,
    next_node_id: int,
    n_components: int | None = None,
) -> tuple[list[RaptorNode], int]:
    """
    Cluster existing nodes, summarize each cluster, return new summary nodes.
    """
    embeddings = np.stack([n.embedding for n in nodes])
    labels = _cluster_embeddings(embeddings, n_components)

    summary_nodes: list[RaptorNode] = []
    for cluster_id in sorted(set(labels)):
        cluster_texts = [nodes[i].text for i, lbl in enumerate(labels) if lbl == cluster_id]
        summary_text = _summarize_cluster(cluster_texts)
        summary_emb = generate_embeddings([summary_text])[0]
        summary_nodes.append(
            RaptorNode(
                node_id=next_node_id,
                text=summary_text,
                embedding=summary_emb,
                level=level,
                cluster=int(cluster_id),
            )
        )
        next_node_id += 1

    return summary_nodes, next_node_id


# ── Full RAPTOR tree ──────────────────────────────────────────────────────────
def build_raptor_index(
    chunks: list[dict],  # [{"chunk_id", "page", "text"}, ...]
    max_levels: int = 3,
    n_components: int | None = None,
    use_llm: bool = True,
) -> list[RaptorNode]:
    """
    Build the full RAPTOR index.
    Returns ALL nodes across all levels (original + summaries).
    Set use_llm=False to skip LLM summarization (uses truncation instead).
    """
    print(f"  Building RAPTOR index for {len(chunks)} chunks...")

    # Level 0 – original chunks
    texts = [c["text"] for c in chunks]
    print("  Generating embeddings for base chunks...")
    embeddings = generate_embeddings(texts, show_progress=True)

    all_nodes: list[RaptorNode] = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        all_nodes.append(
            RaptorNode(
                node_id=i,
                text=chunk["text"],
                embedding=emb,
                level=0,
                page=chunk.get("page", -1),
            )
        )

    next_node_id = len(all_nodes)
    current_level_nodes = all_nodes[:]

    for level in range(1, max_levels + 1):
        if len(current_level_nodes) < 2:
            break  # Can't cluster a single node
        print(f"  RAPTOR level {level}: clustering {len(current_level_nodes)} nodes...")

        if not use_llm:
            # Fast mode: skip LLM, use truncated text
            labels = _cluster_embeddings(
                np.stack([n.embedding for n in current_level_nodes]), n_components
            )
            summary_nodes: list[RaptorNode] = []
            for cluster_id in sorted(set(labels)):
                cluster_texts = [
                    current_level_nodes[i].text
                    for i, lbl in enumerate(labels)
                    if lbl == cluster_id
                ]
                summary_text = " ".join(cluster_texts)[:600]
                summary_emb = generate_embeddings([summary_text])[0]
                summary_nodes.append(
                    RaptorNode(
                        node_id=next_node_id,
                        text=summary_text,
                        embedding=summary_emb,
                        level=level,
                        cluster=int(cluster_id),
                    )
                )
                next_node_id += 1
        else:
            summary_nodes, next_node_id = _build_level(
                current_level_nodes, level, next_node_id, n_components
            )

        all_nodes.extend(summary_nodes)
        current_level_nodes = summary_nodes
        print(f"    → {len(summary_nodes)} summary nodes at level {level}")

    print(f"  RAPTOR index complete: {len(all_nodes)} total nodes.")
    return all_nodes


if __name__ == "__main__":
    # Quick smoke test without LLM
    dummy_chunks = [
        {"chunk_id": i, "page": 1, "text": f"Sample text chunk number {i}. " * 5}
        for i in range(15)
    ]
    nodes = build_raptor_index(dummy_chunks, max_levels=2, use_llm=False)
    print(f"Nodes: {len(nodes)}")
    for n in nodes:
        print(f"  Level {n.level} | node {n.node_id}: {n.text[:60]}")
