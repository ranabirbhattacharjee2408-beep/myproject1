import os

app_index = {}

start_menu_paths = [
    os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs"),
    os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu\Programs")
]

for folder in start_menu_paths:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    app_index[name] = os.path.join(root, file)

print(f"Loaded {len(app_index)} applications.")

def open_app(command):
    command = command.lower().strip()

    # Remove command words if present
    for word in ["open", "launch", "start", "run"]:
        if command.startswith(word):
            command = command[len(word):].strip()
            break

    # Prevent empty command from matching everything
    if not command:
        return False

    # Exact match
    if command in app_index:
        os.startfile(app_index[command])
        return True

    # Partial match
    for name, path in app_index.items():
        if command in name:
            os.startfile(path)
            return True

    return False