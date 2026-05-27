#!/usr/bin/env python3
"""Sync the live chatbot SQLite database into the monitoring PostgreSQL tables."""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone

import psycopg2


SQLITE_PATH = os.environ.get("SQLITE_PATH", "/app/prisma/data/chatbot.db")


def epoch_ms_to_iso(value):
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).isoformat()
        return value
    except (OSError, ValueError):
        return datetime.now(timezone.utc).isoformat()


def get_pg_dsn() -> str:
    dsn = os.environ.get("PG_DSN")
    if not dsn:
        raise RuntimeError("PG_DSN is not set")
    return dsn


def connect_sqlite() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{SQLITE_PATH}?mode=ro", uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def sync(full_resync: bool = False) -> dict[str, int]:
    sqlite_conn = connect_sqlite()
    pg_conn = psycopg2.connect(get_pg_dsn())
    pg_conn.autocommit = False

    try:
        pg_cur = pg_conn.cursor()

        if full_resync:
            watermark_ms = 0
        else:
            pg_cur.execute("SELECT value FROM chatbot_sync_state WHERE key='last_sync'")
            row = pg_cur.fetchone()
            watermark_ms = int(row[0]) if row and str(row[0]).isdigit() else 0

        now = datetime.now(timezone.utc).isoformat()
        now_ms = str(int(datetime.now(timezone.utc).timestamp() * 1000))

        sessions = sqlite_conn.execute(
            """
            SELECT id, customerEmail, title, createdAt, updatedAt
            FROM Session
            WHERE updatedAt > ?
            ORDER BY updatedAt
            """,
            (watermark_ms,),
        ).fetchall()

        session_count = 0
        for session in sessions:
            message_count = sqlite_conn.execute(
                "SELECT COUNT(*) FROM Message WHERE sessionId = ?",
                (session["id"],),
            ).fetchone()[0]

            pg_cur.execute(
                """
                INSERT INTO chatbot_sessions
                  (id, customer_email, title, message_count, created_at, updated_at, last_synced_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  title = EXCLUDED.title,
                  message_count = EXCLUDED.message_count,
                  updated_at = EXCLUDED.updated_at,
                  last_synced_at = EXCLUDED.last_synced_at
                """,
                (
                    session["id"],
                    session["customerEmail"],
                    session["title"],
                    message_count,
                    epoch_ms_to_iso(session["createdAt"]),
                    epoch_ms_to_iso(session["updatedAt"]),
                    now,
                ),
            )
            session_count += 1

        messages = sqlite_conn.execute(
            """
            SELECT id, sessionId, role, content, toolCalls, createdAt
            FROM Message
            WHERE createdAt > ?
            ORDER BY createdAt
            """,
            (watermark_ms,),
        ).fetchall()

        message_count = 0
        for message in messages:
            content = message["content"] or ""
            pg_cur.execute(
                """
                INSERT INTO chatbot_messages
                  (id, session_id, role, content, tool_calls, content_length, created_at, last_synced_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  content = EXCLUDED.content,
                  tool_calls = EXCLUDED.tool_calls,
                  content_length = EXCLUDED.content_length,
                  last_synced_at = EXCLUDED.last_synced_at
                """,
                (
                    message["id"],
                    message["sessionId"],
                    message["role"],
                    content,
                    message["toolCalls"],
                    len(content),
                    epoch_ms_to_iso(message["createdAt"]),
                    now,
                ),
            )
            message_count += 1

        pg_cur.execute(
            """
            INSERT INTO chatbot_sync_state (key, value, updated_at)
            VALUES ('last_sync', %s, %s)
            ON CONFLICT (key) DO UPDATE SET
              value = EXCLUDED.value,
              updated_at = EXCLUDED.updated_at
            """,
            (now_ms, now),
        )

        pg_conn.commit()
        return {"sessions": session_count, "messages": message_count, "watermark_ms": watermark_ms}
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


def main() -> int:
    full_resync = "--full" in sys.argv
    result = sync(full_resync=full_resync)
    mode = "full" if full_resync else "incremental"
    print(
        "Chatbot sync completed "
        f"mode={mode} sessions={result['sessions']} messages={result['messages']} "
        f"watermark_ms={result['watermark_ms']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
