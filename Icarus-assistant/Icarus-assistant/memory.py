import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "data" / "icarus.db"


class ConversationMemory:
    def __init__(self):
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        with closing(sqlite3.connect(DATABASE_PATH)) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)

    def load_recent(self, limit=20):
        with closing(sqlite3.connect(DATABASE_PATH)) as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {"role": role, "content": content}
            for role, content in reversed(rows)
        ]

    def save_exchange(self, user_message, assistant_message):
        # Save both messages together so incomplete exchanges are not stored.
        with closing(sqlite3.connect(DATABASE_PATH)) as connection:
            with connection:
                connection.executemany(
                    "INSERT INTO messages (role, content) VALUES (?, ?)",
                    [
                        ("user", user_message),
                        ("assistant", assistant_message),
                    ],
                )

    def clear(self):
        with closing(sqlite3.connect(DATABASE_PATH)) as connection:
            with connection:
                connection.execute("DELETE FROM messages")