"""
core/resume_ai/cover_letter.py

New — the Task 7 brief asks for a Cover Letter Generator as part of Resume
AI, which the original offline analyzer project didn't include (it was
built purely around scoring/feedback, no generation). Rather than add a
second, separate LLM path, this reuses core/llm_wrapper.py — the same
LLMWrapper class AI Chat already uses — since cover letter writing is a
plain text-generation task with no retrieval step.
"""

from core.llm_wrapper import LLMWrapper

SYSTEM_PROMPT = """You are a professional cover letter writer. Write a concise,
specific, and genuine-sounding cover letter (250-350 words) tailored to the
job description, drawing only on details actually present in the resume.
Do not invent experience, skills, or qualifications not found in the resume.
Avoid generic filler phrases like "I am writing to express my interest."
Structure: a strong opening line, 1-2 paragraphs connecting real resume
experience to the job's requirements, and a brief closing call to action."""


def generate_cover_letter(resume_text: str, jd_text: str, company_name: str = "",
                           tone: str = "professional", provider: str = "gemini") -> str:
    llm = LLMWrapper(provider=provider)
    company_line = f"Company: {company_name}\n" if company_name else ""
    prompt = f"""{company_line}Tone: {tone}

Resume:
{resume_text}

Job description:
{jd_text}

Write the cover letter now."""
    return llm.generate(prompt, system=SYSTEM_PROMPT)