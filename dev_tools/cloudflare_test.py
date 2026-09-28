import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = "@cf/meta/llama-3.1-8b-instruct"

if not ACCOUNT_ID:
    raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is missing.")

if not API_TOKEN:
    raise RuntimeError("CLOUDFLARE_API_TOKEN is missing.")

url = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/{MODEL}"
)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

data = {
    "messages": [
        {
            "role": "system",
            "content": "You are JARVIS, a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Say hello in one short sentence."
        }
    ]
}

print("=" * 50)
print("       JARVIS - CLOUDFLARE AI TEST")
print("=" * 50)
print("Sending request...")

response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=60
)

print("HTTP Status:", response.status_code)

if not response.ok:
    print("CLOUDFLARE ERROR:")
    print(response.text)
    raise SystemExit(1)

result = response.json()

print("\nSUCCESS!\n")

print("CLOUDFLARE:")
print(result["result"]["response"])

print("\n" + "=" * 50)