import os
import streamlit as st
import requests
import re

# Configuration
API_BASE = os.environ.get("EDUMATE_API_URL", os.environ.get("API_BASE", "http://localhost:8000"))

# Page config
st.set_page_config(
    page_title="EduMate – Study Assistant",
    page_icon="🎓",
    layout="centered"
)

# Header with optional logo
logo_path = "static/logo.png"
if os.path.exists(logo_path):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo_path, width=80)
    with col2:
        st.title("EduMate")
        st.caption("Your AI Study Assistant")
else:
    st.title("🎓 EduMate – Study Assistant")

# Mode selector (segmented control style using radio)
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    mode_docs = st.button("📚 Ask Course Docs", use_container_width=True, type="primary" if st.session_state.get("mode", "docs") == "docs" else "secondary")
with col2:
    mode_coach = st.button("💡 Study Coach", use_container_width=True, type="primary" if st.session_state.get("mode", "docs") == "coach" else "secondary")
with col3:
    mode_facts = st.button("⚡ Quick Facts", use_container_width=True, type="primary" if st.session_state.get("mode", "docs") == "facts" else "secondary")

# Handle mode selection
if mode_docs:
    st.session_state.mode = "docs"
if mode_coach:
    st.session_state.mode = "coach"
if mode_facts:
    st.session_state.mode = "facts"

# Initialize mode if not set
if "mode" not in st.session_state:
    st.session_state.mode = "docs"

# Evidence mode toggle (only show in docs mode)
if st.session_state.mode == "docs":
    with st.expander("⚙️ Settings"):
        evidence_mode = st.checkbox("Evidence mode (show citation warnings)", value=st.session_state.get("evidence_mode", False))
        st.session_state.evidence_mode = evidence_mode
        st.caption("When enabled, shows a note if the answer doesn't include source citations.")

st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display mode info
mode_names = {"docs": "Course Documents", "coach": "Study Coach", "facts": "Quick Facts"}
mode_descriptions = {
    "docs": "Ask questions about your course materials. Answers are grounded in the documents.",
    "coach": "Get study tips, learning strategies, and motivational support.",
    "facts": "Quick, concise answers to factual questions."
}

if not st.session_state.messages:
    st.info(f"**Mode: {mode_names[st.session_state.mode]}**\n\n{mode_descriptions[st.session_state.mode]}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Prepare request with current mode
            payload = {
                "messages": st.session_state.messages,
                "mode": st.session_state.mode
            }

            # Stream response from API
            with requests.post(
                f"{API_BASE}/chat_stream",
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                response.raise_for_status()
                
                # Stream tokens as they arrive
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                
                # Remove cursor and show final response
                message_placeholder.markdown(full_response)

            # Evidence mode check (only in docs mode)
            if st.session_state.mode == "docs" and st.session_state.get("evidence_mode", False):
                # Check if response has citation markers [①, ②, etc.]
                has_citations = bool(re.search(r'\[[\u2460-\u2469]\]', full_response))
                if not has_citations:
                    st.caption("ℹ️ This answer may use general knowledge. Add module docs to cite sources.")

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"Error: {e}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button in sidebar
with st.sidebar:
    st.markdown("### Chat Controls")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **EduMate** is your AI-powered study assistant that helps you:
    - 📚 Find answers in course materials
    - 💡 Get study tips and strategies
    - ⚡ Quick factual information
    
    Switch between modes using the buttons above!
    """)
