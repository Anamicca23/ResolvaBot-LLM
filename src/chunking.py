"""
chunking.py - Robust NLTK-based text chunking with multiple fallbacks.
"""
import re

# Download NLTK data safely
def _ensure_nltk():
    try:
        import nltk
        for pkg in ("punkt", "punkt_tab", "wordnet", "omw-1.4"):
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass
        return nltk
    except ImportError:
        return None

nltk = _ensure_nltk()


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using NLTK, regex fallback, or simple split."""
    if not text or not text.strip():
        return []

    # Try NLTK sentence tokenizer
    if nltk:
        try:
            sentences = nltk.sent_tokenize(text)
            if sentences:
                return [s for s in sentences if s.strip()]
        except Exception:
            pass

    # Fallback: regex sentence splitter
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if sentences:
            return [s.strip() for s in sentences if s.strip()]
    except Exception:
        pass

    # Last resort: split by newlines then by period
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return lines if lines else [text]


def _tokenize(text: str) -> list[str]:
    """Tokenize text into words."""
    if nltk:
        try:
            return nltk.word_tokenize(text)
        except Exception:
            pass
    return text.split()


def chunk_text(text: str, chunk_size: int = 100) -> list[str]:
    """
    Split text into chunks of ~chunk_size tokens, preserving sentence boundaries.
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current_tokens = []

    for sentence in sentences:
        sentence_tokens = _tokenize(sentence)
        if not sentence_tokens:
            continue

        if len(current_tokens) + len(sentence_tokens) > chunk_size and current_tokens:
            chunks.append(" ".join(current_tokens))
            current_tokens = sentence_tokens
        else:
            current_tokens.extend(sentence_tokens)

    if current_tokens:
        chunks.append(" ".join(current_tokens))

    return [c for c in chunks if c.strip() and len(c.strip()) > 10]


def chunk_pages(pages: list[dict], chunk_size: int = 100) -> list[dict]:
    """
    Chunk a list of page dicts into text chunks with page metadata.
    Returns [{"chunk_id": 0, "page": 1, "text": "..."}, ...]
    """
    all_chunks = []
    chunk_id = 0

    for page_info in pages:
        page_num = page_info.get("page", 0)
        page_text = page_info.get("text", "")

        if not page_text or not page_text.strip():
            continue

        for chunk in chunk_text(page_text, chunk_size):
            if chunk.strip():
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": chunk,
                })
                chunk_id += 1

    return all_chunks


if __name__ == "__main__":
    sample = "This is sentence one. This is sentence two. " * 30
    chunks = chunk_text(sample, chunk_size=50)
    print(f"Chunks: {len(chunks)}")
    for i, c in enumerate(chunks[:3]):
        print(f"  [{i}] {c[:80]}")