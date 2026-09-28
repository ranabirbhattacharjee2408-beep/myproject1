import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logger import log_info, log_error

log_info("Jarvis started.")

try:
    x = 10 / 0
except Exception as e:
    log_error("Math Test", e)

print("Finished.")