import streamlit as st
import requests
import uuid
import os
from datetime import datetime
import hmac
import base64

# Configuration and Settings
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook-test/42e650d7-3e50-4dda-bf4f-d3e16761b1cd"
BEARER_TOKEN = "__n8n_BLANK_VALUE_e5362baf-c777-4d57-a609-6eaf1f9e87f6/chat"

# Authentication credentials (in production, use environment variables)
VALID_CREDENTIALS = {
    "root": "admin123"  # username: password
}

def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with username and password."""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                return True
        return False

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = False

    if not st.session_state["authentication_status"]:
        if login_form():
            username = st.session_state["username"]
            password = st.session_state["password"]
            
            if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
                st.session_state["authentication_status"] = True
                return True
            else:
                st.error("Invalid username or password")
                return False
        return False
    return True

def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    """Send message to LLM via webhook."""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("output", "No response from server")
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with LLM: {str(e)}")
        return f"Error: {str(e)}"

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

def display_chat_interface():
    """Display the chat interface."""
    st.title("Secure Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(f"Sent at: {message.get('timestamp', 'Unknown time')}")

    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        with st.chat_message("user"):
            st.write(user_input)
            st.caption(f"Sent at: {timestamp}")

        # Get LLM response
        with st.spinner("Getting response..."):
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)
        
        # Add LLM response to chat history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "assistant",
            "content": llm_response,
            "timestamp": timestamp
        })
        
        with st.chat_message("assistant"):
            st.write(llm_response)
            st.caption(f"Received at: {timestamp}")

def add_logout_button():
    """Add a logout button to the sidebar."""
    if st.sidebar.button("Logout"):
        st.session_state["authentication_status"] = False
        st.session_state.messages = []
        st.session_state.session_id = generate_session_id()
        st.rerun()

def main():
    st.set_page_config(page_title="Secure Chat App", layout="wide")
    
    initialize_session_state()
    
    if check_password():
        add_logout_button()
        display_chat_interface()

if __name__ == "__main__":
    main()
