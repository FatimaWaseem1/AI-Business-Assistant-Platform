"""
core/database.py

Single SQLite file backing the whole platform:
- users            -> auth
- chat_history      -> persistent, per-module, per-user conversation log
- prompt_library     -> saved/reusable prompt templates

Every other module (Email AI, Content AI, etc.) reuses these same three
tables instead of inventing its own storage, so "module" is just a string
column (e.g. "ai_chat", "document_ai", "email_ai") that tags each row.
"""

import sqlite3
import hashlib
import hmac
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "platform.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Call once at app startup. Safe to call every run (IF NOT EXISTS)."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                role TEXT NOT NULL,          -- 'user' or 'assistant'
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS prompt_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                name TEXT NOT NULL,
                template TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )


# ---------- auth helpers ----------

def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def create_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    salt = os.urandom(16).hex()
    pw_hash = _hash_password(password, salt)
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, pw_hash, salt),
            )
        return True, "Account created."
    except sqlite3.IntegrityError:
        return False, "Username already taken."


def verify_user(username: str, password: str) -> int | None:
    """Returns user_id on success, None on failure."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, password_hash, salt FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        return None
    candidate = _hash_password(password, row["salt"])
    if hmac.compare_digest(candidate, row["password_hash"]):
        return row["id"]
    return None


# ---------- chat history ----------

def save_message(user_id: int, module: str, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_history (user_id, module, role, content) VALUES (?, ?, ?, ?)",
            (user_id, module, role, content),
        )


def get_history(user_id: int, module: str, limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT role, content, created_at FROM chat_history
               WHERE user_id = ? AND module = ?
               ORDER BY id ASC LIMIT ?""",
            (user_id, module, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def clear_history(user_id: int, module: str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM chat_history WHERE user_id = ? AND module = ?", (user_id, module)
        )


# ---------- prompt library ----------

def save_prompt(user_id: int, module: str, name: str, template: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO prompt_library (user_id, module, name, template) VALUES (?, ?, ?, ?)",
            (user_id, module, name, template),
        )

def get_prompts(user_id: int, module: str | None = None) -> list[dict]:
    with get_conn() as conn:
        if module:
            rows = conn.execute(
                "SELECT * FROM prompt_library WHERE user_id = ? AND module = ? ORDER BY id DESC",
                (user_id, module),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM prompt_library WHERE user_id = ? ORDER BY id DESC", (user_id,)
            ).fetchall()
    return [dict(r) for r in rows]