import sqlite3
import threading
import time
from datetime import datetime

from config import DB_FILE
from speak import speak

DB_NAME = str(DB_FILE)


# ==========================
# DATABASE SETUP
# ==========================

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        reminder_date TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# ==========================
# ADD REMINDER
# ==========================

def add_reminder(title, reminder_date, reminder_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reminders(title, reminder_date, reminder_time)
        VALUES (?, ?, ?)
    """, (title, reminder_date, reminder_time))

    conn.commit()
    conn.close()

    print(f"Reminder Added: {title}")


# ==========================
# SHOW ALL REMINDERS
# ==========================

def get_all_reminders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reminders
        ORDER BY reminder_date, reminder_time
    """)

    reminders = cursor.fetchall()

    conn.close()

    return reminders


# ==========================
# TODAY'S REMINDERS
# ==========================

def get_today_reminders():

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reminders
        WHERE reminder_date=? AND completed=0
        ORDER BY reminder_time
    """, (today,))

    reminders = cursor.fetchall()

    conn.close()

    return reminders


# ==========================
# DELETE REMINDER
# ==========================

def delete_reminder(reminder_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM reminders
        WHERE id=?
    """, (reminder_id,))

    conn.commit()
    conn.close()

    print("Reminder Deleted.")


# ==========================
# CHECK REMINDERS
# ==========================

def check_reminders():

    print("Reminder Service Started.")

    while True:

        now = datetime.now()

        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM reminders
            WHERE reminder_date=?
            AND reminder_time=?
            AND completed=0
        """, (current_date, current_time))

        reminders = cursor.fetchall()

        for reminder in reminders:

            print("Reminder Triggered:", reminder)

            speak(f"Reminder. {reminder[1]}")

            cursor.execute("""
                UPDATE reminders
                SET completed=1
                WHERE id=?
            """, (reminder[0],))

            conn.commit()

        conn.close()

        time.sleep(30)


# ==========================
# START SERVICE
# ==========================

def start_reminder_service():

    thread = threading.Thread(
        target=check_reminders,
        daemon=True
    )

    thread.start()


# ==========================
# INITIALIZE DATABASE
# ==========================

initialize_database()