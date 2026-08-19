"""
core/auth.py

Thin Streamlit wrapper around core.database's auth functions.
Every page starts with: from core.auth import require_login; require_login()
"""

import streamlit as st
from core import database as db


def _login_form():
    st.subheader("Log in")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        user_id = db.verify_user(username, password)
        if user_id:
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password.")


def _signup_form():
    st.subheader("Create an account")
    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Sign up")
    if submitted:
        if password != confirm:
            st.error("Passwords don't match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            ok, msg = db.create_user(username, password)
            if ok:
                st.success(msg + " You can log in now.")
            else:
                st.error(msg)


def auth_gate():
    """Renders login/signup tabs. Call this at the top of app.py."""
    st.title("Axorvian AI Business Assistant")
    tab1, tab2 = st.tabs(["Log in", "Sign up"])
    with tab1:
        _login_form()
    with tab2:
        _signup_form()


def require_login():
    """Call at the top of every page in pages/. Stops the page if not logged in."""
    if "user_id" not in st.session_state:
        st.warning("Please log in from the home page first.")
        st.stop()


def logout_button():
    if st.sidebar.button("Log out"):
        for key in ("user_id", "username"):
            st.session_state.pop(key, None)
        st.rerun()