import sqlite3

from config import DB_FILE


DB_NAME = str(DB_FILE)

def ensure_tables():
    """Create the chat table on a fresh install (no database yet)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            message TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit=10):
    ensure_tables()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, message FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows[::-1]