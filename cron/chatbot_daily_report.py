#!/usr/bin/env python3
"""Generate the daily chatbot monitoring report from PostgreSQL."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import psycopg2

from chatbot_sync import get_pg_dsn, sync


REPORT_EMAIL = os.environ.get("REPORT_EMAIL", "pocharlies@gmail.com")
GRAFANA_URL = os.environ.get("GRAFANA_URL", "https://monitor.e-dani.com")


def mask_email(email: str | None) -> str:
    if not email or "@" not in email:
        return "unknown"
    return email[:3] + "***" + email[email.index("@") :]


def generate_report() -> dict:
    conn = psycopg2.connect(get_pg_dsn())
    cur = conn.cursor()

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    cur.execute("SELECT COUNT(*) FROM chatbot_sessions WHERE created_at::date = %s", (yesterday,))
    sessions_yesterday = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM chatbot_messages WHERE created_at::date = %s", (yesterday,))
    messages_yesterday = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(DISTINCT customer_email) FROM chatbot_sessions WHERE created_at::date = %s",
        (yesterday,),
    )
    unique_users_yesterday = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM chatbot_messages WHERE created_at::date = %s AND role = 'user'",
        (yesterday,),
    )
    user_messages = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*) FROM chatbot_messages
        WHERE created_at::date = %s AND tool_calls IS NOT NULL AND tool_calls != ''
        """,
        (yesterday,),
    )
    tool_call_messages = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM chatbot_sessions")
    total_sessions = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT customer_email) FROM chatbot_sessions")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM chatbot_messages")
    total_messages = cur.fetchone()[0]

    cur.execute(
        """
        SELECT s.customer_email, COUNT(m.id) as msg_count
        FROM chatbot_sessions s
        JOIN chatbot_messages m ON m.session_id = s.id
        WHERE m.created_at::date = %s
        GROUP BY s.customer_email
        ORDER BY msg_count DESC
        LIMIT 5
        """,
        (yesterday,),
    )
    top_users = cur.fetchall()

    cur.execute(
        """
        SELECT s.customer_email, s.title, s.message_count, s.created_at
        FROM chatbot_sessions s
        WHERE s.created_at::date = %s AND s.message_count > 0
        ORDER BY s.created_at DESC
        LIMIT 10
        """,
        (yesterday,),
    )
    recent_sessions = cur.fetchall()

    cur.execute(
        """
        SELECT created_at::date as day, COUNT(*) as sessions, COUNT(DISTINCT customer_email) as users
        FROM chatbot_sessions
        WHERE created_at > NOW() - INTERVAL '7 days'
        GROUP BY created_at::date
        ORDER BY day
        """
    )
    weekly_trend = cur.fetchall()

    conn.close()

    html = f"""
    <html>
    <body>
      <h1>Skirmshop Chatbot Report - {yesterday}</h1>
      <p>Sessions: {sessions_yesterday}</p>
      <p>Unique users: {unique_users_yesterday}</p>
      <p>Messages: {messages_yesterday}</p>
      <p>User messages: {user_messages}</p>
      <p>Bot responses: {messages_yesterday - user_messages}</p>
      <p>Tool-call responses: {tool_call_messages}</p>
      <p>Total sessions: {total_sessions}</p>
      <p>Total unique users: {total_users}</p>
      <p>Total messages: {total_messages}</p>
      <p><a href="{GRAFANA_URL}">View full dashboard on Grafana</a></p>
    </body>
    </html>
    """

    return {
        "subject": f"Chatbot Report {yesterday}: {sessions_yesterday} sessions, {unique_users_yesterday} users",
        "html": html,
        "stats": {
            "date": str(yesterday),
            "sessions": sessions_yesterday,
            "users": unique_users_yesterday,
            "messages": messages_yesterday,
            "user_messages": user_messages,
            "tool_call_messages": tool_call_messages,
            "total_sessions": total_sessions,
            "total_users": total_users,
            "total_messages": total_messages,
            "top_users": [{"email": mask_email(email), "messages": count} for email, count in top_users],
            "recent_sessions": [
                {
                    "email": mask_email(email),
                    "title": (title or "New Chat")[:80],
                    "messages": count,
                    "created_at": created.isoformat() if hasattr(created, "isoformat") else str(created),
                }
                for email, title, count, created in recent_sessions
            ],
            "weekly_trend": [
                {"date": str(day), "sessions": sessions, "users": users}
                for day, sessions, users in weekly_trend
            ],
        },
    }


def main() -> int:
    if "--no-sync" not in sys.argv:
        sync_result = sync(full_resync=False)
        print(json.dumps({"sync": sync_result}, sort_keys=True))

    report = generate_report()
    report_dir = os.environ.get("REPORT_DIR", "/tmp")
    os.makedirs(report_dir, exist_ok=True)
    html_path = os.path.join(report_dir, "chatbot-daily-report.html")
    json_path = os.path.join(report_dir, "chatbot-daily-report.json")

    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(report["html"])
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report["stats"], fh, indent=2, sort_keys=True)

    print(f"Report generated for {REPORT_EMAIL}: {report['subject']}")
    print(f"HTML saved to: {html_path}")
    print(f"JSON saved to: {json_path}")
    print(json.dumps(report["stats"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
