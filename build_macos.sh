#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

for f in launcher.py main.py jarvis_gui.py desktop_bot.py bot.png JARVIS.spec; do
  [ -s "$f" ] || { echo "Missing or empty: $f"; exit 1; }
done
command -v brew >/dev/null && brew list portaudio >/dev/null 2>&1 || \
  echo "Note: PyAudio needs PortAudio -> brew install portaudio"

python_bin="$(command -v python3.12 || command -v python3)"
"$python_bin" -m venv .venv
source .venv/bin/activate
rm -rf build dist release
python -m pip install --upgrade pip
if [ -f requirements-lock.txt ]; then
  python -m pip install -r requirements-lock.txt
else
  python -m pip install -r requirements-desktop.txt
fi
python -m pip install pyinstaller
python -m PyInstaller --clean --noconfirm JARVIS.spec

mkdir -p release
hdiutil create -volname "JARVIS" -srcfolder dist/JARVIS.app -ov -format UDZO release/JARVIS.dmg
echo "DMG created: $(pwd)/release/JARVIS.dmg"
echo "Unsigned app: on first launch right-click JARVIS.app > Open, and allow Microphone in System Settings."
