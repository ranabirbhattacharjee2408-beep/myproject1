"""JARVIS main window (replaces the old, unfinished jarvis_gui.py).

Thread-safe: other threads may call log(), set_status() and call_soon().
Everything that touches Tk runs on the main thread via an internal queue.
"""
import math
import os
import queue
import random
import sys
from datetime import datetime
import tkinter as tk

import customtkinter as ctk

BACKGROUND = "#02060D"
PANEL = "#071521"
CYAN = "#00E5FF"
WHITE = "#F5FFFF"
GRID = "#0B2A40"

STATUS_COLORS = {
    "STARTING": "#FFC857",
    "STANDBY": CYAN,
    "LISTENING": "#4DFF88",
    "THINKING": "#FFC857",
    "SPEAKING": "#B388FF",
}


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


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

        self.on_command = None   # callback(text)
        self.on_writing = None   # callback()
        self.on_stop = None      # callback()
        self.on_close = None     # callback()

        self.angle = 0
        self.status = "STARTING"
        self._q = queue.Queue()

        self._build_layout()
        self._build_stars()
        self._build_core()
        self.root.protocol("WM_DELETE_WINDOW", self._closing)
        self.root.after(33, self._tick)

    # ------------------------------------------------------------------
    # public, thread-safe API
    # ------------------------------------------------------------------
    def log(self, text):
        self._q.put(("log", text))

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

    def _build_layout(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self._draw_grid())

        side = ctk.CTkFrame(self.root, width=440, fg_color=PANEL, corner_radius=0)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)
        side.grid_rowconfigure(1, weight=1)
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            side, text="CONSOLE", text_color=CYAN,
            font=("Consolas", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

        self.console = ctk.CTkTextbox(
            side, fg_color=BACKGROUND, text_color=WHITE,
            font=("Consolas", 12), wrap="word",
        )
        self.console.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        self.console.configure(state="disabled")

        row = ctk.CTkFrame(side, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=12, pady=6)
        row.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            row, placeholder_text="Type a command and press Enter…"
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self._send())
        ctk.CTkButton(row, text="Send", width=64, command=self._send).grid(
            row=0, column=1
        )

        btns = ctk.CTkFrame(side, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 16))
        btns.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            btns, text="Writing Mode",
            command=lambda: self.on_writing and self.on_writing(),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            btns, text="Stop Voice", fg_color="#7A1F2B", hover_color="#A32A3B",
            command=lambda: self.on_stop and self.on_stop(),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._append(f"> {text}")
        if self.on_command:
            self.on_command(text)

    # ------------------------------------------------------------------
    # canvas scene
    # ------------------------------------------------------------------
    def _size(self):
        return max(self.canvas.winfo_width(), 400), max(self.canvas.winfo_height(), 300)

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

    def _build_core(self):
        c = self.canvas
        self.title_item = c.create_text(
            30, 35, text="J A R V I S", fill=CYAN,
            font=("Arial", 28, "bold"), anchor="w",
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
            0, 0, text="STARTING", fill=CYAN, font=("Consolas", 16, "bold")
        )

    # ------------------------------------------------------------------
    # main-thread tick: queue drain + animation
    # ------------------------------------------------------------------
    def _tick(self):
        self._drain()
        self._animate()
        self.root.after(33, self._tick)

    def _drain(self):
        for _ in range(200):
            try:
                kind, payload = self._q.get_nowait()
            except queue.Empty:
                return
            try:
                if kind == "log":
                    self._append(payload)
                elif kind == "status":
                    self.status = payload
                elif kind == "call":
                    payload()
            except Exception as error:  # never kill the UI loop
                self._append(f"[GUI ERROR] {error}")

    def _append(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text + "\n")
        if int(self.console.index("end-1c").split(".")[0]) > 1200:
            self.console.delete("1.0", "200.0")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _animate(self):
        c = self.canvas
        w, h = self._size()
        cx, cy = w // 2, h // 2 + 10
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

        for star in self.stars:
            item, x, y, s, v = star
            y += v
            if y > h:
                y, x = 0, random.randint(0, w)
            star[1], star[2] = x, y
            c.coords(item, x, y, x + s, y + s)

    def _closing(self):
        try:
            if self.on_close:
                self.on_close()
        finally:
            self.root.destroy()
