"""
app.py

Entry point. `streamlit run app.py`

Streamlit auto-detects every .py file in pages/ and adds it to the
sidebar nav, in filename order — that's why pages are numbered
(1_AI_Chat.py, 2_Document_AI.py, ...). This file only handles:
  1. DB init
  2. Login / signup gate
  3. A small landing dashboard once logged in
"""

import streamlit as st
from core.database import init_db
from core.auth import auth_gate, logout_button

st.set_page_config(page_title="Axorvian AI Assistant", page_icon="🧠", layout="wide")

init_db()

if "user_id" not in st.session_state:
    auth_gate()
    st.stop()

# --- logged in: landing dashboard ---
logout_button()
st.title(f"Welcome back, {st.session_state['username']}")
st.write("Pick a module from the sidebar to get started.")

st.markdown(
    """
    | Module | Status |
    |---|---|
    | AI Chat | Available |
    | Document AI | Coming next |
    | Resume AI | Coming next |
    | Email / Meeting / Content / Coding AI | Coming next |
    """
)