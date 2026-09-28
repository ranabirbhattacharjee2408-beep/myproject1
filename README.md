# JARVIS

Voice-controlled desktop assistant: AI chat (Gemini → Mistral → Cloudflare fallback),
voice in/out, reminders, Google Calendar, email drafts, web search, writing mode and a
floating desktop companion bot.

## Run from source
    pip install -r requirements-desktop.txt
    python launcher.py

## Build an installer
See [BUILD.md](BUILD.md) — Windows `.exe` installer or macOS `.dmg`.

## Configuration
First launch asks for an AI key and stores it in `~/.jarvis/.env`. Nothing secret is
ever bundled into the installer. Say "Jarvis" to wake it, or type commands in the window.

`dev_tools/` holds manual test scripts (not part of the app).
