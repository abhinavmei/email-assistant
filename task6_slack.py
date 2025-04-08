import requests

SLACK_BOT_TOKEN = "xoxb-8716323595330-8715481396820-dia010jwk0lrm5N203OBnCy6"
USER_ID = "U08M29HHSSE"  # ✅ Your Slack user ID
MESSAGE_TEXT = "🚀 Hello from your AI email assistant!"

def send_slack_message(token, channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("ok"):
        print("✅ Message sent successfully!")
    else:
        print("❌ Error:", result.get("error"))

# Run it
send_slack_message(SLACK_BOT_TOKEN, USER_ID, MESSAGE_TEXT)
