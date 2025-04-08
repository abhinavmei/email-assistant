from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request 
import datetime
import json
import os

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None

    # Use saved token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid creds, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the token for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

# Read structured data (LLM output or manual test)
try:
   with open("sample_meeting_email.json", "r") as f:
        meeting_data = json.load(f)
except FileNotFoundError:
    print("❌ 'email_to_calendar.json' file not found.")
    exit()

# Skip if no meeting was detected
if meeting_data.get("meeting") is not True:
    print("❌ No meeting info detected in JSON.")
    exit()

try:
    # Parse datetime
    start = datetime.datetime.strptime(
        f"{meeting_data['date']} {meeting_data['time']}", "%Y-%m-%d %H:%M"
    )
except Exception as e:
    print(f"❌ Date/time parsing error: {e}")
    exit()

end = start + datetime.timedelta(minutes=meeting_data.get("duration_minutes", 30))

# Define event
event = {
    'summary': meeting_data.get("title", "Untitled Meeting"),
    'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
    'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'},
}

# Create event
try:
    service = get_calendar_service()
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {event_result.get('htmlLink')}")
except Exception as e:
    print(f"❌ Error creating event: {e}")
