# Assuming you already have the `parse_email()` and `store_email()` functions set up.

import os
import base64
import pickle
import psycopg2
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from psycopg2.extras import execute_values

# Gmail API scope (Read Emails)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = r"D:\gmail_api_project\python_source_code\token.pickle"
CREDENTIALS_PATH = r"D:\gmail_api_project\python_source_code\credentials.json"

# Database configuration
DB_CONFIG = {
    "dbname": "email_db",
    "user": "postgre",  # your PostgreSQL username
    "password": "1234",  # your PostgreSQL password
    "host": "localhost"
}

def authenticate():
    """Authenticate with Gmail API and return the service object."""
    creds = None
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
    print(f"Fetched {len(messages)} messages.")  # Debugging line
    return messages

def get_message(service, msg_id):
    """Retrieve a specific email message by ID."""
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    return message

def decode_message(message):
    """Decode the email body."""
    headers = message['payload']['headers']
    sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")
    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
    
    # Extract email body (handling different formats)
    body = "No email body found."
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

    return sender, subject, body

def store_email(email_data):
    """Store parsed email into PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Insert thread if not exists
    cursor.execute("INSERT INTO threads (thread_id) VALUES (%s) ON CONFLICT DO NOTHING", 
                   (email_data["thread_id"],))

    # Insert email
    cursor.execute("""
        INSERT INTO emails (thread_id, message_id, sender, recipients, subject, timestamp, body, in_reply_to) 
        VALUES (%s, %s, %s, %s, %s, TO_TIMESTAMP(%s / 1000.0), %s, %s)
        ON CONFLICT (message_id) DO NOTHING
    """, (
        email_data["thread_id"],
        email_data["message_id"],
        email_data["sender"],
        email_data["recipients"],
        email_data["subject"],
        email_data["timestamp"],
        email_data["body"],
        None  # in_reply_to (handled later for threading)
    ))

    # Insert attachments
    if email_data["attachments"]:
        execute_values(cursor, """
            INSERT INTO attachments (email_id, filename, mime_type, content) 
            VALUES %s
        """, [
            (email_data["message_id"], att["filename"], att["mime_type"], None)  # Handle binary content later
            for att in email_data["attachments"]
        ])

    conn.commit()
    cursor.close()
    conn.close()

def main():
    try:
        service = authenticate()  # Authenticate with Gmail API
        print("Authentication successful.")

        messages = list_messages(service)  # Get the list of emails
        print(f"Fetched {len(messages)} messages.")

        if not messages:
            print("No messages found.")
            return

        for msg in messages[:5]:  # Limit to the first 5 emails
            msg_id = msg['id']
            message = get_message(service, msg_id)
            sender, subject, body = decode_message(message)

            # Debugging: Print out message details
            print(f"Sender: {sender}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...")  # Print the first 200 characters of the body for debugging

            # Prepare email data to store
            email_data = {
                "thread_id": message['threadId'],
                "message_id": msg_id,
                "sender": sender,
                "recipients": "recipient@example.com",  # You can add more logic to extract recipients
                "subject": subject,
                "timestamp": message['internalDate'],  # Convert to proper timestamp if needed
                "body": body,
                "attachments": []  # Handle attachments if necessary
            }

            store_email(email_data)  # Store parsed data in PostgreSQL
            print(f"Email stored successfully: {msg_id}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
