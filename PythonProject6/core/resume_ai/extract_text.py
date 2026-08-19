"""
core/resume_ai/extract_text.py

Ported from resume-analyzer-nlp (unchanged) — pdfplumber text extraction.
Note this is a DIFFERENT PDF library from Document AI's PyMuPDF (fitz).
Kept as-is deliberately rather than unified: pdfplumber's extraction was
already tuned/tested for resume layouts specifically in the original
project, and swapping libraries here risks subtly changing extraction
quality for no real benefit.
"""

import pdfplumber


def extract_text_from_pdf(uploaded_file):
    """Accepts a file-like object (e.g. Streamlit's st.file_uploader result)
    and returns all extracted text as a single string, page breaks as \n."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text