# Building JARVIS as an installable app

The app entry point is `launcher.py`. It opens the JARVIS window, runs the voice
loop in the background and starts the floating desktop bot (same executable,
`--bot` mode). On first launch it asks for an AI key and stores it in
`~/.jarvis/.env` (never inside the installer). Logs: `~/.jarvis/console.log` (and `~/.jarvis/logs/jarvis.log`).

## Windows (.exe installer)
1. Install Python 3.12 and Inno Setup 6.
2. Run `build_windows.ps1` in PowerShell.
3. Result: `installer\output\JARVIS_Setup.exe` (also the plain folder `dist\JARVIS`).

## macOS (.dmg)
1. Install Python 3.12 and `brew install portaudio`.
2. Run `./build_macos.sh`  ->  `release/JARVIS.dmg`.
3. The app is unsigned: right-click > Open the first time, and allow Microphone.
   Windows-only commands (Everything search, some power/system commands) return
   no action on macOS.

## Tip: reproducible builds
On a machine where JARVIS runs correctly: `pip freeze > requirements-lock.txt`.
The build scripts use that file automatically when it exists.

## Google Calendar (optional)
Put your OAuth client file at `~/.jarvis/credentials.json`.

## Build in the cloud (no local setup)
Push this project to GitHub, open **Actions → Build JARVIS installers → Run workflow**.
When it finishes, download `JARVIS-Windows-Installer` (JARVIS_Setup.exe) and
`JARVIS-macOS-DMG` (JARVIS.dmg) from the run's *Artifacts* section.
