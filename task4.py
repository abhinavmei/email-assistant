import psycopg2
from datetime import datetime
from transformers import BartTokenizer, BartForConditionalGeneration
import torch

# ✅ Load BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

# ✅ DB Config
DB_CONFIG = {
    "dbname": "email",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def fetch_thread_emails(thread_id):
    print("🔍 Fetching emails from DB...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, recipient, subject, timestamp, body
        FROM emails
        WHERE thread_id = %s
        ORDER BY timestamp ASC;
    """, (thread_id,))
    emails = cursor.fetchall()
    cursor.close()
    conn.close()
    print("✅ Emails fetched.")
    return emails

def format_emails_for_bart(emails):
    print("🧾 Formatting emails for BART input...")
    thread_text = ""
    for email in emails:
        sender, recipient, subject, timestamp, body = email
        thread_text += f"From: {sender}\nTo: {recipient}\nSubject: {subject}\nDate: {timestamp}\n{body}\n\n"
    return thread_text.strip()

def summarize_with_bart(text):
    print("🤖 Generating summary with BART...")
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], max_length=200, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# 🧵 Use your actual thread_id here
thread_id = "<1234@example.com>"

# Run the summarization
emails = fetch_thread_emails(thread_id)
thread_text = format_emails_for_bart(emails)
print("\n📬 Full Thread Text:\n", thread_text)

summary = summarize_with_bart(thread_text)
print("\n📝 Thread Summary:\n", summary)

