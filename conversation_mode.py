from speak import speak
from audio.microphone import listen 


def start_conversational():
    import main

    while main.conversation_mode:

        command = listen(timeout=8, phrase_time_limit=8)

        if not command:
            continue

        command = command.lower().strip()

        if command in [
            "go to sleep",
            "exit conversation mode",
            "close conversation mode",
        ]:
            main.conversation_mode = False
            speak("Conversation mode deactivated. Going to standby mode.")
            break

        main.processcommand(command)

    print("Conversation mode ended.")