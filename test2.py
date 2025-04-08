from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(r"D:\gmail_api_project\python_source_code\credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)  # Opens a browser for login
    with open("token.json", "w") as token:
        token.write(creds.to_json())

authenticate_gmail()
