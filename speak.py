import os
import time
import requests
import pygame
from dotenv import load_dotenv
import pyttsx3
from logger import log_error
import threading
import edge_tts
import asyncio
import tempfile

from config import DATA_DIR

speaking = False
stop_requested = False
engine = None
# -----------------------------
# Initialize Pygame Mixer
# -----------------------------
try:
    pygame.mixer.init()
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    print("Mixer initialized")
except Exception as e:
    print("Mixer initialization failed:", e)

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")


# -----------------------------
# Save Messages
# -----------------------------
def save_message(sender, text):
    try:
        with open(DATA_DIR / "messages.log", "a", encoding="utf-8") as file:
            file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {sender}: {text}\n")
    except Exception:
        pass
def play_audio(filename):
    global speaking, stop_requested

    speaking = True
    stop_requested = False

    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except Exception as error:
        log_error("Audio playback", error)
        speaking = False
        return

    while pygame.mixer.music.get_busy():

        if stop_requested:
            pygame.mixer.music.stop()
            break

        time.sleep(0.05)

    pygame.mixer.music.unload()
    speaking = False

    try:
        os.remove(filename)
    except Exception:
        pass
# -----------------------------
# Speak Function
# -----------------------------
def offline_speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log_error("Offline TTS", e)
def speak(text):
    global speaking, stop_requested

    print(">>> speak() called")
    print("Text:", text)

    if text.lower() not in [
        "yes sir",
        "listening",
        "give a command",
        "sorry, i didn't understand",
        "initializing jarvis"
    ]:
        save_message("assistant", text)

    try:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        filename = temp.name
        temp.close()

        async def generate():
            communicate = edge_tts.Communicate(
                text=text,
                voice="en-US-GuyNeural"   # Change voice here
            )
            await communicate.save(filename)

        asyncio.run(generate())

        threading.Thread(
            target=play_audio,
            args=(filename,),
            daemon=True
        ).start()
    


    except Exception as e:
        log_error("Edge TTS", e)
        offline_speak(text)
def stop_speaking():
    global speaking, stop_requested

    if speaking:
        stop_requested = True
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        speaking = False


# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    speak("Hello, this is Jarvis speaking.")