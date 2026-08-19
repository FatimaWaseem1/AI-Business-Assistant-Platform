"""
core/document_ai/rag_pipeline.py

Adapted from paperbrain-ai's rag_chain.py. Same responsibilities: ties the
full RAG pipeline together (PDF -> chunks -> vector store -> retrieval ->
generation) as a single class so pages/2_Document_AI.py has one thing to
import and call.

Difference from the original: paperbrain-ai read settings from its own
config.py (project-specific, backed by a standalone .env). Here it reads
straight from this shell's shared .env via os.environ, since GEMINI_API_KEY
is already loaded once by core/llm_wrapper.py's load_dotenv() call.
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

from .pdf_processor import extract_text_from_bytes
from .chunking import chunk_pages
from .vector_store import PDFVectorStore
from .gemini_rag_client import generate_content, GeminiChatSession, DEFAULT_CHAT_MODEL, DEFAULT_EMBEDDING_MODEL
from .prompts import (
    CHAT_SYSTEM_INSTRUCTION,
    build_chat_prompt,
    build_summary_prompt,
    build_report_prompt,
    build_quiz_prompt,
    build_mcq_prompt,
    build_explain_prompt,
)

load_dotenv()

CHUNK_SIZE = int(os.environ.get("DOC_AI_CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.environ.get("DOC_AI_CHUNK_OVERLAP", 150))
TOP_K = int(os.environ.get("DOC_AI_TOP_K", 4))
TEMPERATURE = float(os.environ.get("DOC_AI_TEMPERATURE", 0.3))
MAX_OUTPUT_TOKENS = int(os.environ.get("DOC_AI_MAX_OUTPUT_TOKENS", 1024))


class RAGPipeline:
    """Holds one vector store (potentially built from multiple PDFs) and
    exposes every operation the Document AI page needs."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ["GEMINI_API_KEY"]
        self.vector_store = PDFVectorStore(self.api_key, DEFAULT_EMBEDDING_MODEL)

    # -- Ingestion -----------------------------------------------------
    def add_pdf_from_bytes(self, file_bytes: bytes, source_name: str):
        pages = extract_text_from_bytes(file_bytes, source_name)
        chunks = chunk_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        self.vector_store.add(chunks)

    # -- Retrieval -------------------------------------------------------
    def retrieve_chunks_with_metadata(self, question: str, k: int = None) -> List[Dict]:
        return self.vector_store.search(question, k=k or TOP_K)

    # -- Feature: Chat (multi-turn) ---------------------------------------
    def start_chat_session(self) -> GeminiChatSession:
        return GeminiChatSession(self.api_key, DEFAULT_CHAT_MODEL, CHAT_SYSTEM_INSTRUCTION)

    def answer_question(self, question: str) -> tuple[str, List[Dict]]:
        """Single-turn RAG answer (retrieve -> generate). Returns (answer, sources)
        so the page can show which pages/PDFs the answer drew from."""
        chunks = self.retrieve_chunks_with_metadata(question)
        prompt = build_chat_prompt(question, chunks)
        answer = generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                   temperature=TEMPERATURE, max_output_tokens=MAX_OUTPUT_TOKENS)
        return answer, chunks

    # -- Feature: Summarization --------------------------------------------
    def summarize(self, style: str = "bullet points", length: str = "medium",
                  section_query: Optional[str] = None) -> str:
        if section_query:
            chunks = self.vector_store.search(section_query, k=8)
            text = "\n\n".join(c["text"] for c in chunks)
        else:
            text = self.vector_store.get_all_text()
        prompt = build_summary_prompt(text, style, length)
        return generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                 temperature=0.2, max_output_tokens=MAX_OUTPUT_TOKENS)

    # -- Feature: Generate Report ------------------------------------------
    def generate_report(self) -> str:
        text = self.vector_store.get_all_text()
        prompt = build_report_prompt(text)
        return generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                 temperature=0.2, max_output_tokens=MAX_OUTPUT_TOKENS)

    # -- Feature: Quiz generation --------------------------------------------
    def generate_quiz(self, n: int = 5, difficulty: str = "medium") -> str:
        text = self.vector_store.get_all_text()
        prompt = build_quiz_prompt(text, n, difficulty)
        return generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                 temperature=0.5, max_output_tokens=MAX_OUTPUT_TOKENS)

    # -- Feature: MCQ generation --------------------------------------------
    def generate_mcqs(self, n: int = 5) -> str:
        text = self.vector_store.get_all_text()
        prompt = build_mcq_prompt(text, n)
        return generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                 temperature=0.5, max_output_tokens=MAX_OUTPUT_TOKENS)

    # -- Feature: Explain difficult topics -----------------------------------
    def explain(self, topic: Optional[str] = None) -> str:
        if topic:
            chunks = self.vector_store.search(topic, k=6)
            text = "\n\n".join(c["text"] for c in chunks)
        else:
            text = self.vector_store.get_all_text()
        prompt = build_explain_prompt(text, topic)
        return generate_content(prompt, self.api_key, DEFAULT_CHAT_MODEL,
                                 temperature=0.3, max_output_tokens=MAX_OUTPUT_TOKENS)