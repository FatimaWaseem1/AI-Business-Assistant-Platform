"""
core/document_ai/gemini_rag_client.py

Ported from paperbrain-ai's gemini_client.py. Isolating embeddings + generation
here keeps the rest of the pipeline provider-agnostic, same principle as
core/llm_wrapper.py for the other modules — this file is deliberately separate
from llm_wrapper.py because RAG needs embed_content (not just generate_content),
which the generic wrapper doesn't expose.

Model names updated from the original project (gemini-2.0-flash /
text-embedding-004, both since retired) to the current stable equivalents:
gemini-3.6-flash and gemini-embedding-001. If Google retires these too,
change DEFAULT_CHAT_MODEL / DEFAULT_EMBEDDING_MODEL below — nothing else
needs to change.
"""

from typing import List
import socket
import google.generativeai as genai

DEFAULT_CHAT_MODEL = "gemini-3.6-flash"
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"

# paperbrain-ai hit DNS/IPv6 resolution issues on some networks; forcing
# IPv4-only lookups fixed it there, so it's carried over here unchanged.
_original_getaddrinfo = socket.getaddrinfo


def _ipv4_only_getaddrinfo(*args, **kwargs):
    return [r for r in _original_getaddrinfo(*args, **kwargs) if r[0] == socket.AF_INET]


socket.getaddrinfo = _ipv4_only_getaddrinfo

_configured_key = None


def _ensure_configured(api_key: str):
    global _configured_key
    if _configured_key != api_key:
        genai.configure(api_key=api_key)
        _configured_key = api_key


def embed_text(text: str, api_key: str, model: str = DEFAULT_EMBEDDING_MODEL,
                task_type: str = "retrieval_document") -> List[float]:
    """Embed a single piece of text. task_type differs for documents vs. queries —
    Gemini's embedding model uses this to optimize the vector for its role."""
    _ensure_configured(api_key)
    result = genai.embed_content(model=model, content=text, task_type=task_type)
    return result["embedding"]


def embed_batch(texts: List[str], api_key: str, model: str = DEFAULT_EMBEDDING_MODEL,
                 task_type: str = "retrieval_document") -> List[List[float]]:
    """Embed multiple texts. Loops one-by-one — fine for a single PDF's worth
    of chunks in this kind of project."""
    return [embed_text(t, api_key, model, task_type) for t in texts]


def generate_content(prompt: str, api_key: str, model: str = DEFAULT_CHAT_MODEL,
                      temperature: float = 0.3, max_output_tokens: int = 1024) -> str:
    """Single-turn generation call (summary/quiz/MCQ/explain — none of these
    need multi-turn chat memory the way Q&A chat does)."""
    _ensure_configured(api_key)
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_output_tokens,
        ),
    )
    return response.text


class GeminiChatSession:
    """Multi-turn chat session, used for the Q&A tab specifically."""

    def __init__(self, api_key: str, model: str, system_instruction: str, history=None):
        _ensure_configured(api_key)
        self._model = genai.GenerativeModel(model, system_instruction=system_instruction)
        self._chat = self._model.start_chat(history=history or [])

    def send(self, message: str, temperature: float = 0.3, max_output_tokens: int = 1024) -> str:
        response = self._chat.send_message(
            message,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_output_tokens,
            ),
        )
        return response.text