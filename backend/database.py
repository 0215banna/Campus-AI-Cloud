import sqlite3
from datetime import datetime

from config import DATABASE_PATH, DATA_DIRECTORY, MODEL_NAME


def initialize_database() -> None:
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_history(question: str, answer: str) -> None:
    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO chat_history (
                question,
                answer,
                model,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                question,
                answer,
                MODEL_NAME,
                created_at,
            ),
        )
        connection.commit()


def get_history(limit: int = 20) -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                question,
                answer,
                model,
                created_at
            FROM chat_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def count_history() -> int:
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM chat_history"
        ).fetchone()

    return int(row[0])