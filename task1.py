import os
import base64
import pickle
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scope (Read Emails)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Token file path (for caching)
TOKEN_PATH = r"D:\gmail_api_project\python_source_code\token.pickle"
CREDENTIALS_PATH = r"D:\gmail_api_project\python_source_code\credentials.json"

def authenticate():
    """Authenticate with Gmail API without token caching."""
    creds_path = r"D:\gmail_api_project\python_source_code\credentials.json"
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

    # Check if token file exists (to avoid re-authentication)
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, max_results=10, label_ids=['INBOX']):
    """Fetch a list of emails from the Gmail API."""
    results = service.users().messages().list(userId='me', labelIds=label_ids, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_message(service, msg_id):
    """Retrieve a specific email message by ID."""
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    return message

def decode_message(message):
    """Decode the email body."""
    headers = message['payload']['headers']

    # Extract sender
    sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")

    # Extract subject
    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")

    # Initialize body safely
    body = "No email body found."

    # Try extracting plain text body
    payload = message['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    return sender, subject, body


def main():
    """Main function to authenticate and fetch emails."""
    service = authenticate()  # Now returns the built Gmail service
    messages = list_messages(service)

    if not messages:
        print("No messages found.")
        return

    for msg in messages[:5]:
        msg_id = msg['id']
        message = get_message(service, msg_id)
        sender, subject, body = decode_message(message)

        print(f"📧 **From:** {sender}")
        print(f"📌 **Subject:** {subject}")
        print(f"📝 **Body:**\n{body[:500]}")
        print("-" * 50)

if __name__ == '__main__':
    main()
