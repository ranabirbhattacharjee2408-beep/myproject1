import customtkinter as ctk
from tkinter import Canvas
import random

# ==========================================================
# THEME
# ==========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BACKGROUND = "#02060D"
CYAN = "#00E5FF"
WHITE = "#F5FFFF"


class JarvisGUI:

    def __init__(self):

        self.root = ctk.CTk()

        self.root.title("JARVIS MK-II")

        self.root.geometry("1600x900")

        self.root.configure(fg_color=BACKGROUND)

        self.root.minsize(1400, 800)

        self.width = 1600
        self.height = 900

        self.create_canvas()
        self.create_background()
        self.create_header()

    # ============================================
    # CANVAS
    # ============================================

    def create_canvas(self):

        self.canvas = Canvas(
            self.root,
            bg=BACKGROUND,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)

    # ============================================
    # BACKGROUND
    # ============================================

    def create_background(self):

        self.particles = []

        for i in range(120):

            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            s = random.randint(1, 3)

            dot = self.canvas.create_oval(
                x,
                y,
                x + s,
                y + s,
                fill=CYAN,
                outline=""
            )

            speed = random.uniform(0.5, 1.5)

            self.particles.append([dot, speed])

    # ============================================
    # HEADER
    # ============================================

    def create_header(self):

        self.canvas.create_text(
            40,
            40,
            text="J A R V I S",
            fill=CYAN,
            font=("Arial", 28, "bold"),
            anchor="w"
        )

        self.clock = self.canvas.create_text(
            1550,
            40,
            text="00:00:00",
            fill=WHITE,
            anchor="e",
            font=("Arial", 18)
        )

    # ============================================
    # RUN
    # ============================================

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = JarvisGUI()

    app.run()
        # ============================================
    # BACKGROUND
    # ============================================

    def create_background(self):

        self.stars = []

        self.particles = []

        # Small Stars
        for i in range(250):

            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            s = random.randint(1, 2)

            star = self.canvas.create_oval(
                x,
                y,
                x+s,
                y+s,
                fill="#7FEFFF",
                outline=""
            )

            speed = random.uniform(0.3,1.2)

            self.stars.append([star,speed])

        # Large Particles
        for i in range(40):

            x = random.randint(0,self.width)
            y = random.randint(0,self.height)

            size = random.randint(3,5)

            particle = self.canvas.create_oval(
                x,
                y,
                x+size,
                y+size,
                fill=CYAN,
                outline=""
            )

            speed = random.uniform(1.2,2.5)

            self.particles.append([particle,speed])

        self.draw_grid()
        # ============================================
    # HUD GRID
    # ============================================

    def draw_grid(self):

     self.grid_lines = []

     for x in range(0, self.width, 60):

        line = self.canvas.create_line(
            x,
            0,
            x,
            self.height,
            fill="#1A567A",
            width=1
        )

        self.grid_lines.append(line)

     for y in range(0, self.height, 60):

        line = self.canvas.create_line(
            0,
            y,
            self.width,
            y,
            fill="#1A567A",
            width=1
        )

        self.grid_lines.append(line)
        # ============================================
    # ANIMATE BACKGROUND
    # ============================================

    def animate_background(self):

        # Small stars
        for star,speed in self.stars:

            self.canvas.move(
                star,
                0,
                speed
            )

            x1,y1,x2,y2=self.canvas.coords(star)

            if y1>self.height:

                x=random.randint(0,self.width)

                self.canvas.coords(
                    star,
                    x,
                    0,
                    x+2,
                    2
                )

        # Large particles
        for p,speed in self.particles:

            self.canvas.move(
                p,
                0,
                speed
            )

            x1,y1,x2,y2=self.canvas.coords(p)

            if y1>self.height:

                x=random.randint(0,self.width)

                size=random.randint(3,5)

                self.canvas.coords(
                    p,
                    x,
                    0,
                    x+size,
                    size
                )

        self.root.after(
            30,
            self.animate_background
        )
    def run(self):

        self.animate_background()

        self.root.mainloop()
        
        draw_grid()