"""PostgreSQL storage layer for meetings (transcript, summary, decisions, action items)."""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import config


def get_connection():
    return psycopg2.connect(config.DATABASE_URL)


def init_db() -> None:
    """Create the meetings table if it doesn't exist. Safe to call on every startup."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            transcript TEXT,
            summary TEXT,
            decisions JSONB,
            action_items JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_meeting(filename, transcript, summary, decisions=None, action_items=None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO meetings (filename, transcript, summary, decisions, action_items)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (filename, transcript, summary, json.dumps(decisions or []), json.dumps(action_items or [])),
    )
    meeting_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return meeting_id


def get_all_meetings() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM meetings ORDER BY created_at DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_meeting(meeting_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM meetings WHERE id = %s;", (meeting_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def delete_meeting(meeting_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM meetings WHERE id = %s;", (meeting_id,))
    conn.commit()
    cur.close()
    conn.close()


def search_meetings(keyword: str) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT * FROM meetings
        WHERE transcript ILIKE %s OR summary ILIKE %s
        ORDER BY created_at DESC;
        """,
        (f"%{keyword}%", f"%{keyword}%"),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows