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
    page_icon="EM",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalistic modern dark mode UI
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main app background */
    .main {
        background-color: #0E1117;
    }
    
    /* Chat messages - clean and minimal */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
        background-color: #1A1D24;
        border: 1px solid #262933;
    }
    
    /* Success/error/warning messages - subtle */
    .stSuccess {
        background-color: #1A2E1A;
        border-left: 3px solid #4A9D4A;
        border-radius: 0.25rem;
        padding: 0.75rem;
    }
    
    .stError {
        background-color: #2E1A1A;
        border-left: 3px solid #E74C3C;
        border-radius: 0.25rem;
        padding: 0.75rem;
    }
    
    .stWarning {
        background-color: #2E2A1A;
        border-left: 3px solid #F39C12;
        border-radius: 0.25rem;
        padding: 0.75rem;
    }
    
    .stInfo {
        background-color: #1A2A2E;
        border-left: 3px solid #3498DB;
        border-radius: 0.25rem;
        padding: 0.75rem;
    }
    
    /* Button styling - minimal */
    .stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid #262933;
    }
    
    .stButton > button:hover {
        border-color: #4A90E2;
        background-color: #1A1D24;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #262933;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }
    
    /* Chat input - clean design */
    .stChatInput > div {
        border-radius: 0.5rem;
        border: 1px solid #262933;
        background-color: #1A1D24;
    }
    
    .stChatInput > div:focus-within {
        border-color: #4A90E2;
    }
    
    /* Headings - clean and minimal */
    h1 {
        font-weight: 600;
        color: #E8E8E8;
        font-size: 1.75rem;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: #C8C8C8;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    /* Expander - minimal styling */
    details > summary {
        background-color: #1A1D24;
        border-radius: 0.375rem;
        font-weight: 400;
        padding: 0.5rem 0.75rem;
        border: 1px solid #262933;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #262933;
    }
    
    /* Links */
    a {
        color: #4A90E2;
        text-decoration: none;
    }
    
    a:hover {
        color: #67A8F0;
        text-decoration: underline;
    }
    
    /* Code blocks */
    code {
        background-color: #1A1D24;
        padding: 0.15rem 0.35rem;
        border-radius: 0.25rem;
        color: #4A90E2;
        font-size: 0.875em;
        border: 1px solid #262933;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem;
        font-weight: 500;
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
                "# Welcome to EduMate\n\n"
                "I'm your AI Module Convenor Assistant, here to provide personalized academic guidance and support.\n\n"
                "## How I Can Help\n\n"
                "**Understanding Concepts** — Clear explanations of theories and course material\n\n"
                "**Assignment Guidance** — Structured guidance on coursework and rubric interpretation\n\n"
                "**Exam Preparation** — Effective study strategies and topic prioritization\n\n"
                "**Study Planning** — Time management and learning techniques\n\n"
                "**Progress Feedback** — Constructive advice and improvement suggestions\n\n"
                "---\n\n"
                "I remember our conversation context, so feel free to ask follow-up questions.\n\n"
                "Ask me anything about your coursework to get started."
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
            <h1 style="margin: 0;">EduMate</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

col_subtitle, col_new_chat = st.columns([5, 1])
with col_subtitle:
    st.markdown(
        '<p style="color: #A0A0A0; font-size: 1rem; margin-top: -0.5rem; margin-bottom: 1rem;">AI Module Convenor • Personalized Academic Guidance</p>', 
        unsafe_allow_html=True
    )
with col_new_chat:
    if st.button("New Chat", help="Start a fresh conversation", use_container_width=True, type="primary"):
        st.session_state.messages = [st.session_state.messages[0]]  # keep only welcome message
        st.session_state.session_id = str(uuid.uuid4())
        st.success("New conversation started")
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

if user_input := st.chat_input("Ask me anything about your course..."):
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
                    st.markdown("---")
                    with st.expander("View Sources & References", expanded=False):
                        st.markdown("*Sources used to generate the response:*")
                        st.markdown("")
                        for i, s in enumerate(sources, 1):
                            # Turn plain URLs into clickable links with better formatting
                            if isinstance(s, str) and (s.startswith("http://") or s.startswith("https://")):
                                st.markdown(f"**{i}.** [{s}]({s})")
                            else:
                                st.markdown(f"**{i}.** {s}")

                # Persist assistant reply
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.api_status = "online"

            except requests.exceptions.ConnectionError:
                error_msg = (
                    "## Connection Error\n\n"
                    f"Cannot connect to the backend API at:\n\n"
                    f"`{API_BASE_URL}`\n\n"
                    "### Possible Causes\n"
                    "- Backend server is not running or unavailable\n"
                    "- Incorrect API URL configuration\n"
                    "- Network connectivity issues\n\n"
                    "### What You Can Do\n"
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
                    "## Request Timeout\n\n"
                    "The request took too long to complete (>120 seconds).\n\n"
                    "### What You Can Do\n"
                    "1. Try asking a simpler or more specific question\n"
                    "2. Wait a moment and try again\n"
                    "3. The backend may be warming up after being idle\n"
                    "4. Check your internet connection"
                )
                st.warning(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.HTTPError as e:
                try:
                    detail = e.response.text[:300]
                except Exception:
                    detail = ""
                error_msg = (
                    f"## API Error (Status: {e.response.status_code})\n\n"
                    f"The backend returned an error.\n\n"
                    f"**Details:** {detail if detail else 'No additional information available'}\n\n"
                    "### What You Can Do\n"
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
                    "## Unexpected Error\n\n"
                    f"Something went wrong:\n\n"
                    f"```\n{str(e)}\n```\n\n"
                    "### What You Can Do\n"
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
    st.markdown("## EduMate Assistant")
    st.markdown("*AI-Powered Academic Guide*")
    
    st.divider()
    
    # About section
    with st.expander("About EduMate", expanded=False):
        st.markdown(
            """
EduMate is an intelligent AI assistant that acts as your personal 
module convenor, providing tailored academic guidance and mentorship.

### Why Choose EduMate?

- **Smart Context Awareness** — Remembers your conversation
- **Evidence-Based Answers** — Cites actual course documents
- **Academic Excellence** — Follows educational best practices
- **Privacy Protected** — Fully anonymized sessions
- **Always Available** — 24/7 academic support
"""
        )
    
    st.divider()

    # What I Can Help With section
    with st.expander("What I Can Help With", expanded=True):
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
    st.markdown("### System Status")
    
    status_col1, status_col2 = st.columns([1, 3])
    
    try:
        health_response = requests.get(api("/health"), timeout=5)
        if health_response.status_code == 200:
            with status_col1:
                st.markdown("✓")
            with status_col2:
                st.markdown("**Online**")
            st.session_state.api_status = "online"
        else:
            with status_col1:
                st.markdown("⚠")
            with status_col2:
                st.markdown(f"**Status {health_response.status_code}**")
            st.session_state.api_status = "warning"
    except requests.exceptions.Timeout:
        with status_col1:
            st.markdown("⏱")
        with status_col2:
            st.markdown("**Timeout**")
        st.session_state.api_status = "timeout"
    except Exception:
        with status_col1:
            st.markdown("✗")
        with status_col2:
            st.markdown("**Offline**")
        st.session_state.api_status = "offline"

    st.caption(f"API: `{API_BASE_URL[:30]}...`" if len(API_BASE_URL) > 30 else f"API: `{API_BASE_URL}`")
    
    st.divider()

    # Session Info
    st.markdown("### Current Session")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric("Messages", len(st.session_state.messages))
    with info_col2:
        st.metric("Session", f"#{st.session_state.session_id[:8]}")
    
    st.divider()

    # Action buttons with better design
    if st.button("Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "# Welcome Back\n\n"
                    "I'm your AI Module Convenor Assistant. "
                    "I can help you with course concepts, assignments, exam prep, and study planning.\n\n"
                    "What would you like to work on today?"
                ),
            }
        ]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # Quick Tips
    with st.expander("Quick Tips", expanded=False):
        st.markdown(
            """
- Ask specific questions about your coursework
- Request detailed guidance on assignments
- Get comprehensive exam preparation strategies
- Ask follow-up questions for deeper understanding
- Check sources in the expandable section below answers
"""
        )

    st.divider()

    # Technology stack
    with st.expander("Powered By", expanded=False):
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

**Total Cost: $0/month base**
*(Pay only for API usage)*
"""
        )
