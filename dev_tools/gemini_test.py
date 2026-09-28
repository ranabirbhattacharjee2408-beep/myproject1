import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    raise SystemExit

print("🔑 Gemini API key found.")
print("🤖 Testing Gemini...")

try:
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say exactly: Gemini is working."
    )

    print("\n✅ SUCCESS!")
    print("Gemini response:", response.text)

except Exception as e:
    print("\n❌ Gemini test failed:")
    print(type(e).__name__, e)