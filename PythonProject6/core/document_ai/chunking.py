"""
core/document_ai/chunking.py

Ported from paperbrain-ai (unchanged) — LangChain's RecursiveCharacterTextSplitter,
which tries to split on paragraph boundaries first, then sentences, then words —
preserving semantic coherence better than a naive fixed-length character split.
"""

from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(pages_data: List[Dict], chunk_size: int = 800, chunk_overlap: int = 150) -> List[Dict]:
    """
    Split extracted page text into overlapping chunks.

    Input:  [{"page": 1, "text": "...", "source": "doc.pdf"}, ...]
    Output: [{"text": "...", "page": 1, "source": "doc.pdf", "chunk_id": 0}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    chunk_id = 0
    for page in pages_data:
        for chunk_text in splitter.split_text(page["text"]):
            chunks.append({
                "text": chunk_text,
                "page": page["page"],
                "source": page["source"],
                "chunk_id": chunk_id,
            })
            chunk_id += 1
    return chunks