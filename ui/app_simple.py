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
# Header
# ============================================================================

st.title("🎓 EduMate - Your AI Module Convenor Assistant")
st.caption("Personalized academic guidance powered by AI — not just a Q&A bot, but an intelligent guide inspired by Prof. Zeng's mentorship style")

# ============================================================================
# Session State Initialization
# ============================================================================

# Initialize chat history in session state
# This persists the conversation across reruns
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm EduMate, your AI Module Convenor Assistant. I provide personalized academic guidance, understand assignment contexts, and help you succeed in your coursework. What would you like help with today?"
        }
    ]

# Initialize session ID for memory tracking
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Initialize mode (convenor by default for intelligent guidance)
if "mode" not in st.session_state:
    st.session_state.mode = "convenor"

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
                # Call the EduMate API with session ID and mode
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "messages": st.session_state.messages,
                        "session_id": st.session_state.session_id,
                        "mode": st.session_state.mode
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
    **EduMate** is an AI-powered Module Convenor Assistant that provides intelligent, personalized academic guidance.
    
    ### 🎯 Key Features:
    - **Intelligent Guidance**: Not just Q&A - provides tailored academic support
    - **Context Awareness**: Understands assignments, deadlines, and coursework
    - **Session Memory**: Remembers conversation context for personalized help
    - **RAG-Powered**: Retrieves information from course documents
    - **Source Citations**: All answers cite course materials
    - **Mentorship Style**: Inspired by Prof. Zeng's supportive teaching approach
    
    ### 🚀 Modes:
    """)
    
    # Mode selector
    mode_options = {
        "convenor": "🎓 Convenor Mode (Recommended)",
        "docs": "📚 Document Q&A",
        "coach": "💪 Study Coach",
        "facts": "⚡ Quick Facts"
    }
    
    selected_mode = st.radio(
        "Choose mode:",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        index=0  # Default to convenor
    )
    
    # Update mode in session state
    st.session_state.mode = selected_mode
    
    st.markdown("""
    ### 💡 How to Use:
    1. Select your preferred mode above
    2. Type your question in the chat box
    3. Get personalized academic guidance
    4. Check sources for reference materials
    
    ### 🔍 Example Questions:
    - "Help me understand the key concepts for my assignment"
    - "What should I focus on for the exam?"
    - "Can you give me feedback on my approach?"
    - "Explain the learning outcomes for this module"
    """)
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I'm EduMate, your AI Module Convenor Assistant. I provide personalized academic guidance, understand assignment contexts, and help you succeed in your coursework. What would you like help with today?"
            }
        ]
        # Generate new session ID
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("---")
    st.caption("💻 Powered by OpenRouter & ChromaDB")
    
    st.markdown("### API Status:")
    
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
