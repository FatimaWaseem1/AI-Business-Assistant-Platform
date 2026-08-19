"""
pages/2_Document_AI.py

Same template as 1_AI_Chat.py (require_login -> interact -> save history),
but this module needs a processing step first (upload -> build vector store)
before chat/summarize/report can run, so the pipeline object is cached in
st.session_state rather than rebuilt on every interaction.

Covers the three Document AI features from the Task 7 brief (Chat with PDFs,
Summarize Documents, Generate Reports), plus Quiz/MCQ/Explain carried over
from paperbrain-ai as bonus tabs — already built and tested, so there's no
reason to leave them out.
"""

import streamlit as st
from core.auth import require_login
from core.database import save_message, get_history
from core.document_ai.rag_pipeline import RAGPipeline

MODULE_NAME = "document_ai"

require_login()
user_id = st.session_state["user_id"]

st.title("Document AI")
st.caption("Upload PDFs, then chat with them, summarize, or generate a structured report.")

# --- upload + process ---
uploaded_files = st.file_uploader("Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🔄 Process Document(s)", disabled=not uploaded_files):
    with st.spinner("Extracting text, chunking, and building the vector index..."):
        pipeline = RAGPipeline()
        for f in uploaded_files:
            pipeline.add_pdf_from_bytes(f.read(), f.name)
        st.session_state["doc_pipeline"] = pipeline
    st.success(f"Processed {len(uploaded_files)} document(s). Ready to use below.")

pipeline: RAGPipeline | None = st.session_state.get("doc_pipeline")

if pipeline is None or not pipeline.vector_store.is_ready():
    st.info("Upload PDF(s) and click 'Process Document(s)' to get started.")
    st.stop()

tab_chat, tab_summary, tab_report, tab_quiz, tab_mcq, tab_explain = st.tabs(
    ["Chat", "Summary", "Report", "Quiz", "MCQs", "Explain"]
)

# --- Chat with PDFs ---
with tab_chat:
    for msg in get_history(user_id, MODULE_NAME):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask a question about the document(s)..."):
        with st.chat_message("user"):
            st.markdown(question)
        save_message(user_id, MODULE_NAME, "user", question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant context..."):
                answer, sources = pipeline.answer_question(question)
            st.markdown(answer)
            if sources:
                with st.expander("Sources"):
                    for s in sources:
                        st.caption(f"Page {s['page']} — {s['source']}")
        save_message(user_id, MODULE_NAME, "assistant", answer)

# --- Summarize Documents ---
with tab_summary:
    col1, col2 = st.columns(2)
    style = col1.selectbox("Style", ["bullet points", "paragraph"])
    length = col2.selectbox("Length", ["short", "medium", "long"])
    if st.button("Generate summary"):
        with st.spinner("Summarizing..."):
            summary = pipeline.summarize(style=style, length=length)
        st.markdown(summary)
        st.download_button("Download summary (.txt)", summary, file_name="summary.txt")

# --- Generate Reports ---
with tab_report:
    if st.button("Generate report"):
        with st.spinner("Generating structured report..."):
            report = pipeline.generate_report()
        st.markdown(report)
        st.download_button("Download report (.txt)", report, file_name="report.txt")

# --- Quiz (bonus, carried over from paperbrain-ai) ---
with tab_quiz:
    n_quiz = st.slider("Number of questions", 3, 10, 5, key="quiz_n")
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
    if st.button("Generate quiz"):
        with st.spinner("Generating quiz questions..."):
            quiz = pipeline.generate_quiz(n=n_quiz, difficulty=difficulty)
        st.markdown(quiz)

# --- MCQs (bonus, carried over from paperbrain-ai) ---
with tab_mcq:
    n_mcq = st.slider("Number of questions", 3, 10, 5, key="mcq_n")
    if st.button("Generate MCQs"):
        with st.spinner("Generating multiple-choice questions..."):
            mcqs = pipeline.generate_mcqs(n=n_mcq)
        st.code(mcqs, language="json")

# --- Explain (bonus, carried over from paperbrain-ai) ---
with tab_explain:
    topic = st.text_input("Specific topic to explain (leave blank for 'hardest concepts in the doc')")
    if st.button("Explain"):
        with st.spinner("Explaining..."):
            explanation = pipeline.explain(topic or None)
        st.markdown(explanation)