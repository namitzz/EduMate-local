import os, requests, streamlit as st

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="EduMate", page_icon="🎓", layout="wide")
st.title("EduMate — Local, Pre-loaded RAG (No Uploads)")

with st.sidebar:
    st.markdown("### Sources")
    src_box = st.empty()
    st.divider()
    st.markdown("**Note:** This assistant only uses the instructor-provided documents. Uploads are disabled.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me anything about your course materials."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Type your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{API_BASE}/chat", json={"messages": st.session_state.messages}, timeout=120)
                r.raise_for_status()
                data = r.json()
                st.markdown(data["answer"])
                with st.sidebar:
                    src_box.markdown("\n".join(f"- {s}" for s in data.get("sources", [])))
                st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
            except Exception as e:
                st.error(f"API error: {e}")
