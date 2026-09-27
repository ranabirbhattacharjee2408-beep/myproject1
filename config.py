import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_ROOT = _app_root()
DATA_DIR = Path(
    os.getenv("JARVIS_DATA_DIR", str(Path.home() / ".jarvis"))
).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load user configuration from the writable data directory first, then allow
# a development .env beside the source tree as a fallback.
load_dotenv(DATA_DIR / ".env")
load_dotenv(APP_ROOT / ".env", override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")

DB_FILE = DATA_DIR / "jarvis_memory.db"
GOOGLE_CREDENTIALS_FILE = Path(
    os.getenv("GOOGLE_CREDENTIALS_FILE", str(DATA_DIR / "credentials.json"))
).expanduser()
GOOGLE_TOKEN_FILE = Path(
    os.getenv("GOOGLE_TOKEN_FILE", str(DATA_DIR / "token.json"))
).expanduser()
