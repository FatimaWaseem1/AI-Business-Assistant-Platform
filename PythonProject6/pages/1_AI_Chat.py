"""
pages/1_AI_Chat.py

This is the template every other module (Email AI, Content AI, Coding AI...)
should copy: require_login -> load history -> render chat -> stream reply
-> save both sides to DB. Once this works, cloning it for the next module
is a ~10 minute job (just change MODULE_NAME and the system prompt).
"""

import streamlit as st
from core.auth import require_login
from core.database import save_message, get_history
from core.llm_wrapper import LLMWrapper

MODULE_NAME = "ai_chat"
SYSTEM_PROMPT = "You are a helpful, concise general-purpose assistant."

require_login()
user_id = st.session_state["user_id"]

st.title("AI Chat")

llm = LLMWrapper(provider="gemini")

# render existing history
for msg in get_history(user_id, MODULE_NAME):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# new message
if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message(user_id, MODULE_NAME, "user", prompt)

    with st.chat_message("assistant"):
        full_reply = st.write_stream(llm.generate_stream(prompt, system=SYSTEM_PROMPT))
    save_message(user_id, MODULE_NAME, "assistant", full_reply)