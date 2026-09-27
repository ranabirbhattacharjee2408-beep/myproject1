


import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import traceback
import logging
import email
import shutil
import sys
from datetime import datetime, timedelta
import  pywhatkit
import urllib
import tkinter as tk
import threading
import time
import traceback

tk_root = None
writing_window = None
try:
    from memory import get_recent_messages
    from writing_mode import WritingMode
except Exception:
    # Fallback: try relative import (if package) or provide a stub to avoid import errors
    try:
        from .jarvis_memory import get_recent_messages  # type: ignore
    except Exception:
        def get_recent_messages(count=10):
            """Fallback stub used when jarvis_memory is unavailable."""
            return []
from browsersearch import search_web

import requests
import os
import time
import customtkinter as ctk
writing_window = None

def find_es_path():
    path = shutil.which("es") or shutil.which("everything")
    if path:
        return path

    candidates = [
        r"C:\Program Files\Everything\Everything.exe",
        r"C:\Program Files (x86)\Everything\Everything.exe",
        r"C:\Program Files\Voidtools\Everything.exe",
        r"C:\Program Files (x86)\Voidtools\Everything.exe"
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return None


ES_PATH = find_es_path()
from tkinter import StringVar
import threading
try:
    import winshell
except ImportError:
    winshell = None
from abc import ABC, abstractmethod
from deep_translator import GoogleTranslator
from app_louncher import open_app
from remainder_perser import create_reminder
from system_commands import system_command
from calendar_manager import add_event, get_today_events
from email_assistant import GeminiEmail, create_email, takeCommand
from calendar_ai import parse_calendar_command
from calendar_manager import add_event
from logger import log_info, log_warning, log_error
from speak import stop_speaking
from audio.microphone import listen
from config import DB_FILE, GEMINI_API_KEY
from conversation_mode import start_conversational


def open_path(path):
    """Open a file or folder with the user's native application."""
    if hasattr(os, "startfile"):
        os.startfile(path)
        return

    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.Popen([opener, path])

pending_files = []

conversation_mode = None
waiting_for_confirmation = False
pending_action = None
pending_app = None
email_draft = None
email_mode = False


class ConversationModeBase(ABC):
    @abstractmethod
    def activate(self):
        raise NotImplementedError

    @abstractmethod
    def deactivate(self):
        raise NotImplementedError

    @abstractmethod
    def process(self, command):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError


class conversation_mode(ConversationModeBase):
    def __init__(self):
        self.active = False
        self.history_limit = 20
        self.history = get_recent_messages(self.history_limit)

    def activate(self):
        if not self.active:
            self.active = True
            save_message("system", "Conversation mode activated.")
        return self.active

    def deactivate(self):
        if self.active:
            self.active = False
            save_message("system", "Conversation mode deactivated.")
        return self.active

    def process(self, command):
        if not isinstance(command, str) or not command.strip():
            return

        command = translate_to_english(command)

        if "close conversation mode" in command.lower():
            self.deactivate()
            speak("Conversation mode deactivated. Going to standby mode.")
            return

        save_message("user", command)

        response = aicommand(command)

        if response:
            save_message("assistant", response)

        print(response)
        speak(response)
        return response

    def start(self):
        if self.active:
            speak("Conversation mode is already active.")
            return

        self.activate()
        speak("Conversation mode activated. You can now chat with me.")

        while self.active:
            try:
                command = listen(timeout=8, phrase_time_limit=8)

                if command is None:
                    continue

                command = command.strip()
                if not command:
                    continue

                if "close conversation mode" in command.lower():
                    self.deactivate()
                    speak("Conversation mode deactivated. Going to standby mode.")
                    break

                self.process(command)

            except Exception as e:
                print("Conversation mode listen error:", e)
                time.sleep(0.5)


conversation_mode = conversation_mode()


def start_conversational():
    conversation_mode.start()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


from Reminder_Database import (
    add_reminder,
    start_reminder_service,
    get_today_reminders,
    get_all_reminders,
    delete_reminder
)



jarvis_awake = False
processing = False

import sqlite3

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    message TEXT
)
""")

def get_recent_messages(limit=20):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.commit()
    conn.close()

    rows.reverse()
    return rows


 
def __init__(self, db_name=str(DB_FILE), poll_interval=30):
        self.db_name = db_name
        self.poll_interval = poll_interval
        self.initialize_database()

def initialize_database(self):
        conn = sqlite3.connect(self.db_name)
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

def check_reminders(self):
        print("Reminder Service Started.")
        while True:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title
                FROM reminders
                WHERE reminder_date=? AND reminder_time=? AND completed=0
            """, (current_date, current_time))

            reminders = cursor.fetchall()
            for reminder_id, title in reminders:
                print("Reminder Triggered:", reminder_id, title)
                speak(f"Reminder. {title}")
                cursor.execute("""
                    UPDATE reminders
                    SET completed=1
                    WHERE id=?
                """, (reminder_id,))
                conn.commit()

            conn.close()
            time.sleep(self.poll_interval)

def start(self):
        thread = threading.Thread(
            target=self.check_reminders,
            daemon=True
        )
        thread.start()
        return thread


# SPEECH FUNCTIONS


conn.commit()




def update_status(text):
    global status
    if status:
        status.set(text)
def translate_to_english(text):
    try:
        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

        print(f"Original : {text}")
        print(f"English : {translated}")

        return translated.lower()

    except Exception as e:
        print("Translation Error:", e)
        return text.lower()



from speak import speak

def save_message(role, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_history (role, message) VALUES (?, ?)",
        (role, message)
    )

    conn.commit()
    conn.close()
    
def save_email(draft):
    """Save an email draft using create_email from email_assistant."""
    try:
        # create_email should handle persisting the draft
        create_email(draft)
        speak("Email saved.")
    except Exception as e:
        print("Save email error:", e)
        speak("Failed to save the email.")

def edit_email():
    """Allow user to edit the email draft."""
    global email_draft
    try:
        speak("What changes would you like to make?")
        edit_text = takeCommand()
        if edit_text:
            email_draft += f"\n{edit_text}"
            speak("Email updated.")
        show_email(email_draft)
    except Exception as e:
        print("Edit email error:", e)
        speak("Failed to edit the email.")

def send_email(draft):
    """Send the email draft."""
    try:
        speak("Sending email.")
        # create_email should handle sending
        create_email(draft)
        speak("Email sent successfully.")
    except Exception as e:
        print("Send email error:", e)
        speak("Failed to send the email.")

def show_email(draft):
    """Display email draft in the GUI."""
    try:
        print(f"Email Draft:\n{draft}")
    except Exception as e:
        print("Show email error:", e)

start_reminder_service()

# TEMPORARY TEST
def handle_power_commands(command):
    command = command.lower().strip()

    if sys.platform != "win32":
        return False

    shutdown_commands = [
        "shutdown",
        "shut down",
        "turn off the computer",
        "turn off computer",
        "power off",
        "shutdown computer",
    ]

    restart_commands = [
        "restart",
        "restart computer",
        "reboot",
        "reboot computer",
    ]

    if command in shutdown_commands:
        speak("Shutting down the computer.")
        time.sleep(1)

        os.system("shutdown /s /t 0")
        return True

    if command in restart_commands:
        speak("Restarting the computer.")
        time.sleep(1)

        os.system("shutdown /r /t 0")
        return True

    return False

def internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def open_writing_mode():
    writing_window = None


# ============================================================
# WRITING MODE
# ============================================================

writing_window = None


# ============================================================
# WRITING MODE
# ============================================================

writing_window = None


def _create_writing_mode():

    global writing_window

    try:

        # ------------------------------------------------------
        # Already open?
        # ------------------------------------------------------

        if writing_window is not None:

            try:

                if writing_window.window.winfo_exists():

                    writing_window.window.deiconify()
                    writing_window.window.lift()
                    writing_window.window.focus_force()

                    print(
                        "[JARVIS] Writing Mode already open."
                    )

                    return

            except Exception:

                writing_window = None

        # ------------------------------------------------------
        # Create Writing Mode
        # ------------------------------------------------------

        print(
            "[JARVIS] Creating Writing Mode..."
        )

        writing_window = WritingMode(
            tk_root
        )

        writing_window.window.deiconify()
        writing_window.window.lift()
        writing_window.window.focus_force()

        print(
            "[JARVIS] Writing Mode opened successfully."
        )

    except Exception as e:

        print(
            "[WRITING MODE ERROR]",
            e
        )

        traceback.print_exc()

        try:
            speak(
                "I couldn't open writing mode."
            )
        except Exception:
            pass


def open_writing_mode():
    global writing_window

    try:
        # If already open, bring it forward
        if writing_window is not None:
            try:
                if writing_window.window.winfo_exists():
                    writing_window.window.deiconify()
                    writing_window.window.lift()
                    writing_window.window.focus_force()
                    return
            except Exception:
                writing_window = None

        # Create Writing Mode
        writing_window = WritingMode()

        writing_window.window.lift()
        writing_window.window.focus_force()

        print("[JARVIS] Writing Mode opened successfully.")

    except Exception as e:
        print("[WRITING MODE ERROR]", e)
        traceback.print_exc()
def start_tk_system():
    global tk_root

    print("[JARVIS] Starting Tkinter system...")

    tk_root = tk.Tk()

    # Hide the empty root window
    tk_root.withdraw()

    print("[JARVIS] Tkinter system ready.")

    # This MUST run continuously
    tk_root.mainloop()
def aicommand(command):
    if not internet_available():
        return "You're offline. Please check your internet connection."

    if command.lower().strip() == "jarvis":
        return ""

    save_message("user", command)

    try:
        # Get recent conversation history
        history = get_recent_messages(20)

        print("\n===== HISTORY =====")
        for role, msg in history:
            print(role, ":", msg)
        print("===================\n")

        conversation = ""

        for role, msg in history:
            conversation += f"{role}: {msg}\n"

        # Send the request through the central AI provider router.
        # Provider order:
        # Gemini -> Mistral -> Cloudflare
        from ai_router import ask_ai

        prompt = f"""
You are Jarvis, a helpful AI voice assistant made by Ranabir Bhattacharjee.

You have access to conversation history below.
Treat this history as your memory.

If the user previously told you a fact or you understand how he is,
use that context when relevant and generate helpful personalized responses.

Never say:
"I don't have memory"
"I don't retain information"
"I don't remember previous conversations"

Conversation history:
{conversation}

Current user message:
{command}

Answer using the conversation history when relevant.
Give concise and useful answers.
"""

        reply = ask_ai(
            prompt,
            conversation_context=""
        )

        return reply

    except Exception as e:
        log_error("AI Router", e)

        error_text = str(e)

        print("[AI ROUTER ERROR]", error_text)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return "I've reached my AI usage limit. Please try again in a minute."

        elif "401" in error_text:
            return "My AI API key is invalid."

        elif "403" in error_text:
            return "My AI service denied access."

        else:
            return "I couldn't contact my AI service."


def play_song(song):
    pywhatkit.playonyt(song)


writing_window = None


def processcommand(command):

    global email_mode
    global email_draft
    global conversation_mode

    # ============================================================
    # 1. VALIDATE
    # ============================================================

    if not isinstance(command, str):
        print("Invalid command:", command)
        return

    command = command.strip()

    if not command:
        return

    # Translate first
    command = translate_to_english(command)

    if not isinstance(command, str):
        print("Translation returned invalid command:", command)
        return

    command = command.lower().strip()

    print(f"[COMMAND] {command}")

    # ============================================================
    # 2. IGNORE WAKE WORD
    # ============================================================

    if command in (
        "jarvis",
        "hey jarvis",
        "ok jarvis",
        "okay jarvis"
    ):
        return

    # ============================================================
    # 3. WRITING MODE
    # MUST COME BEFORE GENERIC OPEN/START COMMANDS
    # ============================================================

    writing_commands = (
        "writing mode",
        "open writing mode",
        "start writing mode",
        "launch writing mode",
        "open writer",
        "start writer",
        "launch writer",
        "writing workspace",
        "open writing workspace"
    )

    if any(
        phrase == command or
        command.startswith(phrase + " ")
        for phrase in writing_commands
    ):

        print("[JARVIS] Opening Writing Mode...")

        try:
            open_writing_mode()
        except Exception as e:
            print("[Writing Mode Error]", e)
            traceback.print_exc()
            speak("I couldn't open writing mode.")

        return

    # ============================================================
    # 4. CLOSE CONVERSATION MODE
    # FIXED BOOLEAN LOGIC
    # ============================================================

    close_conversation_commands = (
        "close conversation mode",
        "stop conversation mode",
        "exit conversation mode",
        "deactivate conversation mode",
        "stop the chat",
        "end the chat",
        "close the chat",
        "stop chatting"
    )

    if any(
        phrase == command or
        command.startswith(phrase + " ")
        for phrase in close_conversation_commands
    ):

        try:
            conversation_mode.deactivate()
            speak("Conversation mode closed.")
        except Exception as e:
            print("[Conversation Mode Error]", e)

        return

    # ============================================================
    # 5. START CONVERSATION MODE
    # ============================================================

    conversation_commands = (
        "start conversation mode",
        "open conversation mode",
        "launch conversation mode",
        "activate conversation mode",
        "start a conversation",
        "let's start a conversation",
        "lets start a conversation",
        "let's chat",
        "lets chat",
        "start chatting",
        "talk with me"
    )

    if any(
        phrase == command or
        command.startswith(phrase + " ")
        for phrase in conversation_commands
    ):

        try:
            conversation_mode.start()
            speak("Conversation mode activated.")
        except Exception as e:
            print("[Conversation Mode Error]", e)
            speak("I couldn't start conversation mode.")

        return

    # ============================================================
    # 6. REMINDERS
    # BEFORE GENERIC CREATE/ADD COMMANDS
    # ============================================================

    if command.startswith("remind me"):

        try:

            create_reminder(command)

            speak(
                "Reminder added successfully."
            )

        except Exception as e:

            print(
                "[Reminder Error]",
                e
            )

            speak(
                "Sorry, I couldn't add the reminder."
            )

        return

    # ============================================================
    # 7. TODAY'S SCHEDULE
    # BEFORE GENERIC CALENDAR COMMANDS
    # ============================================================

    if (
        command == "today schedule"
        or
        command == "today's schedule"
        or
        command == "show today's schedule"
        or
        command == "show today schedule"
        or
        command == "what is my schedule today"
        or
        command == "what's my schedule today"
    ):

        try:

            events = get_today_events()

            if not events:

                speak(
                    "You have no events scheduled for today."
                )

                return

            speak(
                f"You have {len(events)} "
                f"event{'s' if len(events) != 1 else ''} today."
            )

            for event in events:

                summary = event.get(
                    "summary",
                    "Untitled Event"
                )

                start = event[
                    "start"
                ].get(
                    "dateTime",
                    event["start"].get("date")
                )

                try:

                    dt = datetime.fromisoformat(
                        start.replace(
                            "Z",
                            "+00:00"
                        )
                    )

                    time_str = dt.strftime(
                        "%I:%M %p"
                    )

                    speak(
                        f"{summary} at {time_str}"
                    )

                except Exception:

                    speak(summary)

        except Exception as e:

            print(
                "[Calendar Error]",
                e
            )

            speak(
                "I couldn't read today's schedule."
            )

        return

    # ============================================================
    # 8. CALENDAR / SCHEDULE
    # ============================================================

    if command.startswith(
        (
            "schedule ",
            "add event ",
            "create event ",
            "schedule an event ",
            "add a calendar event ",
            "create a calendar event "
        )
    ):

        try:

            title, start = parse_calendar_command(
                command
            )

            if start is None:

                speak(
                    "Sorry, I could not understand the date and time."
                )

                return

            if not title:

                title = "Untitled Event"

            end = start + timedelta(
                hours=1
            )

            add_event(
                title,
                start,
                end
            )

            speak(
                f"{title} has been added to your calendar."
            )

        except Exception as e:

            print(
                "[Calendar Error]",
                e
            )

            speak(
                "Sorry, I couldn't create that calendar event."
            )

        return

    # ============================================================
    # 9. WIKIPEDIA
    # ============================================================

    if command.startswith(
        "search wikipedia"
    ):

        query = command[
            len("search wikipedia"):
        ].strip()

        if not query:

            speak(
                "What would you like me to search on Wikipedia?"
            )

            return

        speak(
            f"Searching Wikipedia for {query}"
        )

        url = (
            "https://en.wikipedia.org/wiki/"
            "Special:Search?search="
            + urllib.parse.quote(query)
        )

        webbrowser.open(url)

        return

    # ============================================================
    # 10. YOUTUBE SEARCH
    # ============================================================

    if command.startswith(
        "search youtube"
    ):

        query = command[
            len("search youtube"):
        ].strip()

        if not query:

            speak(
                "What would you like me to search on YouTube?"
            )

            return

        speak(
            f"Searching YouTube for {query}"
        )

        url = (
            "https://www.youtube.com/results"
            "?search_query="
            + urllib.parse.quote(query)
        )

        webbrowser.open(url)

        return

    # ============================================================
    # 11. GENERAL WEB SEARCH
    # ============================================================

    if command.startswith(
        "search "
    ):

        query = command[
            len("search "):
        ].strip()

        if not query:

            speak(
                "What would you like me to search?"
            )

            return

        speak(
            f"Searching for {query}"
        )

        try:

            search_web(query)

        except Exception as e:

            print(
                "[Search Error]",
                e
            )

            speak(
                "Sorry, I couldn't perform the search."
            )

        return

    # ============================================================
    # 12. PLAY MUSIC
    # ============================================================

    if command.startswith(
        "play "
    ):

        song = command[
            len("play "):
        ].strip()

        if not song:

            speak(
                "What song would you like me to play?"
            )

            return

        speak(
            f"Playing {song} on YouTube."
        )

        try:

            play_song(song)

        except Exception as e:

            print(
                "[Music Error]",
                e
            )

            speak(
                "Sorry, I couldn't play that."
            )

        return

    # ============================================================
    # 13. GOOGLE
    # ============================================================

    if command in (
        "google",
        "open google",
        "launch google",
        "start google"
    ):

        speak(
            "Opening Google."
        )

        webbrowser.open(
            "https://www.google.com"
        )

        return

    # ============================================================
    # 14. GENERIC OPEN / LAUNCH / START / RUN
    #
    # This comes AFTER all special commands.
    # ============================================================

    open_prefixes = (
        "open ",
        "launch ",
        "start ",
        "run "
    )

    matched_prefix = None

    for prefix in open_prefixes:

        if command.startswith(prefix):

            matched_prefix = prefix
            break

    if matched_prefix:

        target = command[
            len(matched_prefix):
        ].strip()

        if not target:

            speak(
                "What would you like me to open?"
            )

            return

        print(
            f"[OPEN] Target: {target}"
        )

        # --------------------------------------------------------
        # 14A. COMMON WEBSITES
        # --------------------------------------------------------

        websites = {

            "youtube":
                "https://youtube.com",

            "google":
                "https://google.com",

            "gmail":
                "https://mail.google.com",

            "github":
                "https://github.com",

            "chatgpt":
                "https://chat.openai.com",

            "facebook":
                "https://facebook.com",

            "instagram":
                "https://instagram.com",

            "linkedin":
                "https://linkedin.com",

            "spotify":
                "https://spotify.com",

            "whatsapp":
                "https://web.whatsapp.com",

            "amazon":
                "https://amazon.in",

            "netflix":
                "https://netflix.com"
        }

        if target in websites:

            speak(
                f"Opening {target}."
            )

            webbrowser.open(
                websites[target]
            )

            return

        # --------------------------------------------------------
        # 14B. FILE / FOLDER
        # --------------------------------------------------------

        if os.path.exists(target):

            try:

                open_path(target)

                speak(
                    f"Opening {os.path.basename(target)}."
                )

                return

            except Exception as e:

                print(
                    "[File Open Error]",
                    e
                )

        # --------------------------------------------------------
        # 14C. INSTALLED APPLICATION
        # --------------------------------------------------------

        try:

            if open_app(target):

                return

        except Exception as e:

            print(
                "[App Open Error]",
                e
            )

        # --------------------------------------------------------
        # 14D. DIRECT WEBSITE
        # --------------------------------------------------------

        if (
            "." in target
            and " " not in target
        ):

            url = target

            if not url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                url = (
                    "https://"
                    + url
                )

            speak(
                "Opening website."
            )

            webbrowser.open(url)

            return

        # --------------------------------------------------------
        # 14E. EVERYTHING SEARCH
        # --------------------------------------------------------

        try:

            result = subprocess.check_output(
                [
                    ES_PATH,
                    target
                ],
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            matches = [
                line.strip()
                for line in result.splitlines()
                if line.strip()
            ]

            if matches:

                open_path(
                    matches[0]
                )

                speak(
                    f"Opening {target}."
                )

                return

        except Exception as e:

            print(
                "[Everything Search Error]",
                e
            )

        # --------------------------------------------------------
        # 14F. NOTHING FOUND
        # --------------------------------------------------------

        speak(
            f"I couldn't find {target}."
        )

        return
    #-------------------------------------------------------------
    #16. SYSTEM COMMANDS
    #-------------------------------------------------------------  
    if "shutdown" in command or "restart" in command or "turn off" in command:

        if handle_power_commands(command):
            return
   

    # ============================================================
    # 15. DEFAULT AI
    # ============================================================

    try:

        output = aicommand(
            command
        )

        if output:

            print(output)

            speak(output)

        else:

            speak(
                "I didn't receive a response."
            )

    except Exception as e:

        print(
            "[AI Command Error]",
            e
        )

        speak(
            "Sorry, I couldn't process that request."
        )

    return
def voice_loop():

    global conversation_mode

    print("[VOICE] Voice loop started.")

    while True:

        try:

            # Conversation mode handles its own listening
            if conversation_mode is not None and conversation_mode.active:
                time.sleep(0.1)
                continue

            print("Listening for wake word...")

            word = listen(
                timeout=5,
                phrase_time_limit=5
            )

            if not word:
                continue

            word = word.lower().strip()

            print(f"[WAKE LISTEN] {word}")

            if "jarvis" not in word:
                continue

            speak("Yes sir")

            print("Waiting for command...")

            command = listen(
                timeout=8,
                phrase_time_limit=8
            )

            if not command:
                speak("I didn't catch that.")
                continue

            command = command.lower().strip()

            print(f"[COMMAND] {command}")

            processcommand(command)

        except sr.WaitTimeoutError:

            print("[VOICE] Listening timeout.")
            continue

        except sr.UnknownValueError:

            print("[VOICE] Could not understand audio.")
            continue

        except sr.RequestError as e:

            print("[VOICE] Speech recognition service error:", e)
            time.sleep(2)

        except Exception as e:

            print("[VOICE LOOP ERROR]", e)
            traceback.print_exc()
            time.sleep(2)
def listen_for_command():
    try:
        command = listen(
            timeout=8,
            phrase_time_limit=8
        )

        if command is None:
            speak("I didn't catch that.")
            return

        processcommand(command)

    except sr.UnknownValueError:
        pass
    except sr.WaitTimeoutError:
        pass
    except sr.RequestError:
        speak("Speech service is unavailable")
    except Exception as e:
        print("Voice Loop Error:", e)
        traceback.print_exc()
        time.sleep(2)
if __name__ == "__main__":

    speak("Initializing Jarvis")

    try:
        voice_loop()

    except Exception as e:
        print(f"Fatal Error: {e}")
        logging.error(traceback.format_exc())
        input("Press Enter to exit...")
