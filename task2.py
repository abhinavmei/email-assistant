from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import email

def get_gmail_service():
    creds = Credentials.from_authorized_user_file(r'D:\gmail_api_project\python_source_code\token.json')
  # Ensure OAuth2 authentication
    service = build('gmail', 'v1', credentials=creds)
    return service

def parse_email(msg):
    headers = msg.get("payload", {}).get("headers", [])
    email_data = {h["name"]: h["value"] for h in headers if h["name"] in ["From", "To", "Cc", "Bcc", "Subject", "Date"]}
    
    # Extract the email body
    parts = msg.get("payload", {}).get("parts", [])
    body = None
    for part in parts:
        if part["mimeType"] == "text/plain":
            body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            break
    
    email_data["Body"] = body

    # Extract attachments
    attachments = []
    for part in parts:
        if "filename" in part and part["filename"]:
            attachment_id = part["body"].get("attachmentId")
            attachments.append({"filename": part["filename"], "attachment_id": attachment_id})
    
    email_data["Attachments"] = attachments
    return email_data

def fetch_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        parsed_email = parse_email(msg_data)
        emails.append(parsed_email)

    return emails

# Fetch and print emails
emails = fetch_emails()
for email in emails:
    print(email)
