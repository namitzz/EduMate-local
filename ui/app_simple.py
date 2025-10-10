"""
EduMate Module Convenor Assistant - Streamlit App
=================================================

An intelligent Module Convenor Assistant that provides personalized academic 
guidance, feedback, and mentorship to students.

Cloud-Native Deployment:
- Frontend: Streamlit Cloud (free tier)
- Backend: Fly.io (free tier)
- LLM: OpenRouter API (pay-as-you-go)

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
    page_title="EduMate - AI Module Convenor",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    /* Main chat container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Success/error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* Chat input */
    .stChatInput > div > div {
        border-radius: 0.5rem;
    }
    
    /* Headers */
    h1 {
        font-weight: 700;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Caption */
    .caption {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

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
                "👋 Hello! I'm your **AI Module Convenor Assistant**.\\n\\n"
                "I'm here to provide personalized academic guidance and support. I can help you with:\\n\\n"
                "• **Understanding Concepts** - Clarify theories and course material\\n"
                "• **Assignment Guidance** - Structure, approach, and rubric interpretation\\n"
                "• **Exam Preparation** - Study strategies and topic prioritization\\n"
                "• **Study Planning** - Time management and learning techniques\\n"
                "• **Progress Feedback** - Constructive advice and improvement suggestions\\n\\n"
                "💡 **Tip**: I maintain conversation context, so feel free to ask follow-up questions!\\n\\n"
                "What would you like to work on today?"
            ),
        }
    ]

if "api_status" not in st.session_state:
    st.session_state.api_status = None

# ============================================================================
# Header & Controls
# ============================================================================

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🎓 EduMate")
    st.markdown('<p class="caption">AI Module Convenor Assistant • Personalized Academic Guidance</p>', 
                unsafe_allow_html=True)
with col_btn:
    st.write("")  # Spacer
    if st.button("🔄", help="Start a new conversation", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]  # keep only welcome message
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

st.divider()

# ============================================================================
# Display Chat History
# ============================================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# Chat Input and Response
# ============================================================================

if user_input := st.chat_input("💬 Ask me anything about your course..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show it immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
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
                    with st.expander("📚 View Sources", expanded=False):
                        for i, s in enumerate(sources, 1):
                            # Turn plain URLs into clickable links
                            if isinstance(s, str) and (s.startswith("http://") or s.startswith("https://")):
                                st.markdown(f"{i}. [{s}]({s})")
                            else:
                                st.markdown(f"{i}. {s}")

                # Persist assistant reply
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.api_status = "online"

            except requests.exceptions.ConnectionError:
                error_msg = (
                    f"❌ **Connection Error**\\n\\n"
                    f"Cannot connect to the backend API at `{API_BASE_URL}`.\\n\\n"
                    f"**Possible causes:**\\n"
                    f"• Backend server is not running\\n"
                    f"• Incorrect API URL\\n"
                    f"• Network connectivity issues\\n\\n"
                    f"**What to do:**\\n"
                    f"• Check if the backend is deployed and running\\n"
                    f"• Verify the API URL in the sidebar\\n"
                    f"• Try again in a moment"
                )
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.session_state.api_status = "offline"

            except requests.exceptions.Timeout:
                error_msg = (
                    "⏱️ **Request Timeout**\\n\\n"
                    "The request took too long to complete (>120 seconds).\\n\\n"
                    "**What to do:**\\n"
                    "• Try asking a simpler question\\n"
                    "• Wait a moment and try again\\n"
                    "• The backend may be warming up after being idle"
                )
                st.warning(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.HTTPError as e:
                try:
                    detail = e.response.text[:300]
                except Exception:
                    detail = ""
                error_msg = (
                    f"❌ **API Error ({e.response.status_code})**\\n\\n"
                    f"The backend returned an error.\\n\\n"
                    f"**Details:** {detail if detail else 'No additional information'}\\n\\n"
                    f"**What to do:**\\n"
                    f"• Try rephrasing your question\\n"
                    f"• Check backend logs for more details\\n"
                    f"• Contact support if the issue persists"
                )
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.session_state.api_status = "error"

            except Exception as e:
                error_msg = (
                    f"❌ **Unexpected Error**\\n\\n"
                    f"Something went wrong: {str(e)}\\n\\n"
                    f"**What to do:**\\n"
                    f"• Try again\\n"
                    f"• Refresh the page if the issue persists\\n"
                    f"• Report this error if it continues"
                )
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("ℹ️ About EduMate")
    st.markdown(
        """
**EduMate** is an AI-powered Module Convenor Assistant that provides 
intelligent academic guidance and mentorship.

### 🎯 What I Can Help With
- 📖 **Concept Clarification** — Understand course material  
- 📝 **Assignment Guidance** — Structure and approach  
- 📚 **Exam Preparation** — Study strategies  
- ⏱️ **Study Planning** — Time management  
- 💬 **Progress Support** — Constructive feedback  

### ✨ Key Features
- 🧠 **Context-Aware** — I remember our conversation  
- 📚 **Source-Based** — References actual course documents  
- 🎓 **Academic Focus** — Educational best practices  
- 🔒 **Privacy-First** — Anonymized sessions  
"""
    )

    st.divider()

    st.subheader("🔧 System Status")
    
    # API Status Check
    status_placeholder = st.empty()
    try:
        health_response = requests.get(api("/health"), timeout=5)
        if health_response.status_code == 200:
            status_placeholder.success("✅ Backend API: Online")
            st.session_state.api_status = "online"
        else:
            status_placeholder.warning(f"⚠️ Backend API: Status {health_response.status_code}")
            st.session_state.api_status = "warning"
    except requests.exceptions.Timeout:
        status_placeholder.error("⏱️ Backend API: Timeout")
        st.session_state.api_status = "timeout"
    except Exception:
        status_placeholder.error("❌ Backend API: Offline")
        st.session_state.api_status = "offline"

    st.caption(f"**API URL:** `{API_BASE_URL}`")
    
    st.divider()

    st.subheader("💬 Session Info")
    st.caption(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    st.caption(f"**Messages:** {len(st.session_state.messages)}")
    
    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm your **AI Module Convenor Assistant**. "
                    "I can help you with course concepts, assignments, exam prep, and study planning. "
                    "What would you like to work on today?"
                ),
            }
        ]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.caption("### 📖 Quick Tips")
    st.caption(
        """
- Ask questions naturally about your coursework  
- Request specific guidance on assignments  
- Get study strategies for exams  
- Ask follow-up questions for deeper understanding  
- Check sources for more details
"""
    )

    st.divider()

    st.caption("### 🚀 Powered By")
    st.caption(
        """
- **Frontend:** Streamlit Cloud  
- **Backend:** Fly.io  
- **LLM:** OpenRouter API  
- **Embeddings:** SentenceTransformers  

**Zero local setup • $0 base cost**
"""
    )
