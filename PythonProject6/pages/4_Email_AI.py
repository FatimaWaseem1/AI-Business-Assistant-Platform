"""
pages/4_Email_AI.py

Three sub-features from the Task 7 brief, each a tab using the shared
run_prompt_tab() helper — no new core/ logic needed, just system prompts.
"""

import streamlit as st
from core.auth import require_login
from core.prompt_module import run_prompt_tab

MODULE_NAME = "email_ai"

require_login()
user_id = st.session_state["user_id"]

st.title("Email AI")

tab_draft, tab_reply, tab_grammar = st.tabs(["Draft Email", "Reply Suggestions", "Grammar Correction"])

with tab_draft:
    st.caption("Describe what the email needs to say — I'll write the full email.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="draft",
        system_prompt=(
            "You are a professional email writer. Write a complete, ready-to-send email "
            "based on the user's brief. Include a subject line. Match a professional but "
            "warm tone unless the user specifies otherwise. Keep it concise — no filler."
        ),
        user_id=user_id,
        input_label="What's the email about?",
        placeholder="e.g. Email my manager asking to move Thursday's 1:1 to Friday afternoon due to a clash.",
    )

with tab_reply:
    st.caption("Paste an email you've received — I'll suggest a few reply options.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="reply_suggestions",
        system_prompt=(
            "You are an email assistant. Given the incoming email below, write 3 short reply "
            "options that differ in approach (e.g. accept/decline/ask for more info, or "
            "formal/casual). Label each option clearly and keep each under 80 words."
        ),
        user_id=user_id,
        input_label="Paste the incoming email",
        placeholder="Paste the full email you need to reply to...",
        button_label="Suggest replies",
        height=200,
    )

with tab_grammar:
    st.caption("Paste a draft — I'll correct grammar, spelling, and clarity issues.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="grammar_correction",
        system_prompt=(
            "You are a professional proofreader. Correct grammar, spelling, punctuation, and "
            "clarity issues in the email below, preserving the original meaning and tone. "
            "First show the corrected version in full, then a short bullet list of what you changed."
        ),
        user_id=user_id,
        input_label="Paste your email draft",
        placeholder="Paste the email text you want proofread...",
        button_label="Correct",
        height=200,
    )