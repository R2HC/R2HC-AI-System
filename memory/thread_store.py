import sqlite3, json, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

DB_PATH = Path(__file__).parent.parent / "threads" / "threads.db"
MAX_TOKENS_BEFORE_SUMMARY = 4000
SUMMARIZE_TARGET_TOKENS = 800

def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with _get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                token_count INTEGER DEFAULT 0,
                metadata TEXT DEFAULT "{}"
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                token_count INTEGER DEFAULT 0,
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            );
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                messages_compressed INTEGER NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            );
            CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
            CREATE INDEX IF NOT EXISTS idx_threads_updated ON threads(updated_at DESC);
        """)
    print(f"[ThreadStore] DB initialized at {DB_PATH}")

def create_thread(thread_id=None, title=None):
    import uuid
    tid = thread_id or str(uuid.uuid4())[:8]
    now = time.time()
    with _get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO threads (id, title, created_at, updated_at) VALUES (?,?,?,?)",
            (tid, title or f"Thread {tid}", now, now)
        )
    return tid

def add_message(thread_id, role, content, token_count=0):
    now = time.time()
    if not token_count:
        token_count = max(1, len(content) // 4)
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO messages (thread_id, role, content, timestamp, token_count) VALUES (?,?,?,?,?)",
            (thread_id, role, content, now, token_count)
        )
        conn.execute(
            "UPDATE threads SET updated_at=?, token_count=token_count+? WHERE id=?",
            (now, token_count, thread_id)
        )

def get_thread_messages(thread_id, limit=50):
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE thread_id=? ORDER BY timestamp DESC LIMIT ?",
            (thread_id, limit)
        ).fetchall()
    return list(reversed([dict(r) for r in rows]))

def get_thread_summary(thread_id):
    with _get_db() as conn:
        row = conn.execute(
            "SELECT summary FROM summaries WHERE thread_id=? ORDER BY created_at DESC LIMIT 1",
            (thread_id,)
        ).fetchone()
    return row["summary"] if row else None

def store_summary(thread_id, summary, messages_compressed):
    now = time.time()
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO summaries (thread_id, summary, messages_compressed, created_at) VALUES (?,?,?,?)",
            (thread_id, summary, messages_compressed, now)
        )
        conn.execute(
            "DELETE FROM messages WHERE thread_id=? AND id NOT IN (SELECT id FROM messages WHERE thread_id=? ORDER BY timestamp DESC LIMIT 10)",
            (thread_id, thread_id)
        )
        conn.execute("UPDATE threads SET token_count=? WHERE id=?", (SUMMARIZE_TARGET_TOKENS, thread_id))

def get_thread_token_count(thread_id):
    with _get_db() as conn:
        row = conn.execute("SELECT token_count FROM threads WHERE id=?", (thread_id,)).fetchone()
    return row["token_count"] if row else 0

def list_threads(limit=20):
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at, token_count FROM threads ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

def needs_summarization(thread_id):
    return get_thread_token_count(thread_id) >= MAX_TOKENS_BEFORE_SUMMARY

init_db()