"""
core/document_ai/prompts.py

Ported from paperbrain-ai (unchanged) — prompt templates for chat,
summarization, quiz, MCQ, and explanation. Kept separate from pipeline logic
so they're easy to review, tune, and quote directly in the capstone's
"Prompt Engineering Approach" documentation.
"""

CHAT_SYSTEM_INSTRUCTION = """You are an AI assistant that answers questions strictly using
the provided document context.

Rules:
1. Answer ONLY using the given context. If the answer is not present in the
   context, say clearly: "I couldn't find this in the document."
2. Do not invent facts, numbers, or details not present in the context.
3. Where helpful, mention which page(s) the information came from.
4. Keep answers concise and well-structured.
"""


def build_chat_prompt(question: str, retrieved_chunks: list) -> str:
    context = "\n\n".join(
        f"[Page {c['page']} - {c['source']}]\n{c['text']}" for c in retrieved_chunks
    )
    return f"""Context from the document:

{context}

Question: {question}

Answer using only the context above."""


def build_summary_prompt(text: str, style: str = "bullet points", length: str = "medium") -> str:
    return f"""Summarize the following document content in {style}, at {length} length.
Preserve key facts, figures, and conclusions. Do not add information not present
in the text.

Document content:
{text}

Summary:"""


def build_report_prompt(text: str) -> str:
    """New — the capstone brief asks for 'Generate Reports' as its own feature,
    distinct from a plain summary. Structured, section-based output rather than
    a bullet-point digest."""
    return f"""Using ONLY the content below, produce a structured report with these
sections: Overview, Key Findings, Supporting Details, and Conclusion.
Do not add information not present in the text.

Document content:
{text}

Report:"""


def build_quiz_prompt(text: str, n: int = 5, difficulty: str = "medium") -> str:
    return f"""Using ONLY the content below, generate {n} open-ended quiz questions
at {difficulty} difficulty that test understanding of the material.
Number them 1 to {n}. Do not include answers, only the questions.

Content:
{text}

Quiz Questions:"""


def build_mcq_prompt(text: str, n: int = 5) -> str:
    return f"""Using ONLY the content below, generate {n} multiple-choice questions.
Each question must have exactly 4 options and exactly one correct answer.
Return ONLY valid JSON (no markdown fences, no extra text) in this exact format:

[
  {{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A"}}
]

Content:
{text}
"""


def build_explain_prompt(text: str, topic: str = None) -> str:
    if topic:
        return f"""From the document content below, find the explanation of "{topic}"
and re-explain it simply, as if teaching a complete beginner. Use an analogy if useful.

Content:
{text}

Simple explanation of "{topic}":"""
    return f"""Identify the most complex or technical concepts in the content below,
and explain each one simply, as if teaching a beginner. List each concept as a
heading followed by a plain-language explanation.

Content:
{text}

Explanations:"""