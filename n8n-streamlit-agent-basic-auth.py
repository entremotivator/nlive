import streamlit as st
import requests
import uuid
import os
from typing import Tuple

# Constants
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/ba43778d-3a11-48fc-ac91-bb4222987045/chat"
BEARER_TOKEN = "__n8n_BLANK_VALUE_e5362baf-c777-4d57-a609-6eaf1f9e87f6"

# Authentication credentials
VALID_USERNAME = "root"
VALID_PASSWORD = "your_secure_password"  # Replace with a secure password

def check_password() -> bool:
    """Returns `True` if the user had the correct password."""

    def password_entered() -> bool:
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == VALID_USERNAME and st.session_state["password"] == VALID_PASSWORD:
            st.session_state["password_correct"] = True
            return True
        else:
            st.session_state["password_correct"] = False
            return False

    if "password_correct" not in st.session_state:
        # First run, show input for username and password
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        if st.button("Login"):
            return password_entered()
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        if st.button("Login"):
            return password_entered()
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct
        return True

def generate_session_id() -> str:
    return str(uuid.uuid4())

def send_message_to_llm(session_id: str, message: str) -> str:
    """Send message to LLM and return response"""
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
        return response.json()["output"]
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

def display_chat_interface():
    """Display the chat interface"""
    st.title("Secure Chat with LLM")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Get LLM response with error handling
        with st.spinner("Thinking..."):
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        # Add LLM response to chat history
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.write(llm_response)

def main():
    """Main application flow"""
    initialize_session_state()
    
    # Show authentication screen if not logged in
    if not check_password():
        st.stop()
    
    # Show logout button if logged in
    if st.sidebar.button("Logout"):
        st.session_state["password_correct"] = False
        st.experimental_rerun()
    
    # Display main chat interface
    display_chat_interface()

if __name__ == "__main__":
    main()
