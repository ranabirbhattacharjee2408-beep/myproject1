import os

import speech_recognition as sr


recognizer = sr.Recognizer()
microphone = None


def _get_microphone():
    global microphone

    if microphone is not None:
        return microphone

    try:
        configured_index = os.getenv("JARVIS_MICROPHONE_INDEX")
        device_index = (
            int(configured_index)
            if configured_index and configured_index.strip()
            else None
        )
        microphone = sr.Microphone(device_index=device_index)
    except Exception as error:
        print(f"Microphone unavailable: {error}")
        microphone = False

    return microphone


def listen(timeout=5, phrase_time_limit=5):
    """
    Listen once and return recognized text.
    Returns None if nothing is understood.
    """

    try:
        source_microphone = _get_microphone()
        if not source_microphone:
            return None

        with source_microphone as source:

            recognizer.adjust_for_ambient_noise(source, duration=0.3)

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = recognizer.recognize_google(audio)

        print("Heard:", text)

        return text.lower()

    except sr.WaitTimeoutError:
        return None

    except sr.UnknownValueError:
        return None

    except sr.RequestError:
        print("Speech Recognition unavailable")
        return None

    except Exception as e:
        print("Microphone Error:", e)
        return None