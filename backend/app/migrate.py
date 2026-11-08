"""Мини-мигратор: применяет SQL-файлы из backend/migrations.

Файлы применяются по порядку имени, каждый ровно один раз.
"""

from pathlib import Path

from app.db import get_conn

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def migrate() -> list[str]:
    applied_now = []
    with get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " name TEXT PRIMARY KEY,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        done = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in done:
                continue
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,))
            applied_now.append(path.name)
    return applied_now
