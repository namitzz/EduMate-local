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
import requests
import streamlit as st
from urllib.parse import urljoin

# ============================================================================
# Configuration
# ============================================================================

# Allow env or query param override; fallback to production
DEFAULT_API_BASE = "https://edumate-local.fly.dev"
api_from_env = os.getenv("EDUMATE_API_BASE")
api_from_query = st.query_params.get("api", [None])[0] if hasattr(st, "query_params") else None

API_BASE_URL = (api_from_query or api_from_env or DEFAULT_API_BASE).rstrip("/")

# Helper to join paths safely (avoids double slashes)
def api(path: str) -> str:
    return urljoin(API_BASE_URL + "/", path.lstrip("/"))

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

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
            ),
        }
    ]

# ============================================================================
# Header & Controls
# ============================================================================

st.title("🎓 EduMate - Module Convenor Assistant")
st.caption("Personalized academic guidance • Intelligent feedback • Study support")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 New Conversation", help="Clear history and start fresh"):
        st.session_state.messages = [st.session_state.messages[0]]  # keep only welcome message
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ============================================================================
# Display Chat History
# ============================================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# Chat Input and Response
# ============================================================================

if user_input := st.chat_input("Type your question here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show it immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    api("/chat"),
                    json={
                        "messages": st.session_state.messages,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                answer = data.get("answer") or data.get("message") or "I couldn't generate a response."
                sources = data.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("📚 Sources"):
                        for s in sources:
                            # Turn plain URLs into clickable links
                            if isinstance(s, str) and (s.startswith("http://") or s.startswith("https://")):
                                st.markdown(f"- [{s}]({s})")
                            else:
                                st.markdown(f"- {s}")

                # Persist assistant reply
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except requests.exceptions.ConnectionError:
                error_msg = f"❌ Cannot connect to the API. Make sure the backend is running at {API_BASE_URL}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.Timeout:
                error_msg = "⏱️ Request timed out. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.HTTPError as e:
                try:
                    detail = e.response.text[:300]
                except Exception:
                    detail = ""
                error_msg = f"❌ API error: {e} {('- ' + detail) if detail else ''}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        f"""
**EduMate** is an AI-powered Module Convenor Assistant that provides 
intelligent academic guidance and mentorship.

### 🎯 Capabilities
- **Concept Clarification** — Deep understanding of course material  
- **Assignment Guidance** — Structured approach and feedback  
- **Exam Preparation** — Study strategies and topic review  
- **Study Planning** — Time management and learning techniques  
- **Progress Support** — Constructive feedback and encouragement  

### 💡 Features
- 🧠 **Context-Aware** — Remembers your conversation  
- 📚 **RAG-Powered** — References actual course documents  
- 🎓 **Academic Focus** — Educational best practices  
- 🔒 **Privacy-First** — Anonymized session storage  

### 📖 How to Use
1. Ask questions naturally about your coursework  
2. Request assignment guidance or concept explanations  
3. Get study tips and exam preparation strategies  
4. Review sources for deeper understanding  
5. Ask follow-up questions — I remember context!

### 🔄 Session Info
- **Session ID**: `{st.session_state.session_id[:8]}...`  
- **Messages**: {len(st.session_state.messages)}
"""
    )

    st.header("🎨 Interaction Modes")
    st.markdown(
        """
The assistant automatically detects your intent:
- 📝 **Assignment Help** — Guidance on coursework  
- 🤔 **Concept Questions** — Explanations and clarification  
- 📚 **Exam Prep** — Study strategies  
- 📊 **Study Planning** — Organization and techniques  
- 💬 **General Queries** — Course information
"""
    )

    st.subheader("🩺 API Status")
    try:
        health_response = requests.get(api("/health"), timeout=5)
        if health_response.status_code == 200:
            st.success("✅ API is online")
        else:
            st.error(f"⚠️ API responded with {health_response.status_code}")
    except Exception:
        st.error("❌ API is offline")

    st.markdown(f"**API URL:** `{API_BASE_URL}`")

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I'm EduMate, your AI study assistant. I can help you with questions "
                    "about your course materials. What would you like to know?"
                ),
            }
        ]
        st.rerun()
