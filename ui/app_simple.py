"""
EduMate Simple Streamlit App
============================

A simple, beginner-friendly Streamlit chat interface for EduMate.
This app demonstrates how to create a basic chat UI that connects to the EduMate API.

Prerequisites:
- Backend API running at http://localhost:8000
- Install dependencies: pip install streamlit requests

Usage:
    streamlit run app_simple.py
"""

import os
import streamlit as st
import requests

# ============================================================================
# Configuration
# ============================================================================

# API endpoint - can be configured via environment variable
API_BASE_URL = os.environ.get("API_BASE", "http://localhost:8000")

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="EduMate - Simple Chat",
    page_icon="🎓",
    layout="centered"
)

# ============================================================================
# Header
# ============================================================================

st.title("🎓 EduMate - Your Study Assistant")
st.caption("Ask me anything about your course materials!")

# ============================================================================
# Session State Initialization
# ============================================================================

# Initialize chat history in session state
# This persists the conversation across reruns
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm EduMate, your AI study assistant. I can help you with questions about your course materials. What would you like to know?"
        }
    ]

# ============================================================================
# Display Chat History
# ============================================================================

# Display all messages in the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# Chat Input and Response
# ============================================================================

# Chat input field
if user_input := st.chat_input("Type your question here..."):
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call the EduMate API
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"messages": st.session_state.messages},
                    timeout=120
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse the response
                data = response.json()
                answer = data.get("answer", "I couldn't generate a response.")
                sources = data.get("sources", [])
                
                # Display the answer
                st.markdown(answer)
                
                # Display sources if available
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.markdown(f"- {source}")
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
                
            except requests.exceptions.ConnectionError:
                error_msg = "❌ Cannot connect to the API. Make sure the backend is running at " + API_BASE_URL
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                
            except requests.exceptions.Timeout:
                error_msg = "⏱️ Request timed out. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# ============================================================================
# Sidebar Information
# ============================================================================

with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **EduMate** is a local AI study assistant that helps you find answers in your course materials.
    
    ### Features:
    - 💬 Natural conversation interface
    - 📚 Retrieves information from course documents
    - 🎯 Provides sourced answers
    - 🔒 Runs completely locally
    
    ### How to Use:
    1. Type your question in the chat box
    2. Press Enter or click Send
    3. Wait for EduMate to respond
    4. Check the sources for reference
    
    ### API Status:
    """)
    
    # Check API health
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ API is online")
        else:
            st.error("⚠️ API is not responding correctly")
    except:
        st.error("❌ API is offline")
    
    st.markdown(f"**API URL:** `{API_BASE_URL}`")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hi! I'm EduMate, your AI study assistant. I can help you with questions about your course materials. What would you like to know?"
            }
        ]
        st.rerun()
