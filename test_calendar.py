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