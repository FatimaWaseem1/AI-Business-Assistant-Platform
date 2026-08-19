"""
pages/3_Resume_AI.py

Different shape from AI Chat / Document AI: this isn't a conversation, it's
a one-shot analysis (resume + job description -> scored report), so instead
of a chat_input loop this page is a form -> results layout. The "history"
core feature is still honored: each analysis run is logged as a single
message pair in the shared chat_history table, so it shows up consistently
with every other module even though the interaction pattern differs.
"""

import streamlit as st
from core.auth import require_login
from core.database import save_message, get_history
from core.resume_ai.extract_text import extract_text_from_pdf
from core.resume_ai.analyzer import analyze_resume
from core.resume_ai.cover_letter import generate_cover_letter

MODULE_NAME = "resume_ai"

require_login()
user_id = st.session_state["user_id"]

st.title("Resume AI")
st.caption("Upload your resume and a job description to get a scored, ATS-style analysis.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Resume (PDF)", type=["pdf"])
with col2:
    jd_text = st.text_area("Job description", height=200, placeholder="Paste the job description here...")

if st.button("Analyze", disabled=not (resume_file and jd_text)):
    with st.spinner("Extracting resume text and running analysis..."):
        resume_text = extract_text_from_pdf(resume_file)
        result = analyze_resume(resume_text, jd_text)
        st.session_state["resume_text"] = resume_text
        st.session_state["jd_text"] = jd_text
        st.session_state["resume_result"] = result
    if "error" not in result:
        save_message(user_id, MODULE_NAME, "user", f"Analyzed resume against a {len(jd_text)}-character job description.")
        save_message(user_id, MODULE_NAME, "assistant",
                     f"Match score: {result['match_score']}% | Overall score: {result['overall_professional_score']}/100")

result = st.session_state.get("resume_result")

if result and "error" in result:
    st.error(result["error"])
elif result:
    st.divider()

    # --- top-line scores ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Match score", f"{result['match_score']}%")
    m2.metric("Overall score", f"{result['overall_professional_score']}/100")
    m3.metric("Content", f"{result['content_score']}/100")
    m4.metric("Format", f"{result['format_score']}/100")

    st.caption(
        f"Match score = TF-IDF (keyword) × 0.3 + Semantic (meaning) × 0.7 "
        f"— TF-IDF: {result['tfidf_score']}%, Semantic: {result['semantic_score']}%"
    )

    # --- skills ---
    st.subheader("Skills")
    sk1, sk2 = st.columns(2)
    with sk1:
        st.markdown("**✅ Matched**")
        st.write(", ".join(result["matched_skills"]) or "None found")
    with sk2:
        st.markdown("**❌ Missing (from JD)**")
        st.write(", ".join(result["missing_skills"]) or "None — great coverage")

    # --- sections / contact / verbs ---
    st.subheader("Structure & formatting")
    sections = result["sections"]
    if sections["missing_required"]:
        st.warning(f"Missing required sections: {', '.join(sections['missing_required'])}")
    else:
        st.success("All required sections present (Experience, Education, Skills).")

    contact = result["contact"]
    for issue in contact["issues"]:
        st.warning(issue)

    if result["verbs"]["weak_phrases_found"]:
        st.warning(f"Weak phrasing found: {', '.join(result['verbs']['weak_phrases_found'])}")
    st.caption(f"Strong action verbs used: {result['verbs']['strong_verb_count']}")

    # --- suggestions ---
    st.subheader("Suggestions")
    for s in result["suggestions"]:
        st.markdown(f"- {s}")

    # --- cover letter ---
    st.divider()
    st.subheader("Cover Letter Generator")
    cl1, cl2 = st.columns(2)
    company_name = cl1.text_input("Company name (optional)")
    tone = cl2.selectbox("Tone", ["professional", "enthusiastic", "formal", "concise"])
    if st.button("Generate cover letter"):
        with st.spinner("Writing..."):
            letter = generate_cover_letter(
                st.session_state["resume_text"], st.session_state["jd_text"],
                company_name=company_name, tone=tone,
            )
        st.markdown(letter)
        st.download_button("Download cover letter (.txt)", letter, file_name="cover_letter.txt")

# --- past analyses ---
past = get_history(user_id, MODULE_NAME)
if past:
    with st.expander(f"Past analyses ({len(past) // 2})"):
        for msg in past:
            st.caption(f"{msg['created_at']} — {msg['content']}")