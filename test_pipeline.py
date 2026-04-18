"""
test_pipeline.py
----------------
Verifies the full ResolvaBot pipeline works correctly WITHOUT needing
an OpenAI API key. Uses dummy text to test:
  ✅ Text chunking
  ✅ SBERT embeddings
  ✅ RAPTOR indexing (no-LLM mode)
  ✅ FAISS vector store
  ✅ BM25 keyword index
  ✅ Hybrid retrieval + RRF re-ranking
  ✅ Wikipedia fallback answer

Run from the project root:
    python test_pipeline.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

SAMPLE_TEXT = """
Chapter 1: Introduction to Algorithms
An algorithm is a step-by-step procedure for solving a problem or accomplishing a task.
Algorithms are fundamental to computer science and programming.

Sorting algorithms arrange elements in a specific order. Common sorting algorithms include
bubble sort, insertion sort, merge sort, and quicksort. Quicksort has average O(n log n)
time complexity and is widely used in practice.

Chapter 2: Data Structures
Data structures are ways of organizing data for efficient access and modification.
Common data structures include arrays, linked lists, stacks, queues, trees, and graphs.
A binary search tree allows O(log n) search, insertion, and deletion operations.

Chapter 3: Natural Language Processing
Natural language processing (NLP) is a field of AI focused on the interaction between
computers and human language. Techniques include tokenization, stemming, lemmatization,
named entity recognition, and sentiment analysis. Transformers and BERT have revolutionized NLP.

Chapter 4: Machine Learning
Machine learning is a branch of artificial intelligence that enables systems to learn
from data. Supervised learning uses labeled data, unsupervised learning finds patterns
in unlabeled data, and reinforcement learning trains agents via rewards and penalties.
"""


def run_tests():
    print("=" * 55)
    print("  ResolvaBot LLM — Pipeline Test")
    print("=" * 55)

    # ── Test 1: Chunking ──────────────────────────────────────────────────────
    print("\n[1/6] Testing text chunking...")
    from chunking import chunk_text
    chunks_raw = chunk_text(SAMPLE_TEXT, chunk_size=50)
    assert len(chunks_raw) > 2, "Expected multiple chunks"
    print(f"  ✅ {len(chunks_raw)} chunks created")

    pages = [{"page": 1, "text": SAMPLE_TEXT}]
    from chunking import chunk_pages
    chunks = chunk_pages(pages, chunk_size=50)
    print(f"  ✅ chunk_pages: {len(chunks)} chunks with page metadata")

    # ── Test 2: Embeddings ────────────────────────────────────────────────────
    print("\n[2/6] Testing SBERT embeddings...")
    from embeddings import generate_embeddings, embed_single
    embs = generate_embeddings([c["text"] for c in chunks])
    assert embs.shape[0] == len(chunks), "Embedding count mismatch"
    assert embs.shape[1] == 384, f"Expected 384-dim, got {embs.shape[1]}"
    print(f"  ✅ Embeddings shape: {embs.shape}")

    # ── Test 3: RAPTOR index (no LLM) ─────────────────────────────────────────
    print("\n[3/6] Testing RAPTOR indexing (no LLM mode)...")
    from raptor_index import build_raptor_index
    raptor_nodes = build_raptor_index(chunks, max_levels=2, use_llm=False)
    assert len(raptor_nodes) >= len(chunks), "Should have at least as many nodes as chunks"
    levels = set(n.level for n in raptor_nodes)
    print(f"  ✅ {len(raptor_nodes)} nodes across {len(levels)} levels: {sorted(levels)}")

    # ── Test 4: FAISS vector store ────────────────────────────────────────────
    print("\n[4/6] Testing FAISS vector store...")
    from vector_store import VectorStore
    vs = VectorStore()
    vs.add_nodes(raptor_nodes)
    assert vs.total_nodes == len(raptor_nodes)
    q_emb = embed_single("sorting algorithm")
    results = vs.search(q_emb, top_k=5)
    assert len(results) > 0
    print(f"  ✅ {vs.total_nodes} nodes stored | query returned {len(results)} results")
    print(f"     Top result: '{results[0]['text'][:60]}...'")

    # ── Test 5: BM25 + Hybrid retrieval ───────────────────────────────────────
    print("\n[5/6] Testing BM25 + hybrid retrieval...")
    from retrieval import BM25Index, HybridRetriever, expand_query
    bm25_data = [{"chunk_id": n.node_id, "page": n.page, "level": n.level, "text": n.text}
                  for n in raptor_nodes]
    bm25 = BM25Index()
    bm25.build(bm25_data)
    bm25_results = bm25.search("algorithm sorting", top_k=5)
    print(f"  ✅ BM25: {len(bm25_results)} results")

    retriever = HybridRetriever(bm25, vs)
    hybrid_results = retriever.retrieve("What is quicksort?", top_k=5)
    assert len(hybrid_results) > 0
    print(f"  ✅ Hybrid: {len(hybrid_results)} results (RRF re-ranked)")
    print(f"     Top: '{hybrid_results[0]['text'][:60]}...'")

    expanded = expand_query("sort")
    print(f"  ✅ Query expansion: 'sort' → '{expanded[:60]}...'")

    # ── Test 6: Wikipedia fallback ────────────────────────────────────────────
    print("\n[6/6] Testing Wikipedia fallback...")
    from question_answering import get_answer_from_wikipedia
    wiki_answer = get_answer_from_wikipedia("quicksort")
    assert len(wiki_answer) > 50, "Expected non-trivial Wikipedia answer"
    print(f"  ✅ Wikipedia answer ({len(wiki_answer)} chars): '{wiki_answer[:80]}...'")

    # ── Full answer_question (no LLM) ─────────────────────────────────────────
    from question_answering import answer_question
    result = answer_question("What is quicksort?", hybrid_results, use_llm=False)
    assert result["answer"], "Expected a non-empty answer"
    print(f"\n  📋 Sample answer (no LLM): '{result['answer'][:120]}...'")
    print(f"     Source: {result['source']}")

    print("\n" + "=" * 55)
    print("  ✅ All 6 tests passed! Pipeline is working correctly.")
    print("=" * 55)
    print("\nNext: Add your OPENAI_API_KEY to .env and run:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    run_tests()
