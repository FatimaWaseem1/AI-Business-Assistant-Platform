"""
core/prompt_module.py

Shared UI + logic for every module that's just "text in -> LLM -> text out"
with no retrieval step: Email AI, Content AI, Coding AI. Rather than
triplicate the same text_area -> button -> stream -> save pattern three
times, each of those modules' tabs calls run_prompt_tab() with just a
system prompt and some labels.
"""

import streamlit as st
from core.database import save_message
from core.llm_wrapper import LLMWrapper


def run_prompt_tab(module_name: str, sub_feature: str, system_prompt: str, user_id: int,
                    input_label: str, placeholder: str = "", button_label: str = "Generate",
                    height: int = 160, output_language: str | None = None,
                    prompt_prefix: str = ""):
    """Renders one tab: input box -> generate button -> output -> saved to history.

    prompt_prefix: extra context prepended to the prompt but not shown in the
    input box itself (e.g. "Platform: Instagram" or "Language: Python") —
    used when a tab needs a selectbox alongside the free-text input.

    output_language: if set (e.g. "python"), renders output as a code block
    instead of markdown, and skips streaming (cleaner for a single code block
    than watching it stream token-by-token).
    """
    key_base = f"{module_name}_{sub_feature}"
    user_input = st.text_area(input_label, placeholder=placeholder, height=height, key=f"{key_base}_input")

    if st.button(button_label, key=f"{key_base}_btn", disabled=not user_input):
        llm = LLMWrapper(provider="gemini")
        full_prompt = f"{prompt_prefix}\n\n{user_input}" if prompt_prefix else user_input

        with st.spinner("Working on it..."):
            if output_language:
                full_output = llm.generate(full_prompt, system=system_prompt)
                st.code(full_output, language=output_language)
            else:
                full_output = st.write_stream(llm.generate_stream(full_prompt, system=system_prompt))

        save_message(user_id, module_name, "user", f"[{sub_feature}] {full_prompt}")
        save_message(user_id, module_name, "assistant", full_output)