#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-desktop.txt
python -m pip install pyinstaller
python -m PyInstaller --clean --noconfirm JARVIS.spec

mkdir -p release
ditto -c -k --sequesterRsrc --keepParent dist/JARVIS release/JARVIS-macOS.zip
echo "Portable build created at: $(pwd)/release/JARVIS-macOS.zip"