import os
import time
import requests
import pygame
from dotenv import load_dotenv
import pyttsx3
from logger import log_error
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

print("Current folder:", os.getcwd())
print(".env exists:", os.path.exists(".env"))

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

print("API Key Loaded:", ELEVEN_API_KEY is not None)
print("Voice ID:", VOICE_ID)


# -----------------------------
# Save Messages
# -----------------------------
def save_message(sender, text):
    try:
        with open("messages.log", "a", encoding="utf-8") as file:
            file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {sender}: {text}\n")
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

    if not ELEVEN_API_KEY:
        offline_speak(text)
        return

    if not VOICE_ID:
        offline_speak(text)
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        print("Status Code:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
         log_error("ElevenLabs API", Exception(response.text))
         offline_speak(text)
         return

        filename = f"speech_{int(time.time()*1000)}.mp3"

        with open(filename, "wb") as f:
            f.write(response.content)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()

        try:
            os.remove(filename)
        except Exception:
            pass

    except Exception as e:
        log_error("ElevenLabs", e)
        offline_speak(text)


# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    speak("Hello, this is Jarvis speaking.")