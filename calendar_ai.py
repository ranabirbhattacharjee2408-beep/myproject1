import re
import dateparser

def parse_calendar_command(command):
    """
    Returns:
        (title, datetime) or (None, None)
    """

    command = command.lower()

    prefixes = [
        "schedule",
        "add",
        "create",
        "remind me to"
    ]

    text = command

    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].strip()

    dt = dateparser.parse(
        text,
        settings={
            "PREFER_DATES_FROM": "future"
        }
    )

    if dt is None:
        return None, None

    # Remove common time words from title
    title = re.sub(
        r"(today|tomorrow|next.*|at.*|\d.*)",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    return title, dt