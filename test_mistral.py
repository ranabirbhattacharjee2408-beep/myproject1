import os
import time
from mistralai.client import Mistral


# ============================================================
# MISTRAL API TEST FOR JARVIS
# ============================================================

api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    print("ERROR: MISTRAL_API_KEY is not set.")
    print()
    print("Set it in PowerShell with:")
    print('$env:MISTRAL_API_KEY="YOUR_API_KEY"')
    exit()


# Create Mistral client
client = Mistral(api_key=api_key)


# Exact model shown in your Mistral Limits page
MODEL = "ministral-8b-2512"


def test_mistral():
    print("=" * 50)
    print("        JARVIS - MISTRAL AI TEST")
    print("=" * 50)
    print()
    print(f"Model: {MODEL}")
    print("Sending request...")
    print()

    try:
        response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Introduce yourself to JARVIS "
                        "in one short sentence."
                    )
                }
            ]
        )

        print("SUCCESS!")
        print()
        print("MISTRAL:")
        print(response.choices[0].message.content)
        print()
        print("=" * 50)

    except Exception as e:
        print("MISTRAL ERROR:")
        print(e)
        print()
        print("=" * 50)


# Give the previous request/rate limit a little time to clear
print("Waiting 3 seconds before testing...")
time.sleep(3)

test_mistral()