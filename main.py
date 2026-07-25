
import uuid
import pyautogui
import pygame
from google import genai
import speech_recognition as sr
import pyttsx3
import webbrowser
import traceback
import logging
import email
from datetime import datetime, timedelta

import music_library
import requests
import os
import playsound
import time
import customtkinter as ctk
from tkinter import StringVar
import threading
import winshell
from deep_translator import GoogleTranslator
from app_louncher import open_app
from remainder_perser import create_reminder
from system_commands import system_command
from remainder_perser import create_reminder 
from calendar_manager import add_event, get_today_events
from email_assistant import GeminiEmail, create_email, takeCommand
from calendar_ai import parse_calendar_command
from calendar_manager import add_event
from logger import log_info, log_warning, log_error


waiting_for_confirmation = False
pending_action = None
pending_app = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


from Reminder_Database import (
    add_reminder,
    start_reminder_service,
    get_today_reminders,
    get_all_reminders,
    delete_reminder
)




GEMINI_API_KEY = "AQ.Ab8RN6JVIizOwBhoHmNdGQWwLbXOw9Q8GVsIfvDdLtRv5ohtRw"
import sqlite3

conn = sqlite3.connect("jarvis_memory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    message TEXT
)
""")

def get_recent_messages(limit=20):
    conn = sqlite3.connect("jarvis_memory.db")
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


 
def __init__(self, db_name="jarvis_memory.db", poll_interval=30):
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
            now = datetime.datetime.now()
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

r = sr.Recognizer()
engine = pyttsx3.init('sapi5')


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
def gui():

    root = ctk.CTk()
    root.title("JARVIS AI")
    root.geometry("1000x700")

    # Header
    title = ctk.CTkLabel(
        root,
        text="J A R V I S",
        font=("Arial", 40, "bold"),
        text_color="#00FFFF"
    )
    title.pack(pady=20)

    # Status
    status_label = ctk.CTkLabel(
        root,
        text="🟢 SYSTEM ONLINE",
        font=("Consolas", 18),
        text_color="#00FF88"
    )
    status_label.pack()

    # Chat Box
    chatbox = ctk.CTkTextbox(
        root,
        width=900,
        height=450,
        font=("Consolas", 14)
    )
    chatbox.pack(pady=20)

   

    chatbox.insert("end", "JARVIS INITIALIZED...\n")
    chatbox.insert("end", "Ready for commands.\n\n")

    # Bottom Frame
    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.pack(fill="x", padx=20, pady=10)

    command_entry = ctk.CTkEntry(
        bottom_frame,
        width=650,
        placeholder_text="Enter command..."
    )
    command_entry.pack(side="left", padx=10, pady=10)

    def execute():
        cmd = command_entry.get().strip()

        if cmd:
            chatbox.insert("end", f"You: {cmd}\n")

            try:
                # Run the command in a background thread. We don't have a
                # synchronous "response" variable here, so just report that
                # the command was executed; any output should be handled by
                # processcommand itself (e.g., updating the UI or logging).
                threading.Thread(
                    target=processcommand,
                    args=(cmd,),
                    daemon=True
                ).start()

                chatbox.insert("end", "Jarvis: Command executed.\n")

            except Exception as e:
                chatbox.insert("end", f"Error: {e}\n")

            chatbox.see("end")
            command_entry.delete(0, "end")

    execute_btn = ctk.CTkButton(
        bottom_frame,
        text="⚡ EXECUTE",
        command=execute,
        width=120
    )
    execute_btn.pack(side="left", padx=5)

    root.mainloop()

    # ================= CENTER =================

    center = ctk.CTkFrame(root)
    center.pack(fill="both", expand=True, padx=15, pady=10)

    # Left Panel
    left = ctk.CTkFrame(center, width=250)
    left.pack(side="left", fill="y", padx=10, pady=10)

    ctk.CTkLabel(
        left,
        text="SYSTEM STATUS",
        font=("Arial", 20, "bold"),
        text_color="#00FFFF"
    ).pack(pady=15)

    status_label = ctk.CTkLabel(
        left,
        text="🟢 READY",
        font=("Consolas", 18)
    )
    status_label.pack(pady=10)

    # Fake AI Core
    ai_core = ctk.CTkLabel(
        left,
        text="◉",
        font=("Arial", 100),
        text_color="#00FFFF"
    )
    ai_core.pack(pady=40)

    # Right Panel
    right = ctk.CTkFrame(center)
    right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(
        right,
        text="CONVERSATION",
        font=("Arial", 20, "bold"),
        text_color="#00FFFF"
    ).pack(pady=10)

    chatbox = ctk.CTkTextbox(
        right,
        width=650,
        height=350,
        font=("Consolas", 14)
    )
    chatbox.pack(fill="both", expand=True, padx=10, pady=10)

    chatbox.insert("end", "JARVIS INITIALIZED...\n")

    # ================= BOTTOM =================

    bottom = ctk.CTkFrame(root)
    bottom.pack(fill="x", padx=15, pady=15)

    command_entry = ctk.CTkEntry(
        bottom,
        width=650,
        placeholder_text="Enter command..."
    )
    command_entry.pack(side="left", padx=10, pady=10)

    def execute():
        cmd = command_entry.get()
        if cmd:
            chatbox.insert("end", f"\nYou: {cmd}\n")
            chatbox.insert("end", "Jarvis: Processing...\n")
            chatbox.see("end")
            command_entry.delete(0, "end")

    execute_btn = ctk.CTkButton(
        bottom,
        text="⚡ EXECUTE",
        width=120,
        command=execute
    )
    execute_btn.pack(side="left", padx=5)

    voice_btn = ctk.CTkButton(
        bottom,
        text="🎤 LISTEN",
        width=120
    )
    voice_btn.pack(side="left", padx=5)

    root.mainloop()


from speak import speak

def save_message(role, message):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_history (role, message) VALUES (?, ?)",
        (role, message)
    )

    conn.commit()
    conn.close()
    

start_reminder_service()

# TEMPORARY TEST

def internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False
def aicommand(command):
    if not internet_available():
     return "You're offline. Please check your internet connection."

    if command.lower().strip() == "jarvis":
        return ""
    save_message("user", command)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        history = get_recent_messages(20)
        print("\n===== HISTORY =====")
        for role, msg in history:
          print(role, ":", msg)
        print("===================\n")

        conversation = ""

        for role, msg in history:
            conversation += f"{role}: {msg}\n"

        prompt = f"""
You are Jarvis, a helpful AI voice assistant made by Ranabir Bhattacharjee.

You have access to conversation history below.
Treat this history as your memory.
about the
If the user previously told you a fact  or you underastand how he is,
you should remember and use it and constantly understand your user and generate helpful responses especially when the user asks for personalized assistance.

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

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        reply = response.text

       

        return reply

    except Exception as e:
     log_error("Gemini", e)

     error_text = str(e)

     if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        return "I've reached my AI usage limit. Please try again in a minute."

     elif "401" in error_text:
        return "My AI API key is invalid."

     elif "403" in error_text:
        return "My AI service denied access."

     else:
        return "I couldn't contact my AI service."
def processcommand(command):
    
    command = command.lower().strip()
    command = translate_to_english(command)

    # Handle Windows commands first
    if handle_windows_commands(command):
        return
    if command == "jarvis":
        return
    API_KEY = "875d98a266774be28fa8ac00126fead4"

    if any(command.startswith(word) for word in ["open", "launch", "start", "run"]):
        response = open_app(command)
        speak(response)
        return

    if "play" in command:
        song = command.replace("play ", "").strip()
        if song in music_library.music:
            speak(f"Playing {song}")
            webbrowser.open(music_library.music[song])
        else:
            speak("Song not found in library")
        return

    if "google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        return

    if command.lower().startswith("remind me"):
        try:
            create_reminder(command)
            speak("Reminder added successfully.")
        except Exception as e:
            print("Reminder Error:", e)
            speak("Sorry, I couldn't add the reminder.")
        return
    
    elif command.startswith(("schedule", "add", "create")):

     title, start = parse_calendar_command(command)

     if start is None:
        speak("Sorry, I could not understand the date and time.")
        return

     if title == "":
        title = "Untitled Event"

     end = start + timedelta(hours=1)

     add_event(title, start, end)

     speak(f"{title} has been added to your calendar.")
    elif "today schedule" in command.lower() or "today's schedule" in command.lower():

     events = get_today_events()

     if not events:
        speak("You have no events scheduled for today.")
        return

     speak(f"You have {len(events)} event{'s' if len(events) > 1 else ''} today.")

     for event in events:
        summary = event.get("summary", "Untitled Event")

        start = event["start"].get("dateTime", event["start"].get("date"))

        try:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            time_str = dt.strftime("%I:%M %p")
            speak(f"{summary} at {time_str}")
        except Exception:
            speak(summary)
    if "write an email" in command:
     speak("What should I write in the email?")
     email_text = takeCommand()      # your speech recognition function

     email_client = GeminiEmail()
     email = email_client.draft(email_text)
     speak.speak("Here is your email.")
     print(email)
    if "news" in command:
        speak("Fetching news for you")
        try:
            response = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
            )
            news = response.json()
            articles = news.get("articles", [])
            if not articles:
                speak("No news found")
                return
            for article in articles[:5]:
                title = article.get("title")
                if title:
                    print(title)
                    speak(title)
            if "totalResults" in news and news["totalResults"] == 0:
                speak("No news found")
        except Exception as e:
            print("News error:", e)
            speak("I could not fetch news.")
        return

    output = aicommand(command)
    print(output)
    speak(output)
app_index = {}

start_menu_paths = [
    os.path.join(os.environ["APPDATA"],
                 r"Microsoft\Windows\Start Menu\Programs"),

    os.path.join(os.environ["PROGRAMDATA"],
                 r"Microsoft\Windows\Start Menu\Programs")
]

for start_menu in start_menu_paths:
    for root, dirs, files in os.walk(start_menu):
        for file in files:
            if file.endswith(".lnk"):
                app_name = os.path.splitext(file)[0].lower()
                app_index[app_name] = os.path.join(root, file)

print(f"Loaded {len(app_index)} applications.")

def open_app(command):
    command = command.lower().strip()

    # Remove the opening keyword
    for word in ["open", "launch", "start", "run"]:
        if command.startswith(word):
            command = command.replace(word, "", 1).strip()
            break

    if not command:
        return "Please tell me which app to open."

    # Exact match
    if command in app_index:
        os.startfile(app_index[command])
        return f"Opening {command}"

    # Partial match
    for app_name, shortcut in app_index.items():
        if command in app_name:
            os.startfile(shortcut)
            return f"Opening {app_name}"

    return "Sorry, I couldn't find that application."
from app_louncher import open_app
from system_commands import system_command

def handle_windows_commands(command):
    command = command.lower().strip()

    # Handle system commands first
    if system_command(command):
        speak("Done.")
        return True

    # Handle app launching
    if open_app(command):
        speak("Opening application.")
        return True

    return False
def voice_loop():

    while True:
           

        try:
            log_info("Listening for wake word...")
            print("Listening for wake word...")

            with sr.Microphone(device_index=1) as source:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)

            word = r.recognize_google(audio).lower()
            print("Heard:", word)

            if "jarvis" in word:

                speak("Yes sir")

                print("give a  command...")

                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)

                try:
                    command = r.recognize_google(audio).lower()
                    print("Command:", command)
                    processcommand(command)

                except sr.UnknownValueError:
                    speak("I could not understand the command")

                except sr.RequestError:
                    speak("Network error in speech recognition")

        except sr.UnknownValueError:
            print("Could not understand wake word")

        except sr.WaitTimeoutError:
            print("Listening timed out")

        except Exception as e:
          log_error("Voice Loop", e)
          speak("Something went wrong, but I'm still running.")
if __name__ == "__main__":
    speak("Initializing Jarvis")

    threading.Thread(
        target=voice_loop,
        daemon=True
    ).start()

    try:
        gui()
    except Exception as e:
        print(f"Fatal Error: {e}")
        logging.error(traceback.format_exc())

        input("Press Enter to exit...")
