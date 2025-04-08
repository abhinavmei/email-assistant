import os
import json
import datetime
import base64
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ==== CONFIGURATION ====
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send',
]

# ==== AUTHENTICATION ====
def get_google_services(script_dir):
    creds = None
    token_path = os.path.join(script_dir, 'token.json')
    credentials_path = os.path.join(script_dir, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    calendar_service = build('calendar', 'v3', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return calendar_service, gmail_service

# ==== MOCK LLM REPLY GENERATOR ====
def generate_meeting_reply(title, date, time, duration):
    return f"""Hi,\n\nThanks for your email. I've scheduled our \"{title}\" on {date} at {time} for {duration} minutes.\n\nLooking forward to it!\n\nBest,\nAbhinav"""

# ==== CREATE CALENDAR EVENT ====
def create_calendar_event(service, data):
    start = datetime.datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
    end = start + datetime.timedelta(minutes=data.get("duration_minutes", 30))

    event = {
        'summary': data.get("title", "Untitled Meeting"),
        'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {event_result.get('htmlLink')}")
    return event_result

# ==== SEND EMAIL REPLY ====
def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = 'me'
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email_reply(gmail_service, to_email, subject, body):
    message = create_message(to_email, subject, body)
    sent = gmail_service.users().messages().send(userId='me', body=message).execute()
    print(f"📩 Reply sent to {to_email}: Message ID {sent['id']}")

# ==== MAIN FLOW ====
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "sample_meeting_email.json")

    try:
        with open(json_path, "r") as f:
            meeting_data = json.load(f)
    except FileNotFoundError:
        print("❌ 'sample_meeting_email.json' file not found.")
        exit()

    if not meeting_data.get("meeting"):
        print("❌ No meeting info detected in the JSON.")
        exit()

    # 1. Authenticate and initialize services
    calendar_service, gmail_service = get_google_services(script_dir)

    # 2. Create event
    create_calendar_event(calendar_service, meeting_data)

    # 3. Generate reply
    reply_text = generate_meeting_reply(
        meeting_data["title"],
        meeting_data["date"],
        meeting_data["time"],
        meeting_data["duration_minutes"]
    )

    # 4. Send email
    recipient_email = meeting_data.get("sender_email", "example@gmail.com")
    send_email_reply(gmail_service, recipient_email, "Meeting Confirmed", reply_text)
