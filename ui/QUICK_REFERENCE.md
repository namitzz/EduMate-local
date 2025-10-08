# Quick Reference: app_simple.py

A one-page reference for the simple Streamlit app.

## File Location
```
/home/runner/work/EduMate-local/EduMate-local/ui/app_simple.py
```

## Quick Start
```bash
cd ui
streamlit run app_simple.py
```

## Dependencies
```python
import os          # Environment variables
import streamlit   # UI framework
import requests    # API calls
```

## Configuration
```python
API_BASE_URL = os.environ.get("API_BASE", "http://localhost:8000")
```

## Key Features

| Feature | Code Location | Description |
|---------|---------------|-------------|
| Chat History | Line 47-49 | Session state initialization |
| Display Messages | Line 54-57 | Loop through messages |
| User Input | Line 64 | `st.chat_input()` |
| API Call | Line 83-86 | POST to `/chat` |
| Sources | Line 96-99 | Expander with sources |
| Error Handling | Line 105-124 | Try/except blocks |
| Health Check | Line 140-149 | GET `/health` |
| Clear Chat | Line 159-166 | Reset session state |

## API Endpoints Used

### POST /chat
```python
requests.post(
    f"{API_BASE_URL}/chat",
    json={"messages": st.session_state.messages},
    timeout=120
)
```

**Response:**
```json
{
    "answer": "string",
    "sources": ["source1", "source2"]
}
```

### GET /health
```python
requests.get(f"{API_BASE_URL}/health", timeout=5)
```

**Response:**
```json
{
    "ok": true
}
```

## Session State Structure

```python
st.session_state.messages = [
    {
        "role": "assistant",  # or "user"
        "content": "message text"
    },
    # ... more messages
]
```

## Message Flow

1. User types in `st.chat_input()`
2. Message added to `st.session_state.messages`
3. User message displayed with `st.chat_message("user")`
4. API called with POST `/chat`
5. Response parsed for `answer` and `sources`
6. Assistant message displayed with `st.chat_message("assistant")`
7. Assistant message added to `st.session_state.messages`

## Error Types

| Error | Catch | User Message |
|-------|-------|--------------|
| Connection | `requests.exceptions.ConnectionError` | "Cannot connect to API" |
| Timeout | `requests.exceptions.Timeout` | "Request timed out" |
| Generic | `Exception` | "Error: {message}" |

## UI Components

### Header
```python
st.title("🎓 EduMate - Your Study Assistant")
st.caption("Ask me anything about your course materials!")
```

### Chat Message
```python
with st.chat_message("user"):  # or "assistant"
    st.markdown(message["content"])
```

### Spinner
```python
with st.spinner("Thinking..."):
    # Long-running operation
```

### Expander
```python
with st.expander("📚 Sources"):
    for source in sources:
        st.markdown(f"- {source}")
```

### Sidebar
```python
with st.sidebar:
    st.header("ℹ️ About")
    # sidebar content
```

### Button
```python
if st.button("🗑️ Clear Chat History", use_container_width=True):
    # button action
    st.rerun()
```

## Customization Quick Tips

### Change API URL
```python
# In code:
API_BASE_URL = "http://192.168.1.10:8000"

# Or via environment:
export API_BASE=http://192.168.1.10:8000
```

### Change Page Title
```python
st.set_page_config(
    page_title="My Custom Title",
    page_icon="📖"
)
```

### Add Custom Message
```python
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Your custom greeting here!"
        }
    ]
```

### Modify Timeout
```python
response = requests.post(
    f"{API_BASE_URL}/chat",
    json={"messages": st.session_state.messages},
    timeout=60  # Changed from 120
)
```

### Add More Error Details
```python
except Exception as e:
    error_msg = f"❌ Error: {str(e)}\nType: {type(e).__name__}"
    st.error(error_msg)
```

## Common Modifications

### 1. Add Streaming Support
```python
# Use /chat_stream endpoint
with requests.post(
    f"{API_BASE_URL}/chat_stream",
    json={"messages": st.session_state.messages, "mode": "docs"},
    stream=True
) as response:
    for chunk in response.iter_content(decode_unicode=True):
        # Display chunk
```

### 2. Add Mode Selector
```python
mode = st.radio("Mode:", ["docs", "coach", "facts"])
payload = {"messages": st.session_state.messages, "mode": mode}
```

### 3. Add File Upload
```python
uploaded_file = st.file_uploader("Upload document")
if uploaded_file:
    # Handle file
```

### 4. Export Chat
```python
if st.button("Export Chat"):
    chat_text = "\n\n".join(
        f"{m['role']}: {m['content']}" 
        for m in st.session_state.messages
    )
    st.download_button("Download", chat_text, "chat.txt")
```

### 5. Add User Feedback
```python
col1, col2 = st.columns(2)
with col1:
    if st.button("👍"):
        st.success("Thanks for feedback!")
with col2:
    if st.button("👎"):
        st.info("Sorry! Try rephrasing?")
```

## Debugging Tips

### View Session State
```python
st.sidebar.write("Debug:", st.session_state)
```

### Log API Calls
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Calling API with {len(st.session_state.messages)} messages")
```

### Test API Manually
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hello"}]}'
```

### Check Streamlit Version
```bash
streamlit --version
```

### Clear Cache
```bash
streamlit cache clear
```

## Performance Tips

1. **Reduce timeout** for faster error feedback
2. **Add caching** for repeated API calls:
   ```python
   @st.cache_data(ttl=300)
   def call_api(message):
       # API call
   ```
3. **Lazy load** components only when needed
4. **Minimize reruns** by using session state effectively

## Security Considerations

1. **Don't hardcode credentials**
   ```python
   # Bad
   API_KEY = "secret123"
   
   # Good
   API_KEY = os.getenv("API_KEY")
   ```

2. **Validate inputs**
   ```python
   if len(user_input) > 1000:
       st.error("Message too long")
       return
   ```

3. **Use HTTPS in production**
   ```python
   API_BASE_URL = "https://api.example.com"
   ```

4. **Set timeouts**
   ```python
   timeout=120  # Prevent hanging requests
   ```

## Testing Commands

```bash
# Syntax check
python -m py_compile app_simple.py

# Run tests (if any)
pytest tests/test_ui.py

# Start with debug logging
streamlit run app_simple.py --logger.level=debug

# Start on different port
streamlit run app_simple.py --server.port 8502
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE` | `http://localhost:8000` | Backend API URL |
| `STREAMLIT_SERVER_PORT` | `8501` | UI port |
| `STREAMLIT_SERVER_ADDRESS` | `localhost` | Bind address |

## File Structure

```
ui/
├── app_simple.py          # This file
├── app.py                 # Original UI
├── app_public.py          # Advanced UI
├── requirements.txt       # Dependencies
├── README_SIMPLE.md       # Documentation
├── TESTING_GUIDE.md       # Testing guide
└── VISUAL_GUIDE.md        # Visual reference
```

## Related Files

- **Backend**: `/backend/main.py` - API endpoints
- **Config**: `/backend/config.py` - Configuration
- **Docs**: `/README.md` - Main documentation

## Support

- 📖 Full docs: [README_SIMPLE.md](README_SIMPLE.md)
- 🧪 Testing: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- 👁️ Visual guide: [VISUAL_GUIDE.md](VISUAL_GUIDE.md)
- 📚 Main docs: [../README.md](../README.md)

## Version Info

- **App Version**: 1.0
- **Streamlit**: 1.37.1
- **Python**: 3.8+

---

**Last Updated**: 2024  
**Maintainer**: EduMate Team
