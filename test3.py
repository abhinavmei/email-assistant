def get_thread_emails(thread_id):
    """Retrieve all emails in a thread."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT sender, subject, timestamp, body FROM emails WHERE thread_id = %s ORDER BY timestamp ASC", (thread_id,))
    emails = cursor.fetchall()

    conn.close()
    return emails
