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
DEFAULT_API_BASE = "https://edumate-local-api.fly.dev"
api_from_env = os.getenv("EDUMATE_API_BASE")
api_from_query = st.query_params.get("api") if hasattr(st, "query_params") else None

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

# Custom CSS for enhanced UI with modern design
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global font */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main app background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Chat messages */
    .stChatMessage {
        padding: 1.25rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Chat message styling - keeping simple for compatibility */
    .stChatMessage {
        background: white;
    }
    
    /* Success/error messages with modern design */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-left: 4px solid #ffc107;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid #e9ecef;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }
    
    /* Chat input with modern design */
    .stChatInput > div {
        border-radius: 1rem;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stChatInput > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Main title with gradient */
    h1 {
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    /* Section headers */
    h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Caption styling */
    .caption {
        color: #6c757d;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Expander styling - using more stable selectors */
    details > summary {
        background: #f8f9fa;
        border-radius: 0.5rem;
        font-weight: 500;
        padding: 0.75rem;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e9ecef;
    }
    
    /* Link styling */
    a {
        color: #667eea;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    /* Code blocks */
    code {
        background: #f8f9fa;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        color: #e83e8c;
        font-size: 0.875em;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    
    .status-online {
        background: #d4edda;
        color: #155724;
    }
    
    .status-offline {
        background: #f8d7da;
        color: #721c24;
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
                "# 👋 Welcome to EduMate!\n\n"
                "I'm your **AI Module Convenor Assistant** - here to provide personalized academic guidance and support.\n\n"
                "## 🎯 How I Can Help You\n\n"
                "### 📚 Understanding Concepts\n"
                "Get clear explanations of theories and course material with practical examples.\n\n"
                "### 📝 Assignment Guidance\n"
                "Receive structured guidance on coursework, rubric interpretation, and approach strategies.\n\n"
                "### 📖 Exam Preparation\n"
                "Learn effective study strategies, topic prioritization, and preparation techniques.\n\n"
                "### ⏰ Study Planning\n"
                "Optimize your time management and discover proven learning techniques.\n\n"
                "### 💬 Progress Feedback\n"
                "Get constructive advice and personalized improvement suggestions.\n\n"
                "---\n\n"
                "💡 **Pro Tip**: I remember our conversation, so feel free to ask follow-up questions and dive deeper into topics!\n\n"
                "✨ **Ready to get started?** Ask me anything about your coursework!"
            ),
        }
    ]

if "api_status" not in st.session_state:
    st.session_state.api_status = None

# ============================================================================
# Header & Controls
# ============================================================================

# Create a modern header with controls
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
        <div>
            <h1 style="margin: 0;">🎓 EduMate</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

col_subtitle, col_new_chat = st.columns([5, 1])
with col_subtitle:
    st.markdown(
        '<p style="color: #6c757d; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 1rem;">💡 Your AI Module Convenor • Personalized Academic Guidance</p>', 
        unsafe_allow_html=True
    )
with col_new_chat:
    if st.button("🔄 New Chat", help="Start a fresh conversation", use_container_width=True, type="primary"):
        st.session_state.messages = [st.session_state.messages[0]]  # keep only welcome message
        st.session_state.session_id = str(uuid.uuid4())
        st.success("✨ New conversation started!")
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

if user_input := st.chat_input("💬 Ask me anything about your course... (e.g., 'Explain the concept of...' or 'Help me with my assignment on...')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show it immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response (SSE streaming)
with st.chat_message("assistant"):
    with st.spinner("🤔 Thinking..."):
        try:
            payload = {
                "model": WORKING_MODEL,                # <- explicit, known-good model
                "messages": st.session_state.messages,
                "temperature": 0.2,
            }

            # Ask backend to stream (SSE)
            resp = requests.post(
                api("/chat"),
                json=payload,
                timeout=120,
                stream=True,
            )
            resp.raise_for_status()

            # Render streamed tokens as they arrive
            full = ""
            placeholder = st.empty()

            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue

                data_str = line[6:].strip()

                if data_str == "[DONE]":
                    break

                # Each chunk looks like OpenAI-style delta JSON
                # {"choices":[{"delta":{"content":"..."}}], ...}
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        full += token
                        placeholder.markdown(full)
                except Exception:
                    # ignore keepalives or malformed fragments
                    pass

            # Persist final assistant reply
            answer = full if full.strip() else "I couldn't generate a response."
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.api_status = "online"

        except requests.exceptions.ConnectionError:
            error_msg = (
                "## ❌ Connection Error\n\n"
                f"Cannot connect to the backend API at:\n\n"
                f"`{API_BASE_URL}`\n\n"
                "### 🔍 Possible Causes\n"
                "- Backend server is not running or unavailable\n"
                "- Incorrect API URL configuration\n"
                "- Network connectivity issues\n\n"
                "### 💡 What You Can Do\n"
                "1. Check if the backend is deployed and running\n"
                "2. Verify the API URL in the sidebar\n"
                "3. Wait a moment and try again\n"
                "4. Contact support if the issue persists"
            )
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.session_state.api_status = "offline"

        except requests.exceptions.Timeout:
            error_msg = (
                "## ⏱️ Request Timeout\n\n"
                "The request took too long to complete (>120 seconds).\n\n"
                "### 💡 What You Can Do\n"
                "1. Try asking a simpler or more specific question\n"
                "2. Wait a moment and try again\n"
                "3. The backend may be warming up after being idle\n"
                "4. Check your internet connection"
            )
            st.warning(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        except requests.HTTPError as e:
            try:
                detail = e.response.text[:600]
            except Exception:
                detail = ""
            error_msg = (
                f"## ❌ API Error (Status: {e.response.status_code})\n\n"
                f"The backend returned an error.\n\n"
                f"**Details:** {detail if detail else 'No additional information available'}\n\n"
                "### 💡 What You Can Do\n"
                "1. Try rephrasing your question\n"
                "2. Check backend logs for more details\n"
                "3. Wait a moment and try again\n"
                "4. Contact support if the issue persists"
            )
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.session_state.api_status = "error"

        except Exception as e:
            error_msg = (
                "## ❌ Unexpected Error\n\n"
                f"Something went wrong:\n\n"
                f"```\n{str(e)}\n```\n\n"
                "### 💡 What You Can Do\n"
                "1. Try your question again\n"
                "2. Refresh the page if the issue persists\n"
                "3. Contact support and report this error"
            )
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.markdown("## 📚 EduMate Assistant")
    st.markdown("*Your AI-Powered Academic Guide*")
    
    st.divider()
    
    # About section with better formatting
    with st.expander("ℹ️ **About EduMate**", expanded=False):
        st.markdown(
            """
**EduMate** is an intelligent AI assistant that acts as your personal 
module convenor, providing tailored academic guidance and mentorship.

### 🌟 Why Choose EduMate?

- 🧠 **Smart Context Awareness** — Remembers your conversation
- 📚 **Evidence-Based Answers** — Cites actual course documents
- 🎓 **Academic Excellence** — Follows educational best practices
- 🔒 **Privacy Protected** — Fully anonymized sessions
- ⚡ **Always Available** — 24/7 academic support
"""
        )
    
    st.divider()

    # What I Can Help With section
    with st.expander("🎯 **What I Can Help With**", expanded=True):
        st.markdown(
            """
**Concept Clarification**
> Understand complex theories and course material

**Assignment Support**
> Get guidance on structure and approach

**Exam Strategies**
> Learn effective study techniques

**Time Management**
> Optimize your study planning

**Academic Feedback**
> Receive constructive improvement tips
"""
        )

    st.divider()

    # System Status with improved design
    st.markdown("### 🔧 System Status")
    
    status_col1, status_col2 = st.columns([1, 3])
    
    try:
        health_response = requests.get(api("/health"), timeout=5)
        if health_response.status_code == 200:
            with status_col1:
                st.markdown("✅")
            with status_col2:
                st.markdown("**Backend Online**")
            st.session_state.api_status = "online"
        else:
            with status_col1:
                st.markdown("⚠️")
            with status_col2:
                st.markdown(f"**Status {health_response.status_code}**")
            st.session_state.api_status = "warning"
    except requests.exceptions.Timeout:
        with status_col1:
            st.markdown("⏱️")
        with status_col2:
            st.markdown("**Timeout**")
        st.session_state.api_status = "timeout"
    except Exception:
        with status_col1:
            st.markdown("❌")
        with status_col2:
            st.markdown("**Offline**")
        st.session_state.api_status = "offline"

    st.caption(f"🌐 API: `{API_BASE_URL[:30]}...`" if len(API_BASE_URL) > 30 else f"🌐 API: `{API_BASE_URL}`")
    
    st.divider()

    # Session Info
    st.markdown("### 💬 Current Session")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric("Messages", len(st.session_state.messages))
    with info_col2:
        st.metric("Session", f"#{st.session_state.session_id[:8]}")
    
    st.divider()

    # Action buttons with better design
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "# 👋 Welcome Back!\n\n"
                    "I'm your **AI Module Convenor Assistant**. "
                    "I can help you with course concepts, assignments, exam prep, and study planning.\n\n"
                    "What would you like to work on today?"
                ),
            }
        ]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # Quick Tips
    with st.expander("💡 **Quick Tips**", expanded=False):
        st.markdown(
            """
- 🎯 Ask specific questions about your coursework
- 📝 Request detailed guidance on assignments
- 📚 Get comprehensive exam preparation strategies
- 🔄 Ask follow-up questions for deeper understanding
- 📖 Check sources in the expandable section below answers
"""
        )

    st.divider()

    # Technology stack
    with st.expander("🚀 **Powered By**", expanded=False):
        st.markdown(
            """
**Frontend**
- Streamlit Cloud (Free Tier)

**Backend**
- Fly.io (Free Tier)
- FastAPI & Uvicorn

**AI & ML**
- OpenRouter API (GPT-3.5)
- SentenceTransformers
- ChromaDB Vector Database

**💰 Total Cost: $0/month base**
*(Pay only for API usage)*
"""
        )
