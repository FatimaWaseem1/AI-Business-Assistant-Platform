"""
core/document_ai/pdf_processor.py

Ported from paperbrain-ai (unchanged) — PyMuPDF text extraction, page-by-page.
Keeps page numbers attached to each block of extracted text, so retrieved
chunks can later be traced back to "this came from page 4 of document.pdf" —
important for both UX (citations) and multi-PDF source attribution.
"""

from typing import List, Dict
import fitz  # PyMuPDF


def extract_text_from_bytes(file_bytes: bytes, source_name: str) -> List[Dict]:
    """Extract text page-by-page directly from in-memory bytes — matches what
    Streamlit's st.file_uploader gives you.

    Returns: [{"page": 1, "text": "...", "source": "document.pdf"}, ...]
    """
    pages_data = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:  # skip fully blank pages (common at start/end of PDFs)
            pages_data.append({"page": page_num, "text": text, "source": source_name})
    doc.close()
    return pages_data