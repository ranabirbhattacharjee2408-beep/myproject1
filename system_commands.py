import os
import subprocess
from anyio import Path
from httpx import delete

from speak import speak
def create_file(filename, folder="."):
    path = Path(folder) / filename

    if path.exists():
        return f"{filename} already exists."

    path.touch()
    return f"{filename} has been created."
def delete_file(filename, folder="."):
    path = Path(folder) / filename

    if path.exists():
        path.unlink()
        return f"{filename} deleted successfully."

    return "File not found."
def rename_file(old_name, new_name, folder="."):
    old_path = Path(folder) / old_name
    new_path = Path(folder) / new_name

    if not old_path.exists():
        return "File not found."

    old_path.rename(new_path)
    return f"Renamed to {new_name}."
def system_command(command):
    command = command.lower().strip()

    # Shutdown
    if "shutdown" in command or "turn off computer" in command:
        os.system("shutdown /s /t 0")
        return True

    # Restart
    elif "restart" in command or "reboot" in command:
        os.system("shutdown /r /t 0")
        return True

    # Sleep
    elif "sleep" in command:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return True

    # Hibernate
    elif "hibernate" in command:
        os.system("shutdown /h")
        return True

    # Lock
    elif "lock" in command:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return True

    # Log out
    elif "logout" in command or "log out" in command or "sign out" in command:
        os.system("shutdown /l")
        return True

    # Cancel shutdown/restart
    elif "cancel shutdown" in command or "abort shutdown" in command:
        os.system("shutdown /a")
        return True

      
    elif "delete temp files" in command or "clear temp files" in command:
       temp_path = os.environ.get("TEMP", None)
       return True if temp_path and os.path.exists(temp_path) and os.system(f"del /q /f /s {temp_path}\\*") == 0 else False
    elif "delete recycle bin" in command or "empty recycle bin" in command:
        return True if os.system("rd /s /q %systemdrive%\\$Recycle.Bin") == 0 else False    
    elif "delete recent files" in command or "clear recent files" in command:
        recent_path = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent")
        return True if os.path.exists(recent_path) and os.system(f"del /q /f /s {recent_path}\\*") == 0 else False  
    elif "delete prefetch files" in command or "clear prefetch files" in command:
        prefetch_path = os.path.join(os.environ.get("SystemRoot", ""), "Prefetch")
        return True if os.path.exists(prefetch_path) and os.system(f"del /q /f /s {prefetch_path}\\*") == 0 else False
    
    elif "delete" in command or "uninstall" in command:
        global waiting_for_confirmation, pending_action, pending_app
        
        app = command.split(" ", 1)[1].strip()
        pending_action = "uninstall"
        pending_app = app
        waiting_for_confirmation = True
        speak(f"Are you sure you want to uninstall {app}?")
        return True
    
    elif "refresh" in command or "reload" in command:
        os.system("taskkill /f /im explorer.exe && start explorer.exe")
    elif command in ["clear cache", "delete cache", "clear browser cache"]:
        cache_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Cache")
        if os.path.exists(cache_path):
            os.system(f"del /q /f /s {cache_path}\\*")
            speak("Cache cleared.")
            return True
        else:
            speak("Cache folder not found.")
            return False
    elif "close all applications" in command or "close all apps" in command:
        os.system("taskkill /f /fi \"status eq running\"")
        speak("All running applications have been closed.")
        return True

    elif "create file" in command:
        filename = command.split("create file", 1)[1].strip()
        result = create_file(filename)
        speak(result)
        return True
    elif "delete file" in command:
        filename = command.split("delete file", 1)[1].strip()
        result = delete_file(filename)
        speak(result)
        return True
    elif "rename file" in command:
        parts = command.split("rename file", 1)[1].strip().split(" to ")
        if len(parts) == 2:
            old_name, new_name = parts[0].strip(), parts[1].strip()
            result = rename_file(old_name, new_name)
            speak(result)
            return True
        else:
            speak("Please specify the old and new file names.")
            return False