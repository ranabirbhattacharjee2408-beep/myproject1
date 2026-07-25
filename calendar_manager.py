import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If you change these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None

    # Load saved login
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Login first time
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def add_event(title, start_time, end_time):

    service = get_calendar_service()

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("Created:", event.get("htmlLink"))


def today_events():

    service = get_calendar_service()

    now = datetime.datetime.utcnow().isoformat() + "Z"

    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events.get("items", [])
from datetime import datetime, timedelta, timezone

def get_today_events():
    service = get_calendar_service()

    # Current time in UTC
    now = datetime.now(timezone.utc)

    # Beginning of today (UTC)
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Beginning of tomorrow
    end_day = start_day + timedelta(days=1)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_day.isoformat(),
        timeMax=end_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])