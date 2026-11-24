import os
import sqlite3
import json
from datetime import datetime, timezone

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")


def get_db_path():
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "", 1)
        return path
    return "./app.db"


DB_PATH = get_db_path()


def get_connection():
    if DB_PATH.startswith("/"):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_session_id
        ON messages(session_id)
    """)

    conn.commit()
    conn.close()


def save_message(session_id, role, content, metadata=None):
    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO messages
        (session_id, role, content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_id,
        role,
        content,
        json.dumps(metadata) if metadata is not None else None,
        created_at
    ))

    conn.commit()
    conn.close()


def get_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, metadata, created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def session_exists(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM messages
        WHERE session_id = ?
        LIMIT 1
    """, (session_id,))

    result = cursor.fetchone()
    conn.close()

    return result is not None


# =========================================================
# CHAT HISTORY
# =========================================================

def get_all_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            session_id,
            MAX(created_at) AS last_activity,
            (
                SELECT content
                FROM messages AS first_message
                WHERE first_message.session_id = grouped.session_id
                  AND first_message.role = 'user'
                ORDER BY first_message.id ASC
                LIMIT 1
            ) AS title
        FROM messages AS grouped
        GROUP BY session_id
        ORDER BY last_activity DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    sessions = []

    for session_id, last_activity, title in rows:
        sessions.append({
            "session_id": session_id,
            "title": title or "New Chat",
            "last_activity": last_activity
        })

    return sessions


def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE session_id = ?
    """, (session_id,))

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count > 0
