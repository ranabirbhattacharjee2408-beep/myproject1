import sqlite3

DB_NAME = "jarvis_memory.db"

def get_recent_messages(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, message FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows[::-1]