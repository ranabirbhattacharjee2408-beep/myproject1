import socket

BOT_HOST = "127.0.0.1"
BOT_PORT = 8765


def send_bot_state(state, message=None):
    try:
        if message:
            data = f"{state}|{message}"
        else:
            data = state

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.sendto(
            data.encode("utf-8"),
            (BOT_HOST, BOT_PORT)
        )

        sock.close()

        print(f"[BOT CONTROL] Sent: {data}")

    except Exception as e:
        print("[BOT CONTROL] Robot unavailable:", e)


def bot_idle():
    send_bot_state("idle")


def bot_listening():
    send_bot_state("listening")


def bot_thinking():
    send_bot_state("thinking")


def bot_speaking():
    send_bot_state("speaking")


def bot_happy():
    send_bot_state("happy")


def bot_surprised():
    send_bot_state("surprised")


def bot_sleepy():
    send_bot_state("sleepy")