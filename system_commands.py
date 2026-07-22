import os

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

    return False