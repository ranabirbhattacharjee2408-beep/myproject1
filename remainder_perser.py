import dateparser
from datetime import datetime

from Reminder_Database import add_reminder
from speak import speak


def create_reminder(command):
    command = command.lower().replace("remind me to", "").strip()

    if " at " not in command:
        speak("Please tell me the time.")
        return

    task, time_text = command.rsplit(" at ", 1)

    reminder_datetime = dateparser.parse(time_text)

    if reminder_datetime is None:
        speak("I couldn't understand the reminder time.")
        return

    add_reminder(
        task,
        reminder_datetime.strftime("%Y-%m-%d"),
        reminder_datetime.strftime("%H:%M")
    )

    speak(f"Reminder added for {task}.")