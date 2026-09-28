"""JARVIS desktop entry point.

  python launcher.py           -> full app (window + voice loop + desktop bot)
  JARVIS.exe / JARVIS.app      -> same thing, once packaged
  ... --bot                    -> runs only the floating desktop bot
"""
import os
import sys
import socket
import subprocess
import threading
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

LOCK_PORT = 8766  # single-instance guard (the bot itself uses UDP 8765)


def data_dir():
    return Path(os.getenv("JARVIS_DATA_DIR", str(Path.home() / ".jarvis"))).expanduser()


# ----------------------------------------------------------------------
# --bot mode: desktop_bot.py runs its window at import time
# ----------------------------------------------------------------------
def run_bot_only():
    import desktop_bot  # noqa: F401  (blocks in mainloop)


# ----------------------------------------------------------------------
# first-run API key setup (must happen BEFORE config/main are imported)
# ----------------------------------------------------------------------
KEYS = ("GEMINI_API_KEY", "MISTRAL_API_KEY", "CLOUDFLARE_API_TOKEN")


def ensure_keys():
    from dotenv import load_dotenv

    folder = data_dir()
    folder.mkdir(parents=True, exist_ok=True)
    env_path = folder / ".env"
    load_dotenv(env_path)
    if any(os.getenv(k) for k in KEYS):
        return

    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    win = ctk.CTk()
    win.title("JARVIS — First-time setup")
    win.geometry("520x330")
    win.resizable(False, False)
    ctk.CTkLabel(
        win, text="Add at least one AI key",
        font=("Arial", 20, "bold"),
    ).pack(pady=(20, 4))
    ctk.CTkLabel(
        win,
        text="Keys are stored only on this computer in\n" + str(env_path),
        text_color="#8FA9B8",
    ).pack(pady=(0, 12))
    gem = ctk.CTkEntry(win, width=420, placeholder_text="Gemini API key")
    gem.pack(pady=6)
    mis = ctk.CTkEntry(win, width=420, placeholder_text="Mistral API key (optional)")
    mis.pack(pady=6)

    def save():
        lines = []
        if gem.get().strip():
            lines.append(f"GEMINI_API_KEY={gem.get().strip()}")
        if mis.get().strip():
            lines.append(f"MISTRAL_API_KEY={mis.get().strip()}")
        if lines:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        win.destroy()

    row = ctk.CTkFrame(win, fg_color="transparent")
    row.pack(pady=18)
    ctk.CTkButton(row, text="Save & Continue", command=save).pack(side="left", padx=8)
    ctk.CTkButton(
        row, text="Skip (AI chat disabled)", fg_color="#3A4A55", command=win.destroy
    ).pack(side="left", padx=8)
    win.mainloop()
    load_dotenv(env_path, override=True)


# ----------------------------------------------------------------------
# console -> GUI + log file
# ----------------------------------------------------------------------
class Tee:
    def __init__(self, gui, logfile, on_line):
        self.gui, self.on_line = gui, on_line
        self.buf = ""
        self.lock = threading.Lock()
        try:
            self.file = open(logfile, "a", encoding="utf-8", buffering=1)
        except Exception:
            self.file = None

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)
        with self.lock:
            self.buf += s
            while "\n" in self.buf:
                line, self.buf = self.buf.split("\n", 1)
                line = line.rstrip()
                if not line:
                    continue
                if self.file:
                    self.file.write(line + "\n")
                self.on_line(line)
                if not line.startswith("[BOT CONTROL]"):
                    self.gui.log(line)
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


def status_for(line):
    low = line.lower()
    if "listening for wake word" in low:
        return "STANDBY"
    if "waiting for command" in low:
        return "LISTENING"
    if line.startswith("[COMMAND]"):
        return "THINKING"
    if ">>> speak() called" in line:
        return "SPEAKING"
    return None


# ----------------------------------------------------------------------
def start_bot():
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--bot"]
    else:
        cmd = [sys.executable, str(Path(__file__).resolve()), "--bot"]
    try:
        return subprocess.Popen(cmd)
    except Exception as error:
        print("[LAUNCHER] Could not start desktop bot:", error)
        return None


def main_app():
    lock = socket.socket()
    try:
        lock.bind(("127.0.0.1", LOCK_PORT))
        lock.listen(1)
    except OSError:
        from tkinter import Tk, messagebox
        r = Tk(); r.withdraw()
        messagebox.showinfo("JARVIS", "JARVIS is already running.")
        return

    ensure_keys()

    # pywhatkit can fail to import when offline; don't let that kill the app
    try:
        import pywhatkit  # noqa: F401
    except Exception:
        import types
        stub = types.ModuleType("pywhatkit")
        stub.playonyt = lambda *a, **k: print("[JARVIS] pywhatkit unavailable (offline?)")
        stub.search = stub.playonyt
        sys.modules["pywhatkit"] = stub

    from jarvis_gui import JarvisGUI

    gui = JarvisGUI()
    sys.stdout = Tee(gui, data_dir() / "console.log",
                     lambda l: (status_for(l) and gui.set_status(status_for(l))))
    sys.stderr = sys.stdout
    print("[JARVIS] Starting…")

    try:
        import main as jarvis
        from writing_mode import WritingMode
        from speak import stop_speaking
    except Exception:
        print("[FATAL] Could not load JARVIS core:")
        traceback.print_exc()
        gui.set_status("ERROR")
        gui.run()
        return

    # Writing mode must be created on the GUI thread, as a child window
    def open_writing():
        def create():
            w = getattr(jarvis, "writing_window", None)
            try:
                if w is not None and w.window.winfo_exists():
                    w.window.deiconify(); w.window.lift(); w.window.focus_force()
                    return
            except Exception:
                pass
            jarvis.writing_window = WritingMode(gui.root)
            jarvis.writing_window.window.lift()
        gui.call_soon(create)

    jarvis.open_writing_mode = open_writing
    gui.on_writing = open_writing
    gui.on_stop = stop_speaking
    gui.on_command = lambda text: threading.Thread(
        target=lambda: jarvis.processcommand(text.lower().strip()), daemon=True
    ).start()

    bot = start_bot()

    def shutdown():
        if bot and bot.poll() is None:
            bot.terminate()
    gui.on_close = shutdown

    def voice_worker():
        try:
            jarvis.speak("Initializing Jarvis")
            jarvis.voice_loop()
        except Exception:
            print("[VOICE] Stopped unexpectedly:")
            traceback.print_exc()
            gui.set_status("ERROR")

    threading.Thread(target=voice_worker, daemon=True).start()
    gui.set_status("STANDBY")
    gui.run()
    shutdown()


if __name__ == "__main__":
    if "--bot" in sys.argv:
        run_bot_only()
    else:
        main_app()
