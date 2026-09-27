#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python_bin="$(command -v python3.12 || command -v python3)"
"$python_bin" -m venv .venv
source .venv/bin/activate
rm -rf build dist release
python -m pip install --upgrade pip
python -m pip install -r requirements-desktop.txt
python -m pip install pyinstaller
python -m PyInstaller --clean --noconfirm JARVIS.spec

mkdir -p release
ditto -c -k --sequesterRsrc --keepParent dist/JARVIS release/JARVIS-macOS.zip
echo "Portable build created at: $(pwd)/release/JARVIS-macOS.zip"