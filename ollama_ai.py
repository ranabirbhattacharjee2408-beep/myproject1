import ollama

MODEL = "llama3.2"


def ask_ollama(prompt):
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a helpful and intelligent "
                        "desktop AI assistant. Answer clearly and naturally."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        print(f"[OLLAMA ERROR] {e}")
        return "Sorry, I could not connect to my  AI."