email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Fri, 5 Apr 2024 10:00:00 +0000
Message-ID: <1234@example.com>

This is a test email body.
"""

with open("D:/gmail_api_project/python_source_code/sample_email.eml", "w") as f:
    f.write(email_content)

print("Sample email created: sample_email.eml")
