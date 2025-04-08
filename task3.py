import mailparser
import psycopg2
from datetime import datetime
import os

# ✅ Correct database config
DB_CONFIG = {
    "dbname": "email",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def parse_email(raw_email):
    mail = mailparser.parse_from_string(raw_email)
    return {
        "message_id": mail.message_id,
        "thread_id": mail.thread_id or mail.message_id,
        "in_reply_to": mail.in_reply_to,
        "sender": mail.from_[0][1],  # Extract email address from tuple
        "recipient": mail.to[0][1] if mail.to else None,
        "subject": mail.subject,
        "timestamp": mail.date,
        "body": mail.text_plain[0] if mail.text_plain else "",
        "body_html": mail.text_html[0] if mail.text_html else "",
        "has_attachments": bool(mail.attachments),
        "attachments": [
            {
                "filename": att["filename"],
                "mime_type": att["mail_content_type"],
                "data": att["payload"]
            }
            for att in mail.attachments
        ]
    }

def store_email(email_data):
    print("🔍 Connecting to DB with config:", DB_CONFIG)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            message_id TEXT UNIQUE,
            thread_id TEXT,
            in_reply_to TEXT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            timestamp TIMESTAMPTZ,
            body TEXT,
            body_html TEXT,
            has_attachments BOOLEAN
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id SERIAL PRIMARY KEY,
            email_id INTEGER REFERENCES emails(id),
            filename TEXT,
            mime_type TEXT,
            data BYTEA
        );
    """)

    cursor.execute("""
        INSERT INTO emails (message_id, thread_id, in_reply_to, sender, recipient, subject, timestamp, body, body_html, has_attachments)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        email_data["message_id"], email_data["thread_id"], email_data["in_reply_to"],
        email_data["sender"], email_data["recipient"], email_data["subject"],
        email_data["timestamp"], email_data["body"], email_data["body_html"],
        email_data["has_attachments"]
    ))

    email_id = cursor.fetchone()[0]

    for att in email_data["attachments"]:
        cursor.execute("""
            INSERT INTO attachments (email_id, filename, mime_type, data)
            VALUES (%s, %s, %s, %s)
        """, (email_id, att["filename"], att["mime_type"], att["data"]))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Email stored successfully!")

# ✅ Load the sample email file from same directory as script
base_dir = os.path.dirname(os.path.abspath(__file__))
eml_path = os.path.join(base_dir, "sample_email.eml")

with open(eml_path, "r") as f:
    raw_email = f.read()

parsed_email = parse_email(raw_email)
store_email(parsed_email)
