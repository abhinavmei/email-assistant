def fetch_emails_from_db():
    return [
        {
            "thread_id": "abc123",
            "subject": "Meeting Follow-Up",
            "sender": "john@example.com",
            "timestamp": "2025-04-07 10:00",
            "body": "Hi, just following up on the meeting we had..."
        },
        {
            "thread_id": "def456",
            "subject": "Project Update",
            "sender": "jane@example.com",
            "timestamp": "2025-04-07 15:00",
            "body": "Here is the latest update on the project..."
        }
    ]

def summarize_thread(thread_id):
    return f"This is a mock summary for thread {thread_id}."

def detect_intent(summary_text):
    return {
        "intent": "schedule_meeting",
        "entities": {
            "date": "2025-04-10",
            "time": "3:00 PM",
            "participants": ["john@example.com"]
        }
    }

def take_action_based_on_intent(thread_id, intent_data):
    return {"status": "success", "details": f"Meeting scheduled for thread {thread_id}."}
