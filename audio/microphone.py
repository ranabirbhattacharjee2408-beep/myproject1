import speech_recognition as sr

# Create ONE recognizer
recognizer = sr.Recognizer()

# Create ONE microphone
microphone = sr.Microphone(device_index=1)


def listen(timeout=5, phrase_time_limit=5):
    """
    Listen once and return recognized text.
    Returns None if nothing is understood.
    """

    try:
        with microphone as source:

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