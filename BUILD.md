# JARVIS desktop builds

JARVIS is a Python desktop app with a CustomTkinter interface, voice input,
speech output, reminders, calendar support, and a multi-provider AI fallback
chain.

## Windows

1. Install Python 3.12 and Inno Setup.
2. Copy `.env.example` to `%USERPROFILE%\.jarvis\.env`.
3. Add at least one AI provider key to that file.
4. Run `build_windows.ps1` in PowerShell.
5. Open `installer/JARVIS.iss` in Inno Setup to create `installer/output/JARVIS_Setup.exe`.

## macOS

1. Install Python 3.12 and PortAudio (`brew install portaudio`).
2. Copy `.env.example` to `~/.jarvis/.env`.
3. Add at least one AI provider key.
4. Run `./build_macos.sh`.

The macOS build creates `release/JARVIS-macOS.zip`. Some computer-control
commands remain Windows-specific and return no action on macOS; chat, voice,
web search, writing mode, reminders, and provider fallback remain available.

## Google Calendar

Calendar integration is optional. Put your own downloaded OAuth client file at
`~/.jarvis/credentials.json`. The app stores the OAuth token in the same
user-data directory and never bundles either file into the installer.