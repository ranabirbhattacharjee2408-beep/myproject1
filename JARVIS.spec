# -*- mode: python ; coding: utf-8 -*-
# Single build spec for JARVIS (Windows .exe folder / macOS .app).
from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH)


def safe(fn, *args):
    try:
        return fn(*args)
    except Exception:
        return []


hiddenimports = (
    safe(collect_submodules, "google.genai")
    + safe(collect_submodules, "mistralai")
    + safe(collect_submodules, "pyttsx3.drivers")
    + safe(collect_submodules, "dateparser")
    + [
        "desktop_bot", "audio.microphone", "edge_tts", "speech_recognition",
        "pygame", "wikipedia", "pywhatkit", "deep_translator",
    ]
)

# customtkinter ships theme JSON/fonts that MUST be bundled or the window crashes
datas = (
    safe(collect_data_files, "customtkinter")
    + safe(collect_data_files, "speech_recognition")
    + safe(collect_data_files, "dateparser")
    + safe(collect_data_files, "certifi")
    + [(str(ROOT / "bot.png"), "."), (str(ROOT / "JARVIS.ico"), ".")]
)

icon = str(ROOT / "JARVIS.ico") if sys.platform == "win32" else None

a = Analysis(
    ["launcher.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="JARVIS",
    debug=False,
    strip=False,
    upx=False,          # UPX often triggers antivirus false-positives
    console=False,
    icon=icon,
)

coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=False, name="JARVIS",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="JARVIS.app",
        icon=None,
        bundle_identifier="com.jarvis.assistant",
        info_plist={
            "NSMicrophoneUsageDescription": "JARVIS listens for your voice commands.",
            "NSAppleEventsUsageDescription": "JARVIS opens apps on your behalf.",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
