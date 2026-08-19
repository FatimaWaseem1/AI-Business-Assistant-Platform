"""
core/document_ai/vector_store.py

Ported from paperbrain-ai (unchanged logic) — FAISS-backed vector store for
chunk embeddings. FAISS only stores/searches vectors — it has no idea what
the original text was. We keep a parallel list (`self.chunks`) so that when
FAISS returns "index #47 is closest," we can map that straight back to the
chunk's text, page number, and source PDF.
"""

from typing import List, Dict
import numpy as np
import faiss

from .gemini_rag_client import embed_batch, embed_text, DEFAULT_EMBEDDING_MODEL


class PDFVectorStore:
    def __init__(self, api_key: str, embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.index = None
        self.chunks: List[Dict] = []
        self.embedding_dim = None

    def build(self, chunks: List[Dict]):
        """Embed all chunks and build a fresh FAISS index."""
        texts = [c["text"] for c in chunks]
        embeddings = embed_batch(texts, self.api_key, self.embedding_model, task_type="retrieval_document")
        vectors = np.array(embeddings, dtype="float32")
        self.embedding_dim = vectors.shape[1]
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(vectors)
        self.chunks = chunks

    def add(self, chunks: List[Dict]):
        """Add more chunks to an existing index (multi-PDF support)."""
        if self.index is None:
            self.build(chunks)
            return
        texts = [c["text"] for c in chunks]
        embeddings = embed_batch(texts, self.api_key, self.embedding_model, task_type="retrieval_document")
        vectors = np.array(embeddings, dtype="float32")
        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 4) -> List[Dict]:
        """Return the top-k most similar chunks to the query."""
        if self.index is None or len(self.chunks) == 0:
            return []
        query_vector = embed_text(query, self.api_key, self.embedding_model, task_type="retrieval_query")
        query_vector = np.array([query_vector], dtype="float32")
        k = min(k, len(self.chunks))
        _distances, indices = self.index.search(query_vector, k)
        return [self.chunks[idx] for idx in indices[0] if idx != -1]

    def get_all_text(self) -> str:
        """Concatenate all chunk text — used for whole-document summarization."""
        return "\n\n".join(c["text"] for c in self.chunks)

    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0