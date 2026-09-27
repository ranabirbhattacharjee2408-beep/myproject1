"""Small manual Gemini smoke test.

This file is intentionally not imported by the desktop app. Keep credentials
in the user's environment rather than storing them in source control.
"""

import os

from google import genai


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit(
        "GEMINI_API_KEY is not configured. "
        "Set it in the environment before running this test."
    )

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is coding?",
)

print(response.text)