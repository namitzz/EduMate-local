"""
EduMate Module Convenor Assistant - Streamlit App
=================================================

An intelligent Module Convenor Assistant that provides personalized academic 
guidance, feedback, and mentorship to students.

Prerequisites:
- Backend API running (default: https://edumate-local.fly.dev)
- Install dependencies: pip install streamlit requests

Usage:
    streamlit run app_simple.py
"""

import os
import uuid
import streamlit as st
import requests

# ============================================================================
# Configuration
# ============================================================================

# API endpoint - hardcoded to production URL
API_BASE_URL = "https://edumate-local.fly.dev/"

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="EduMate - Module Convenor Assistant",
    page_icon="🎓",
    layout="centered"
)

# ============================================================================
# Session State Initialization
# ============================================================================

# Generate or retrieve session ID for conversation memory
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history in session state
# This persists the conversation across reruns
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": (
                "👋 Hello! I'm your **AI Module Convenor Assistant**.\n\n"
                "I'm here to provide personalized academic guidance and support. I can help you with:\n\n"
                "• **Understanding Concepts** - Clarify theories and course material\n"
                "• **Assignment Guidance** - Structure, approach, and rubric interpretation\n"
                "• **Exam Preparation** - Study strategies and topic prioritization\n"
                "• **Study Planning** - Time management and learning techniques\n"
                "• **Progress Feedback** - Constructive advice and improvement suggestions\n\n"
                "💡 **Tip**: I maintain conversation context, so feel free to ask follow-up questions!\n\n"
                "What would you like to work on today?"
            )
        }
    ]

# ============================================================================
# Header & Mode Selection
# ============================================================================

st.title("🎓 EduMate - Module Convenor Assistant")
st.caption("Personalized academic guidance • Intelligent feedback • Study support")

# Add mode selector in the main area
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 New Conversation", help="Clear history and start fresh"):
        st.session_state.messages = [st.session_state.messages[0]]  # Keep only welcome message
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

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
                # Call the EduMate API with session_id for conversation memory
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "messages": st.session_state.messages,
                        "session_id": st.session_state.session_id
                    },
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
    **EduMate** is an AI-powered Module Convenor Assistant that provides 
    intelligent academic guidance and mentorship.
    
    ### 🎯 Capabilities:
    - **Concept Clarification** - Deep understanding of course material
    - **Assignment Guidance** - Structured approach and feedback
    - **Exam Preparation** - Study strategies and topic review
    - **Study Planning** - Time management and learning techniques
    - **Progress Support** - Constructive feedback and encouragement
    
    ### 💡 Features:
    - 🧠 **Context-Aware** - Remembers your conversation
    - 📚 **RAG-Powered** - References actual course documents
    - 🎓 **Academic Focus** - Educational best practices
    - 🔒 **Privacy-First** - Anonymized session storage
    
    ### 📖 How to Use:
    1. Ask questions naturally about your coursework
    2. Request assignment guidance or concept explanations
    3. Get study tips and exam preparation strategies
    4. Review sources for deeper understanding
    5. Ask follow-up questions - I remember context!
    
    ### 🔄 Session Info:
    - **Session ID**: `{}`
    - **Messages**: {}
    
    ---
    
    💬 **Pro Tips:**
    - Be specific about what you need help with
    - Mention assignment names or concepts explicitly
    - Ask for examples or clarification when needed
    - Use "New Conversation" to start fresh
    """.format(st.session_state.session_id[:8] + "...", len(st.session_state.messages)))
    
    st.header("🎨 Interaction Modes")
    st.markdown("""
    The assistant automatically detects your intent:
    - 📝 **Assignment Help** - Guidance on coursework
    - 🤔 **Concept Questions** - Explanations and clarification
    - 📚 **Exam Prep** - Study strategies
    - 📊 **Study Planning** - Organization and techniques
    - 💬 **General Queries** - Course information
    """)
    
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
