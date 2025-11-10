"""
EduMate Module Convenor Assistant - Streamlit App
=================================================

Frontend for EduMate: an AI academic guidance assistant.

- Frontend: Streamlit Cloud
- Backend: Fly.io FastAPI
- LLM: OpenRouter via backend
"""

import os
import json
import uuid
import requests
import streamlit as st
from urllib.parse import urljoin

# ============================================================================
# Configuration
# ============================================================================

# API base: can be overridden by env or query param
DEFAULT_API_BASE = "https://edumate-local-api.fly.dev"
api_from_env = os.getenv("EDUMATE_API_BASE")
api_from_query = st.query_params.get("api") if hasattr(st, "query_params") else None
API_BASE_URL = (api_from_query or api_from_env or DEFAULT_API_BASE).rstrip("/")

# Working model (the one verified with curl)
WORKING_MODEL = os.getenv("EDUMATE_MODEL", st.query_params.get("model", "openai/gpt-4o-mini"))

def api(path: str) -> str:
    """Helper to safely join API URLs"""
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

# ============================================================================
# Session Initialization
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "# 👋 Welcome to EduMate!\n\n"
                "I'm your **AI Module Convenor Assistant** — here to provide personalized academic guidance and support.\n\n"
                "💡 **Tip:** I remember our conversation, so feel free to ask follow-up questions!"
            ),
        }
    ]

# ============================================================================
# Header
# ============================================================================

st.markdown(
    """
    <h1 style='text-align: center;'>🎓 EduMate</h1>
    <p style='text-align: center; color: #6c757d;'>Your AI Module Convenor • Personalized Academic Guidance</p>
    """,
    unsafe_allow_html=True
)

if st.button("🔄 New Chat", use_container_width=True):
    st.session_state.messages = [st.session_state.messages[0]]
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
# Chat Input + Streaming Response
# ============================================================================

if user_input := st.chat_input("💬 Ask me anything about your course..."):
    # Save user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response (streaming)
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                payload = {
                    "model": WORKING_MODEL,
                    "messages": st.session_state.messages,
                    "temperature": 0.2,
                }

                resp = requests.post(
                    api("/chat"),
                    json=payload,
                    timeout=120,
                    stream=True,
                )
                resp.raise_for_status()

                full = ""
                placeholder = st.empty()

                for line in resp.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            full += token
                            placeholder.markdown(full)
                    except Exception:
                        continue

                answer = full if full.strip() else "I couldn't generate a response."
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to backend API at `{API_BASE_URL}`. Check if it's running.")
            except requests.exceptions.Timeout:
                st.warning("⏱️ The request took too long (>120s). Try again or simplify your query.")
            except requests.HTTPError as e:
                st.error(f"❌ API Error ({e.response.status_code}): {e.response.text[:400]}")
            except Exception as e:
                st.error(f"❌ Unexpected Error:\n```\n{str(e)}\n```")

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ System Status")

    try:
        health = requests.get(api("/health"), timeout=5)
        if health.status_code == 200:
            st.success("Backend Online ✅")
        else:
            st.warning(f"Backend Responded: {health.status_code}")
    except Exception:
        st.error("Backend Offline ❌")

    st.caption(f"🌐 API: `{API_BASE_URL}`")
    st.caption(f"🤖 Model: `{WORKING_MODEL}`")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
