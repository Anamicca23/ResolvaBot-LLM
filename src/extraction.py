"""
extraction.py - Robust PDF text extraction using PyMuPDF.
Falls back through multiple strategies if primary extraction returns empty text.
"""
import fitz  # PyMuPDF
import io
import os

# Safely detect Tesseract
OCR_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    pytesseract.get_tesseract_version()
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


def _extract_page_text(page) -> str:
    """Try multiple extraction methods for a single page."""
    # Method 1: standard get_text
    text = page.get_text("text")
    if text and text.strip():
        return text

    # Method 2: get_text with blocks (better for multi-column)
    try:
        blocks = page.get_text("blocks")
        if blocks:
            text = "\n".join(b[4] for b in blocks if b[4].strip())
            if text.strip():
                return text
    except Exception:
        pass

    # Method 3: get_text raw
    try:
        text = page.get_text("rawtext")
        if text and text.strip():
            return text
    except Exception:
        pass

    # Method 4: OCR (only if Tesseract is installed)
    if OCR_AVAILABLE:
        try:
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
            if text.strip():
                return text
        except Exception:
            pass

    return ""


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text page-by-page from PDF bytes.
    Returns [{"page": 1, "text": "..."}, ...]
    Raises ValueError if no text could be extracted from any page.
    """
    pages = []
    pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    try:
        total_pages = len(pdf_document)
        for page_num in range(total_pages):
            page = pdf_document.load_page(page_num)
            page_text = _extract_page_text(page)
            pages.append({"page": page_num + 1, "text": page_text})
    finally:
        pdf_document.close()

    # Check if we got any text at all
    total_chars = sum(len(p["text"]) for p in pages)
    if total_chars == 0:
        raise ValueError(
            f"Could not extract any text from the PDF ({len(pages)} pages scanned). "
            "This may be a scanned/image-only PDF. Install Tesseract OCR for support."
        )

    return pages


def extract_text_from_pdf_path(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pages = extract_text_from_pdf_bytes(f.read())
    return "\n".join(p["text"] for p in pages)