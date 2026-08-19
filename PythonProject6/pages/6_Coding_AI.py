"""
pages/6_Coding_AI.py

Same shared-helper pattern. Code Generation is the one tab that sets
output_language, so its output renders as a proper code block instead of
markdown prose — Explanation and Bug Detection stay as markdown since
their output is a mix of prose and inline code.
"""

import streamlit as st
from core.auth import require_login
from core.prompt_module import run_prompt_tab

MODULE_NAME = "coding_ai"

require_login()
user_id = st.session_state["user_id"]

st.title("Coding AI")

tab_explain, tab_bugs, tab_generate = st.tabs(["Code Explanation", "Bug Detection", "Code Generation"])

with tab_explain:
    st.caption("Paste a code snippet — I'll explain what it does in plain language.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="explain",
        system_prompt=(
            "You are a patient programming tutor. Explain the given code snippet in plain, "
            "beginner-friendly language. Break it down section by section, explain what each "
            "part does and why, and summarize the overall purpose at the end."
        ),
        user_id=user_id,
        input_label="Paste your code",
        placeholder="Paste a function, class, or code block here...",
        button_label="Explain",
        height=220,
    )

with tab_bugs:
    st.caption("Paste code to review — I'll flag likely bugs and explain fixes.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="bug_detection",
        system_prompt=(
            "You are a careful code reviewer. Identify likely bugs, edge cases, and issues in "
            "the code below (logic errors, off-by-one errors, unhandled exceptions, type "
            "mismatches, etc). For each issue: quote the relevant line, explain the problem, "
            "and suggest a fix. If the code looks correct, say so plainly."
        ),
        user_id=user_id,
        input_label="Paste code to review",
        placeholder="Paste the code you want checked for bugs...",
        button_label="Check for bugs",
        height=220,
    )

LANGUAGE_TO_HIGHLIGHT_ID = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "java",
    "C++": "cpp",
    "SQL": "sql",
    "HTML/CSS": "html",
}

with tab_generate:
    st.caption("Describe what the code should do — I'll generate it.")
    language = st.selectbox("Language", list(LANGUAGE_TO_HIGHLIGHT_ID.keys()))
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="generate",
        system_prompt=(
            "You are an expert software engineer. Generate clean, working, well-commented code "
            "in the specified language that fulfills the user's requirements exactly. Output "
            "ONLY the code — no explanation before or after, no markdown fences."
        ),
        user_id=user_id,
        input_label="Describe what the code should do",
        placeholder="e.g. A function that takes a list of prices and returns the total after a given discount percentage",
        button_label="Generate code",
        height=140,
        output_language=LANGUAGE_TO_HIGHLIGHT_ID[language],
        prompt_prefix=f"Language: {language}",
    )