"""SQLite: suhbatlar tarixi va statistika."""

import sqlite3
from contextlib import closing
from datetime import datetime

from src.config import DB_PATH


def _connect() -> sqlite3.Connection:
    """`with closing(_connect()) as conn, conn:` bilan ishlatiladi —
    closing() ulanishni yopadi, ichki `conn` konteksti tranzaksiyani commit qiladi."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Jadvallarni yaratadi (agar mavjud bo'lmasa) va eski bazani yangilaydi."""
    with closing(_connect()) as conn, conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario TEXT NOT NULL,
                level TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'en',
                created_at TEXT NOT NULL
            )"""
        )
        # Migratsiya: til ustuni bo'lmagan eski bazalarga qo'shamiz
        columns = [row[1] for row in conn.execute("PRAGMA table_info(conversations)")]
        if "language" not in columns:
            conn.execute(
                "ALTER TABLE conversations ADD COLUMN language TEXT NOT NULL DEFAULT 'en'"
            )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                corrected TEXT DEFAULT '',
                explanation TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )"""
        )


def create_conversation(scenario: str, level: str, language: str = "en") -> int:
    with closing(_connect()) as conn, conn:
        cur = conn.execute(
            """INSERT INTO conversations (scenario, level, language, created_at)
               VALUES (?, ?, ?, ?)""",
            (scenario, level, language, datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid


def save_message(
    conversation_id: int,
    role: str,
    content: str,
    corrected: str = "",
    explanation: str = "",
) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            """INSERT INTO messages
               (conversation_id, role, content, corrected, explanation, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                conversation_id,
                role,
                content,
                corrected,
                explanation,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def get_stats() -> dict:
    """Umumiy statistika: suhbatlar, gaplar, xatolar soni."""
    with closing(_connect()) as conn, conn:
        conversations = conn.execute(
            "SELECT COUNT(*) FROM conversations"
        ).fetchone()[0]
        user_messages = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE role = 'user'"
        ).fetchone()[0]
        mistakes = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE role = 'user' AND corrected != ''"
        ).fetchone()[0]
    correct = user_messages - mistakes
    accuracy = round(correct / user_messages * 100) if user_messages else 0
    return {
        "conversations": conversations,
        "user_messages": user_messages,
        "mistakes": mistakes,
        "accuracy": accuracy,
    }


def get_recent_mistakes(limit: int = 20) -> list[dict]:
    """Oxirgi xatolar ro'yxati (yangi birinchi)."""
    with closing(_connect()) as conn, conn:
        rows = conn.execute(
            """SELECT m.content, m.corrected, m.explanation, m.created_at,
                      c.scenario, c.language
               FROM messages m
               JOIN conversations c ON c.id = m.conversation_id
               WHERE m.role = 'user' AND m.corrected != ''
               ORDER BY m.id DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
