import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate():
    creds_path = r"D:\gmail_api_project\python_source_code\credentials.json"  # Full path
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

service = authenticate()
