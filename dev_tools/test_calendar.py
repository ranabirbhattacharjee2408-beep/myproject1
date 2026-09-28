import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta

from calendar_manager import add_event

start = datetime.now() + timedelta(minutes=2)
end = start + timedelta(hours=1)

add_event(
    "Testing Jarvis Calendar",
    start,
    end
)

print("Event Created!")