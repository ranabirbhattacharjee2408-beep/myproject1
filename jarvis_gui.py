"""JARVIS main window — a full-screen HUD, no console/log panel.

Thread-safe: other threads may call chat(), set_status() and call_soon().
Everything that touches Tk runs on the main thread via an internal queue.
Raw processing lines are never shown here; only real exchanges (chat())
appear, as large captions that fade after a few seconds.
"""
import math
import os
import queue
import random
import sys
import time
from datetime import datetime
import tkinter as tk

import customtkinter as ctk

BACKGROUND = "#02060D"
PANEL = "#0A1A28"
CYAN = "#00E5FF"
WHITE = "#F5FFFF"
GRID = "#0B2A40"
ERROR_COLOR = "#FF5C5C"

STATUS_COLORS = {
    "STARTING": "#FFC857",
    "STANDBY": CYAN,
    "LISTENING": "#4DFF88",
    "THINKING": "#FFC857",
    "SPEAKING": "#B388FF",
    "ERROR": ERROR_COLOR,
}

CAPTION_HOLD = 5.0   # seconds fully visible
CAPTION_FADE = 2.0   # seconds fading out


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def _mix(c1, c2, t):
    """Blend two '#rrggbb' colors; t=0 -> c1, t=1 -> c2."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class IconButton(ctk.CTkButton):
    """Small round icon toggle, e.g. mic / speaker / writing mode."""

    def __init__(self, master, icon_on, icon_off, on_toggle, start_on=True, **kw):
        self.icon_on, self.icon_off = icon_on, icon_off
        self.state_on = start_on
        self.on_toggle = on_toggle
        super().__init__(
            master, text=icon_on if start_on else icon_off,
            width=44, height=44, corner_radius=22,
            fg_color=PANEL, hover_color="#123247",
            font=("Segoe UI Emoji", 18),
            command=self._clicked, **kw,
        )

    def _clicked(self):
        self.state_on = not self.state_on
        self.configure(text=self.icon_on if self.state_on else self.icon_off)
        if self.on_toggle:
            self.on_toggle(self.state_on)


class JarvisGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("JARVIS")
        self.root.geometry("1280x760")
        self.root.minsize(1000, 620)
        self.root.configure(fg_color=BACKGROUND)
        self.root.after(300, self._set_icon)

        self.on_command = None       # callback(text)
        self.on_writing = None       # callback()
        self.on_stop = None          # callback()
        self.on_close = None         # callback()
        self.on_voice_toggle = None  # callback(bool)  speak replies aloud
        self.on_mic_toggle = None    # callback(bool)  listen to microphone

        self.angle = 0
        self.status = "STARTING"
        self._q = queue.Queue()
        self._caption_user = {"text": "", "born": 0.0}
        self._caption_jarvis = {"text": "", "born": 0.0, "error": False}

        self._build_canvas()
        self._build_core()
        self._build_toolbar()
        self._build_input_bar()
        self._build_stars()
        self.root.protocol("WM_DELETE_WINDOW", self._closing)
        self.root.after(33, self._tick)

    # ------------------------------------------------------------------
    # public, thread-safe API
    # ------------------------------------------------------------------
    def chat(self, role, text, error=False):
        """Show one exchange as a fading caption. role: 'You' or 'JARVIS'."""
        self._q.put(("chat", (role, text, error)))

    def log(self, text):
        """Kept for compatibility; intentionally invisible (no console)."""
        pass

    def set_status(self, status):
        self._q.put(("status", status.upper()))

    def call_soon(self, fn):
        self._q.put(("call", fn))

    def run(self):
        self.root.mainloop()

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def _set_icon(self):
        try:
            ico = resource_path("JARVIS.ico")
            if sys.platform == "win32" and os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_grid())

    def _draw_grid(self):
        w, h = self._size()
        self.canvas.delete("grid")
        for x in range(0, w, 60):
            self.canvas.create_line(x, 0, x, h, fill=GRID, tags="grid")
        for y in range(0, h, 60):
            self.canvas.create_line(0, y, w, y, fill=GRID, tags="grid")
        self.canvas.tag_lower("grid")

    def _build_stars(self):
        self.stars = []
        for _ in range(160):
            x, y = random.randint(0, 1600), random.randint(0, 900)
            s = random.randint(1, 2)
            item = self.canvas.create_oval(x, y, x + s, y + s, fill=CYAN, outline="")
            self.stars.append([item, x, y, s, random.uniform(0.3, 1.4)])
        self.canvas.tag_lower("all")
        for star in self.stars:
            self.canvas.tag_raise(star[0])

    def _build_core(self):
        c = self.canvas
        self.title_item = c.create_text(
            30, 35, text="J A R V I S", fill=CYAN,
            font=("Arial", 26, "bold"), anchor="w",
        )
        self.clock_item = c.create_text(
            0, 35, text="", fill=WHITE, font=("Consolas", 18), anchor="e"
        )
        self.glow = c.create_oval(0, 0, 1, 1, outline="#003344", width=10)
        self.outer_arcs = [
            c.create_arc(0, 0, 1, 1, start=i * 45, extent=20, style="arc",
                         outline=CYAN, width=3) for i in range(8)
        ]
        self.middle_arcs = [
            c.create_arc(0, 0, 1, 1, start=i * 30, extent=12, style="arc",
                         outline="#00BFFF", width=2) for i in range(12)
        ]
        self.nodes = [
            c.create_oval(0, 0, 8, 8, fill="#00FFFF", outline="") for _ in range(10)
        ]
        self.core = c.create_oval(0, 0, 1, 1, fill="#00D9FF", outline="")
        self.status_item = c.create_text(
            0, 0, text="STARTING", fill=CYAN, font=("Consolas", 15, "bold")
        )
        # Captions: what was said, shown large and center, fading after a
        # few seconds. This replaces the old scrolling console entirely.
        self.caption_user_item = c.create_text(
            0, 0, text="", fill=CYAN, font=("Arial", 16), anchor="s"
        )
        self.caption_jarvis_item = c.create_text(
            0, 0, text="", fill=WHITE, font=("Arial", 22, "bold"),
            anchor="s", width=900,
        )

    def _build_toolbar(self):
        self.toolbar = ctk.CTkFrame(self.root, fg_color="transparent")
        self.toolbar.place(relx=1.0, y=24, x=-24, anchor="ne")
        self.mic_btn = IconButton(
            self.toolbar, "🎤", "🚫",
            lambda on: self.on_mic_toggle and self.on_mic_toggle(on),
        )
        self.mic_btn.grid(row=0, column=0, padx=5)
        self.voice_btn = IconButton(
            self.toolbar, "🔊", "🔇",
            lambda on: self.on_voice_toggle and self.on_voice_toggle(on),
        )
        self.voice_btn.grid(row=0, column=1, padx=5)
        ctk.CTkButton(
            self.toolbar, text="✎", width=44, height=44, corner_radius=22,
            fg_color=PANEL, hover_color="#123247", font=("Segoe UI", 16),
            command=lambda: self.on_writing and self.on_writing(),
        ).grid(row=0, column=2, padx=5)
        ctk.CTkButton(
            self.toolbar, text="⏹", width=44, height=44, corner_radius=22,
            fg_color="#3A1420", hover_color="#5C1E2E", font=("Segoe UI", 16),
            command=lambda: self.on_stop and self.on_stop(),
        ).grid(row=0, column=3, padx=5)

    def _build_input_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color=PANEL, corner_radius=22, height=52)
        bar.place(relx=0.5, rely=1.0, y=-26, anchor="s", relwidth=0.5)
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            bar, placeholder_text="Type a command…", border_width=0,
            fg_color="transparent", height=44, font=("Arial", 14),
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(18, 6), pady=4)
        self.entry.bind("<Return>", lambda e: self._send())
        ctk.CTkButton(
            bar, text="➤", width=40, height=40, corner_radius=20,
            command=self._send,
        ).grid(row=0, column=1, padx=(0, 6), pady=4)

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.chat("You", text)
        if self.on_command:
            self.on_command(text)

    # ------------------------------------------------------------------
    # main-thread tick: queue drain + animation
    # ------------------------------------------------------------------
    def _size(self):
        return max(self.canvas.winfo_width(), 400), max(self.canvas.winfo_height(), 300)

    def _tick(self):
        self._drain()
        self._animate()
        self.root.after(33, self._tick)

    def _drain(self):
        now = time.time()
        for _ in range(200):
            try:
                kind, payload = self._q.get_nowait()
            except queue.Empty:
                return
            try:
                if kind == "status":
                    self.status = payload
                elif kind == "call":
                    payload()
                elif kind == "chat":
                    role, text, error = payload
                    if role.lower().startswith("you"):
                        self._caption_user = {"text": text, "born": now}
                    else:
                        self._caption_jarvis = {"text": text, "born": now, "error": error}
            except Exception:
                pass  # never let a bad payload kill the UI loop

    def _animate(self):
        c = self.canvas
        w, h = self._size()
        cx, cy = w // 2, h // 2 - 20
        speed = {"STARTING": 2, "STANDBY": 1.5, "LISTENING": 3,
                 "THINKING": 6, "SPEAKING": 4}.get(self.status, 2)
        self.angle = (self.angle + speed) % 360
        pulse = math.sin(math.radians(self.angle * 2)) * 8
        color = STATUS_COLORS.get(self.status, CYAN)

        c.coords(self.title_item, 30, 35)
        c.coords(self.clock_item, w - 30, 35)
        c.itemconfigure(self.clock_item, text=datetime.now().strftime("%H:%M:%S"))

        r = 170 + pulse
        c.coords(self.glow, cx - r, cy - r, cx + r, cy + r)
        for i, arc in enumerate(self.outer_arcs):
            c.coords(arc, cx - 160, cy - 160, cx + 160, cy + 160)
            c.itemconfigure(arc, start=i * 45 + self.angle, outline=color)
        for i, arc in enumerate(self.middle_arcs):
            c.coords(arc, cx - 120, cy - 120, cx + 120, cy + 120)
            c.itemconfigure(arc, start=i * 30 - self.angle * 1.5)
        for i, node in enumerate(self.nodes):
            a = math.radians(self.angle * 2 + i * 36)
            x, y = cx + math.cos(a) * 90, cy + math.sin(a) * 90
            c.coords(node, x - 4, y - 4, x + 4, y + 4)
        cr = 28 + pulse / 2
        c.coords(self.core, cx - cr, cy - cr, cx + cr, cy + cr)
        c.itemconfigure(self.core, fill=color)
        c.coords(self.status_item, cx, cy + 215)
        c.itemconfigure(self.status_item, text=self.status, fill=color)

        self._draw_caption(
            self.caption_jarvis_item, self._caption_jarvis, cx, h - 110,
            ERROR_COLOR if self._caption_jarvis.get("error") else WHITE,
        )
        self._draw_caption(self.caption_user_item, self._caption_user, cx, h - 150, CYAN)

        for star in self.stars:
            item, x, y, s, v = star
            y += v
            if y > h:
                y, x = 0, random.randint(0, w)
            star[1], star[2] = x, y
            c.coords(item, x, y, x + s, y + s)

    def _draw_caption(self, item, state, cx, y, base_color):
        c = self.canvas
        text = state.get("text", "")
        if not text:
            c.itemconfigure(item, text="")
            return
        age = time.time() - state.get("born", 0)
        if age >= CAPTION_HOLD + CAPTION_FADE:
            state["text"] = ""
            c.itemconfigure(item, text="")
            return
        fade_t = max(0.0, (age - CAPTION_HOLD) / CAPTION_FADE) if age > CAPTION_HOLD else 0.0
        c.coords(item, cx, y)
        c.itemconfigure(item, text=text, fill=_mix(base_color, BACKGROUND, fade_t))

    def _closing(self):
        try:
            if self.on_close:
                self.on_close()
        finally:
            self.root.destroy()
