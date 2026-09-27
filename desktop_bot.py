import tkinter as tk
from PIL import Image, ImageTk
import math
import os
import random
import socket
import sys

# ============================================================
# JARVIS DESKTOP COMPANION
# ============================================================

WINDOW_SIZE = 300
RIGHT_MARGIN = 20
BOTTOM_MARGIN = 40

TRANSPARENT = "#010101"
CYAN = "#00E5FF"
BLUE = "#009DFF"
WHITE = "#F5FFFF"
PANEL = "#071521"

BOT_PORT = 8765


# ============================================================
# RESOURCE PATH
# Works in normal Python AND PyInstaller EXE
# ============================================================
def resource_path(relative_path):
    """
    Get the correct path for resources in both development
    and PyInstaller packaged modes.
    """
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_dir, relative_path)
IMAGE_PATH = resource_path("bot.png")
ASSETS_DIR = resource_path("bot_assets")


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title("JARVIS")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg=TRANSPARENT)

try:
    root.wm_attributes("-transparentcolor", TRANSPARENT)
except Exception:
    pass


# ============================================================
# DESKTOP POSITION
# ============================================================

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

start_x = screen_width - WINDOW_SIZE - RIGHT_MARGIN
start_y = screen_height - WINDOW_SIZE - BOTTOM_MARGIN

root.geometry(
    f"{WINDOW_SIZE}x{WINDOW_SIZE}+{start_x}+{start_y}"
)


# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    root,
    width=WINDOW_SIZE,
    height=WINDOW_SIZE,
    bg=TRANSPARENT,
    highlightthickness=0,
    bd=0
)

canvas.pack()


# ============================================================
# CHECK ROBOT IMAGE
# ============================================================

if not os.path.exists(IMAGE_PATH):

    print()
    print("==========================================")
    print("ERROR: ROBOT IMAGE NOT FOUND")
    print("==========================================")
    print()
    print("Expected:")
    print(IMAGE_PATH)
    print()

    root.destroy()
    raise SystemExit


# ============================================================
# LOAD ROBOT
# ============================================================

original_image = Image.open(
    IMAGE_PATH
).convert("RGBA")


# ============================================================
# STATE
# ============================================================

state = "idle"
animation_time = 0.0

robot_photo = None
robot = None

bubble_box = None
bubble_text = None
state_label = None

mouth = None

listening_ring_1 = None
listening_ring_2 = None

thinking_dot = None

emotion_effects = []


# ============================================================
# RANDOM ANIMATION VARIABLES
# ============================================================

blink_timer = random.uniform(2.5, 5.0)
blink_until = 0
wave_offset = 0


# ============================================================
# ROBOT IMAGE CREATION
# ============================================================

def create_robot(scale=1.0, angle=0):

    image = original_image.copy()

    max_size = int(
        WINDOW_SIZE * 0.72 * scale
    )

    image.thumbnail(
        (max_size, max_size),
        Image.Resampling.LANCZOS
    )

    if angle != 0:

        image = image.rotate(
            angle,
            Image.Resampling.BICUBIC,
            expand=True
        )

    return ImageTk.PhotoImage(image)


# ============================================================
# INITIAL ROBOT
# ============================================================

robot_photo = create_robot()

robot = canvas.create_image(
    WINDOW_SIZE // 2,
    WINDOW_SIZE // 2 + 30,
    image=robot_photo
)


# ============================================================
# SPEECH BUBBLE
# ============================================================

def hide_bubble():

    global bubble_box
    global bubble_text

    if bubble_box is not None:

        canvas.delete(bubble_box)
        bubble_box = None

    if bubble_text is not None:

        canvas.delete(bubble_text)
        bubble_text = None


def show_bubble(text):

    global bubble_box
    global bubble_text

    hide_bubble()

    bubble_box = canvas.create_rectangle(
        10,
        8,
        WINDOW_SIZE - 10,
        67,
        fill=PANEL,
        outline=CYAN,
        width=2
    )

    bubble_text = canvas.create_text(
        WINDOW_SIZE // 2,
        37,
        text=text,
        fill=WHITE,
        font=("Segoe UI", 10, "bold"),
        width=WINDOW_SIZE - 30,
        justify="center"
    )


# ============================================================
# STATE LABEL
# ============================================================

def update_state_label():

    global state_label

    if state_label is not None:

        canvas.delete(state_label)
        state_label = None

    labels = {

        "idle": "",

        "listening":
            "● LISTENING",

        "thinking":
            "● THINKING",

        "speaking":
            "● SPEAKING",

        "happy":
            "★ HAPPY",

        "surprised":
            "! SURPRISED",

        "sleepy":
            "Z Z Z"
    }

    text = labels.get(state, "")

    if not text:
        return

    state_label = canvas.create_text(
        WINDOW_SIZE // 2,
        WINDOW_SIZE - 13,
        text=text,
        fill=CYAN,
        font=("Segoe UI", 9, "bold")
    )


# ============================================================
# SET STATE
# ============================================================

def set_state(new_state, message=None):

    global state

    state = new_state

    update_state_label()

    if message:

        show_bubble(message)

    elif state == "idle":

        hide_bubble()

    elif state == "listening":

        show_bubble("I'm listening... 🎙️")

    elif state == "thinking":

        show_bubble("Hmm... let me think 🤔")

    elif state == "speaking":

        show_bubble("I'm speaking! 🗣️")

    elif state == "happy":

        show_bubble("Done! 🎉")

    elif state == "surprised":

        show_bubble("WOW! 😮")

    elif state == "sleepy":

        show_bubble("Zzz... 😴")


# ============================================================
# MAIN PROGRAM COMMUNICATION
# ============================================================

bot_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

bot_socket.bind(
    ("127.0.0.1", BOT_PORT)
)

print("[BOT] UDP PORT 8765 READY")

bot_socket.setblocking(False)


def check_bot_commands():

    try:

        while True:

            data, address = bot_socket.recvfrom(4096)

            command = data.decode(
                "utf-8"
            ).strip()

            if not command:
                continue

            print(
                "[BOT] Received:",
                command
            )

            if "|" in command:

                state_name, message = command.split(
                    "|",
                    1
                )

                set_state(
                    state_name.strip(),
                    message.strip()
                )

            else:

                set_state(
                    command.strip()
                )

    except BlockingIOError:
        pass

    except Exception as e:

        print(
            "[BOT COMMUNICATION ERROR]",
            e
        )

    root.after(
        50,
        check_bot_commands
    )


# ============================================================
# REMOVE EFFECTS
# ============================================================

def clear_effects():

    global mouth
    global listening_ring_1
    global listening_ring_2
    global thinking_dot

    if mouth is not None:

        canvas.delete(mouth)
        mouth = None

    if listening_ring_1 is not None:

        canvas.delete(listening_ring_1)
        listening_ring_1 = None

    if listening_ring_2 is not None:

        canvas.delete(listening_ring_2)
        listening_ring_2 = None

    if thinking_dot is not None:

        canvas.delete(thinking_dot)
        thinking_dot = None

    for item in emotion_effects:

        try:
            canvas.delete(item)

        except Exception:
            pass

    emotion_effects.clear()


# ============================================================
# TALKING MOUTH
# ============================================================

def animate_mouth():

    global mouth

    if state != "speaking":

        if mouth is not None:

            canvas.delete(mouth)
            mouth = None

        root.after(
            45,
            animate_mouth
        )

        return

    cx = WINDOW_SIZE // 2
    cy = WINDOW_SIZE // 2 + 58

    amount = abs(
        math.sin(
            animation_time * 15
        )
    )

    height = 5 + amount * 15
    width = 10 + amount * 5

    if mouth is None:

        mouth = canvas.create_oval(
            cx - width,
            cy - height,
            cx + width,
            cy + height,
            fill="#02060D",
            outline=CYAN,
            width=2
        )

    else:

        canvas.coords(
            mouth,
            cx - width,
            cy - height,
            cx + width,
            cy + height
        )

    root.after(
        45,
        animate_mouth
    )


# ============================================================
# LISTENING EFFECT
# ============================================================

def animate_listening():

    global listening_ring_1
    global listening_ring_2

    if state != "listening":

        if listening_ring_1 is not None:

            canvas.delete(listening_ring_1)
            listening_ring_1 = None

        if listening_ring_2 is not None:

            canvas.delete(listening_ring_2)
            listening_ring_2 = None

        root.after(
            50,
            animate_listening
        )

        return

    pulse = (
        abs(
            math.sin(
                animation_time * 4
            )
        )
        * 9
    )

    cx = WINDOW_SIZE // 2
    cy = WINDOW_SIZE // 2 + 30

    r1 = 50 + pulse
    r2 = 60 + pulse * 1.5

    if listening_ring_1 is None:

        listening_ring_1 = canvas.create_oval(
            cx - r1,
            cy - r1,
            cx + r1,
            cy + r1,
            outline=CYAN,
            width=2
        )

    else:

        canvas.coords(
            listening_ring_1,
            cx - r1,
            cy - r1,
            cx + r1,
            cy + r1
        )

    if listening_ring_2 is None:

        listening_ring_2 = canvas.create_oval(
            cx - r2,
            cy - r2,
            cx + r2,
            cy + r2,
            outline=BLUE,
            width=1
        )

    else:

        canvas.coords(
            listening_ring_2,
            cx - r2,
            cy - r2,
            cx + r2,
            cy + r2
        )

    root.after(
        50,
        animate_listening
    )


# ============================================================
# THINKING DOT
# ============================================================

def animate_thinking():

    global thinking_dot

    if state != "thinking":

        if thinking_dot is not None:

            canvas.delete(thinking_dot)
            thinking_dot = None

        root.after(
            200,
            animate_thinking
        )

        return

    phase = int(
        animation_time * 4
    ) % 3

    x = (
        WINDOW_SIZE // 2
        + (phase - 1) * 18
    )

    y = WINDOW_SIZE // 2 - 72

    if thinking_dot is not None:
        canvas.delete(thinking_dot)

    thinking_dot = canvas.create_oval(
        x - 5,
        y - 5,
        x + 5,
        y + 5,
        fill=CYAN,
        outline=""
    )

    root.after(
        180,
        animate_thinking
    )


# ============================================================
# EMOTION EFFECTS
# ============================================================

def animate_emotion():

    if state == "happy":

        if len(emotion_effects) < 6:

            for i in range(6):

                angle = (
                    i / 6
                ) * math.pi * 2

                radius = 80

                x = (
                    WINDOW_SIZE // 2
                    + math.cos(angle)
                    * radius
                )

                y = (
                    WINDOW_SIZE // 2
                    + 20
                    + math.sin(angle)
                    * radius
                )

                item = canvas.create_text(
                    x,
                    y,
                    text="✦",
                    fill=CYAN,
                    font=(
                        "Segoe UI",
                        16,
                        "bold"
                    )
                )

                emotion_effects.append(item)

    else:

        if emotion_effects:

            for item in emotion_effects:

                try:
                    canvas.delete(item)

                except Exception:
                    pass

            emotion_effects.clear()

    root.after(
        200,
        animate_emotion
    )


# ============================================================
# MAIN BODY ANIMATION
# ============================================================

def animate():

    global animation_time
    global robot_photo

    animation_time += 0.12

    x = 0
    y = 0
    angle = 0
    scale = 1.0

    if state == "idle":

        y = math.sin(
            animation_time * 1.5
        ) * 10

        x = math.sin(
            animation_time * 0.8
        ) * 4

        angle = math.sin(
            animation_time * 0.8
        ) * 2.5

        scale = (
            1.0
            + math.sin(
                animation_time * 1.2
            ) * 0.025
        )

    elif state == "listening":

        y = math.sin(
            animation_time * 4
        ) * 8

        x = math.sin(
            animation_time * 2
        ) * 6

        angle = math.sin(
            animation_time * 3
        ) * 3

        scale = (
            1.03
            + math.sin(
                animation_time * 5
            ) * 0.035
        )

    elif state == "thinking":

        y = math.sin(
            animation_time * 1.5
        ) * 6

        x = math.sin(
            animation_time * 2
        ) * 12

        angle = math.sin(
            animation_time * 2
        ) * 5

        scale = 1.02

    elif state == "speaking":

        y = math.sin(
            animation_time * 8
        ) * 10

        x = math.sin(
            animation_time * 5
        ) * 5

        angle = math.sin(
            animation_time * 7
        ) * 3

        scale = (
            1.03
            + abs(
                math.sin(
                    animation_time * 8
                )
            ) * 0.05
        )

    elif state == "happy":

        y = -abs(
            math.sin(
                animation_time * 5
            )
        ) * 22

        x = math.sin(
            animation_time * 6
        ) * 9

        angle = math.sin(
            animation_time * 5
        ) * 8

        scale = (
            1.04
            + abs(
                math.sin(
                    animation_time * 5
                )
            ) * 0.06
        )

    elif state == "surprised":

        y = math.sin(
            animation_time * 12
        ) * 8

        x = math.sin(
            animation_time * 12
        ) * 5

        angle = 0

        scale = (
            1.10
            + math.sin(
                animation_time * 12
            ) * 0.05
        )

    elif state == "sleepy":

        y = math.sin(
            animation_time * 0.7
        ) * 3

        x = math.sin(
            animation_time * 0.5
        ) * 2

        angle = math.sin(
            animation_time * 0.5
        ) * 4

        scale = 0.98

    robot_photo = create_robot(
        scale,
        angle
    )

    canvas.itemconfig(
        robot,
        image=robot_photo
    )

    canvas.coords(
        robot,
        WINDOW_SIZE // 2 + x,
        WINDOW_SIZE // 2 + 30 + y
    )

    root.after(
        30,
        animate
    )


# ============================================================
# THINKING SPEECH
# ============================================================

def thinking_animation():

    if state == "thinking":

        dots = "." * (
            int(
                animation_time * 3
            ) % 4
        )

        show_bubble(
            "Thinking"
            + dots
            + " 🤔"
        )

    root.after(
        400,
        thinking_animation
    )


# ============================================================
# KEYBOARD CONTROLS
# ============================================================

def keyboard(event):

    key = event.keysym.lower()

    if key == "1":
        set_state("idle")

    elif key == "2":
        set_state("listening")

    elif key == "3":
        set_state("thinking")

    elif key == "4":
        set_state(
            "speaking",
            "I am speaking! 🗣️"
        )

    elif key == "5":
        set_state("happy")

    elif key == "6":
        set_state("surprised")

    elif key == "7":
        set_state("sleepy")

    elif key == "0":
        set_state("idle")


root.bind("<Key>", keyboard)
root.focus_force()


# ============================================================
# DRAGGING
# ============================================================

drag_x = 0
drag_y = 0


def start_drag(event):

    global drag_x
    global drag_y

    drag_x = event.x
    drag_y = event.y


def drag(event):

    new_x = (
        root.winfo_x()
        + event.x
        - drag_x
    )

    new_y = (
        root.winfo_y()
        + event.y
        - drag_y
    )

    root.geometry(
        f"+{new_x}+{new_y}"
    )


canvas.bind(
    "<Button-1>",
    start_drag
)

canvas.bind(
    "<B1-Motion>",
    drag
)


# ============================================================
# RIGHT CLICK = CLOSE
# ============================================================

canvas.bind(
    "<Button-3>",
    lambda event: root.destroy()
)


# ============================================================
# START
# ============================================================

print()
print("============================================")
print("           JARVIS DESKTOP BOT")
print("============================================")
print()
print("1 = IDLE")
print("2 = LISTENING")
print("3 = THINKING")
print("4 = SPEAKING")
print("5 = HAPPY")
print("6 = SURPRISED")
print("7 = SLEEPY")
print("0 = IDLE")
print()
print("LEFT CLICK + DRAG = MOVE")
print("RIGHT CLICK = CLOSE")
print()
print("============================================")
print()

animate()
animate_mouth()
animate_listening()
animate_thinking()
animate_emotion()
thinking_animation()
check_bot_commands()

root.mainloop()