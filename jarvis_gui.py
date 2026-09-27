import customtkinter as ctk
from tkinter import Canvas
from datetime import datetime
import random
import math
import pyautogui

# ==========================================================
# THEME
# ==========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BACKGROUND = "#02060D"
CYAN = "#00E5FF"
WHITE = "#F5FFFF"
GRID = "#123C58"


class JarvisGUI:
    def __init__(self):
        self.root = ctk.CTk()
        # ... all your GUI setup ...

    def run(self):
        self.root.mainloop()

    def __init__(self):

        self.root = ctk.CTk()

        self.root.title("JARVIS MK-II")

        self.width = 1600
        self.height = 900

        self.root.geometry(f"{self.width}x{self.height}")

        self.root.configure(fg_color=BACKGROUND)

        self.root.minsize(1400, 800)

        # Uncomment for borderless mode
        # self.root.overrideredirect(True)

        self.create_canvas()

        self.create_background()

        self.create_header()
        self.create_canvas()

        self.create_background()

        self.create_header()

        self.create_ai_core()

    # ======================================================

    def create_canvas(self):

        self.canvas = Canvas(
            self.root,
            bg=BACKGROUND,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)

    # ======================================================

    def create_background(self):

        self.draw_grid()

        self.stars = []

        for i in range(250):

            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            size = random.randint(1, 2)

            star = self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill=CYAN,
                outline=""
            )

            speed = random.uniform(0.2, 1.2)

            self.stars.append([star, speed])

    # ======================================================

    def draw_grid(self):

        for x in range(0, self.width, 60):

            self.canvas.create_line(
                x,
                0,
                x,
                self.height,
                fill=GRID
            )

        for y in range(0, self.height, 60):

            self.canvas.create_line(
                0,
                y,
                self.width,
                y,
                fill=GRID
            )

    # ======================================================

    def create_header(self):

        self.canvas.create_text(
            30,
            35,
            text="J A R V I S",
            fill=CYAN,
            font=("Arial", 30, "bold"),
            anchor="w"
        )

        self.clock_text = self.canvas.create_text(
            1570,
            35,
            text="00:00:00",
            fill=WHITE,
            font=("Consolas", 18),
            anchor="e"
        )

    # ======================================================
    # AI CORE
    # ======================================================
    def create_ai_core(self):

        self.cx = self.width // 2
        self.cy = self.height // 2 + 20

        self.angle = 0

    # ---------------------------
    # Glow Ring
    # ---------------------------

        self.glow_outer = self.canvas.create_oval(
        self.cx-170,
        self.cy-170,
        self.cx+170,
        self.cy+170,
        outline="#003344",
        width=10
    )

    # ---------------------------
    # Outer Rotating Arcs
    # ---------------------------

        self.outer_arcs = []

        for i in range(8):
         arc = self.canvas.create_arc(
         self.cx-160,
         self.cy-160,
         self.cx+160,
         self.cy+160,
            start=i*45,
            extent=20,
            style="arc",
            outline="#00E5FF",
            width=3
          )

        self.outer_arcs.append(arc)

    # ---------------------------
    # Middle Rotating Arcs
    # ---------------------------

        self.middle_arcs = []

        for i in range(12):

         arc = self.canvas.create_arc(
            self.cx-120,
            self.cy-120,
            self.cx+120,
            self.cy+120,
            start=i*30,
            extent=12,
            style="arc",
            outline="#00BFFF",
            width=2
        )

        self.middle_arcs.append(arc)

    # ---------------------------
    # Orbiting Nodes
    # ---------------------------

        self.nodes = []

        for i in range(10):

         node = self.canvas.create_oval(
            0,
            0,
            8,
            8,
            fill="#00FFFF",
            outline=""
        )

        self.nodes.append(node)

    # ---------------------------
    # Electric Arcs
    # ---------------------------

        self.energy_arcs = []

        for i in range(6):

         arc = self.canvas.create_arc(
            self.cx-145,
            self.cy-145,
            self.cx+145,
            self.cy+145,
            start=i*60,
            extent=15,
            style="arc",
            outline="#66FFFF",
            width=4
        )

        self.energy_arcs.append(arc)

    # ---------------------------
    # CENTER AI CORE
    # ---------------------------

        self.core = self.canvas.create_oval(
        self.cx-28,
        self.cy-28,
        self.cx+28,
        self.cy+28,
        fill="#00D9FF",
        outline=""
    )
    # ======================================================
# AI CORE
# ======================================================


def animate_ai_core(self):

    self.angle += 2

    # -------------------------
    # Rotating outer ring
    # -------------------------

    for i,arc in enumerate(self.outer_arcs):

        self.canvas.itemconfig(
            arc,
            start=self.angle+i*45
        )

    # -------------------------
    # Counter rotating ring
    # -------------------------

    for i,arc in enumerate(self.middle_arcs):

        self.canvas.itemconfig(
            arc,
            start=-self.angle+i*30
        )

    # -------------------------
    # Orbiting Nodes
    # -------------------------

    radius=145

    for i,node in enumerate(self.nodes):

        angle=math.radians(self.angle*2+i*36)

        x=self.cx+math.cos(angle)*radius

        y=self.cy+math.sin(angle)*radius

        self.canvas.coords(
            node,
            x-4,
            y-4,
            x+4,
            y+4
        )

    # -------------------------
    # Electric Arcs
    # -------------------------

    for i,arc in enumerate(self.energy_arcs):

        self.canvas.itemconfig(
            arc,
            start=self.angle*3+i*60
        )

    # -------------------------
    # Pulsing Glow
    # -------------------------

    pulse=math.sin(math.radians(self.angle))*10

    self.canvas.coords(

        self.glow_outer,

        self.cx-170-pulse,

        self.cy-170-pulse,

        self.cx+170+pulse,

        self.cy+170+pulse

    )

    self.root.after(
        16,
        self.animate_ai_core
    )

def update_clock(self):

        now = datetime.now().strftime("%H:%M:%S")

        self.canvas.itemconfig(
            self.clock_text,
            text=now
        )

        self.root.after(
            1000,
            self.update_clock
        )

    # ======================================================

def animate_background(self):

        for star, speed in self.stars:

            self.canvas.move(
                star,
                0,
                speed
            )

            x1, y1, x2, y2 = self.canvas.coords(star)

            if y1 > self.height:

                x = random.randint(0, self.width)

                self.canvas.coords(
                    star,
                    x,
                    0,
                    x + 2,
                    2
                )

        self.root.after(
            30,
            self.animate_background
        )
# ======================================================
# AI CORE ANIMATION
# ======================================================

def animate_ai_core(self):

    self.angle += 3

    pulse = math.sin(math.radians(self.angle)) * 8

    # Outer Ring
    self.canvas.coords(

        self.outer_ring,

        self.cx - 160 - pulse,
        self.cy - 160 - pulse,
        self.cx + 160 + pulse,
        self.cy + 160 + pulse
    )

    # Middle Ring
    self.canvas.coords(

        self.middle_ring,

        self.cx - 110 + pulse/2,
        self.cy - 110 + pulse/2,
        self.cx + 110 - pulse/2,
        self.cy + 110 - pulse/2
    )

    # Glow Ring
    self.canvas.coords(

        self.glow_outer,

        self.cx - 170 - pulse,
        self.cy - 170 - pulse,
        self.cx + 170 + pulse,
        self.cy + 170 + pulse
    )

    self.root.after(
        30,
        self.animate_ai_core
    )

    # ======================================================

def run(self):

    self.update_clock()

    self.animate_background()

    self.animate_ai_core()

    self.root.mainloop()

if __name__ == "__main__":

    app = JarvisGUI()
    
    app.run()
    run()