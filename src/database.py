import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "mood.db"


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(_connect()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                emotion TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                mood_score REAL NOT NULL
            )
        """)


def log_mood(emotion, sentiment, mood_score):
    """Save one check-in. Only the emotion data is stored, never the message."""
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO mood_log (timestamp, emotion, sentiment, mood_score) "
            "VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), emotion, sentiment, mood_score),
        )


def get_moods():
    with closing(_connect()) as conn:
        return conn.execute(
            "SELECT timestamp, emotion, sentiment, mood_score FROM mood_log ORDER BY timestamp"
        ).fetchall()


def clear_moods():
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM mood_log")


if __name__ == "__main__":
    init_db()
    print("Database ready. Saved check-ins:", len(get_moods()))