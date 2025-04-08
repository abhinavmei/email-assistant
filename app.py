import streamlit as st
from your_backend import (
    fetch_emails_from_db,
    summarize_thread,
    detect_intent,
    take_action_based_on_intent
)

st.set_page_config(page_title="AI Email Assistant", layout="wide")
st.title("📬 AI-Powered Email Assistant")

# Step 1: Fetch Emails
st.header("📥 Inbox Viewer")
if st.button("Fetch Emails"):
    emails = fetch_emails_from_db()
    st.session_state["emails"] = emails

if "emails" in st.session_state:
    for idx, email in enumerate(st.session_state["emails"]):
        with st.expander(f"{email['subject']} - {email['sender']} ({email['timestamp']})"):
            st.text(email["body"][:1000])
            if st.button(f"Summarize Thread {idx}"):
                summary = summarize_thread(email["thread_id"])
                st.session_state["summary"] = summary
                st.session_state["selected_thread"] = email["thread_id"]

# Step 2: Show Summary
if "summary" in st.session_state:
    st.header("🧠 Thread Summary")
    st.write(st.session_state["summary"])

    if st.button("Detect Intent"):
        intent = detect_intent(st.session_state["summary"])
        st.session_state["intent"] = intent

# Step 3: Show Detected Intent
if "intent" in st.session_state:
    st.header("🤖 Detected Intent")
    st.json(st.session_state["intent"])

    if st.button("🚀 Take Action"):
        result = take_action_based_on_intent(
            thread_id=st.session_state["selected_thread"],
            intent_data=st.session_state["intent"]
        )
        st.success("Action Completed:")
        st.json(result)

st.sidebar.markdown("Made with 💡 by GPT-4 + You")
