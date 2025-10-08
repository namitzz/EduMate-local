# Testing Guide for app_simple.py

## Overview

This guide explains how to test the simple Streamlit app with the EduMate backend.

## Prerequisites

### 1. Backend Setup

The backend must be running before testing the UI:

```bash
# Terminal 1: Start the backend
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python ingest.py  # Index documents from corpus/
uvicorn main:app --reload --port 8000
```

### 2. Ollama Setup

Ensure Ollama is installed and running:

```bash
# Install Ollama from https://ollama.com
ollama pull mistral  # or any model of your choice
```

### 3. UI Setup

```bash
# Terminal 2: Start the UI
cd ui
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app_simple.py
```

## Manual Testing Checklist

### ✅ Basic Functionality

- [ ] App loads at http://localhost:8501
- [ ] Title displays "🎓 EduMate - Your Study Assistant"
- [ ] Initial assistant message appears
- [ ] Chat input box is visible
- [ ] Sidebar shows "About" section

### ✅ API Health Check

- [ ] Sidebar shows API status
- [ ] Status is "✅ API is online" when backend is running
- [ ] Status is "❌ API is offline" when backend is not running
- [ ] API URL displays correctly (http://localhost:8000)

### ✅ Chat Functionality

1. **Simple Question Test**
   - [ ] Type "Hello" and press Enter
   - [ ] Response appears within a few seconds
   - [ ] Response is friendly and relevant
   - [ ] Message appears in chat history

2. **RAG Query Test**
   - [ ] Ask a question about course materials (e.g., "What is machine learning?")
   - [ ] Response appears with relevant content
   - [ ] Sources expander appears
   - [ ] Clicking sources shows document references
   - [ ] Message is added to chat history

3. **Multiple Messages Test**
   - [ ] Send 3-4 messages in sequence
   - [ ] All messages appear in chat history
   - [ ] Conversation context is maintained
   - [ ] UI remains responsive

### ✅ Error Handling

1. **Backend Down Test**
   - [ ] Stop the backend (Ctrl+C in Terminal 1)
   - [ ] Try sending a message
   - [ ] Error message appears: "Cannot connect to the API"
   - [ ] Error is user-friendly
   - [ ] Sidebar shows "❌ API is offline"

2. **Timeout Test**
   - [ ] Send a very complex query
   - [ ] If timeout occurs, appropriate message appears
   - [ ] UI doesn't crash

### ✅ UI Controls

1. **Clear Chat Test**
   - [ ] Send a few messages
   - [ ] Click "🗑️ Clear Chat History" in sidebar
   - [ ] Chat resets to initial assistant message
   - [ ] No previous messages remain

2. **Session Persistence Test**
   - [ ] Send a few messages
   - [ ] Refresh the page (F5)
   - [ ] Chat history is lost (expected behavior)
   - [ ] Initial message appears again

### ✅ Responsive Design

- [ ] Resize browser window
- [ ] UI adapts to different widths
- [ ] Chat remains usable on smaller screens
- [ ] Sidebar is accessible

## Automated Testing

### Python Syntax Check

```bash
cd ui
python -m py_compile app_simple.py
echo "✓ Syntax check passed"
```

### Import Check

```bash
cd ui
python -c "
import streamlit
import requests
import os
print('✓ All imports successful')
"
```

### Code Quality Check (Optional)

If you have pylint or flake8 installed:

```bash
cd ui
pylint app_simple.py --disable=C0111,C0103
# or
flake8 app_simple.py --max-line-length=120
```

## Expected Behavior

### Normal Operation

1. **Startup**: App loads in 2-3 seconds
2. **API Check**: Health check completes in < 1 second
3. **Simple Query**: Response in 2-4 seconds
4. **Complex Query**: Response in 4-8 seconds
5. **Greeting**: Response in < 1 second

### Error States

1. **No Backend**: Clear error message, no crash
2. **Timeout**: User-friendly timeout message
3. **Empty Response**: Handles gracefully

## Performance Expectations

| Scenario | Expected Time | Acceptable Range |
|----------|---------------|------------------|
| Page Load | 2-3 seconds | 1-5 seconds |
| Health Check | < 1 second | < 2 seconds |
| Greeting Response | < 1 second | < 2 seconds |
| Simple Query | 2-4 seconds | 1-6 seconds |
| Complex Query | 4-8 seconds | 3-12 seconds |

## Troubleshooting Testing Issues

### Issue: App Won't Start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
cd ui
pip install -r requirements.txt
```

### Issue: Cannot Connect to API

**Error**: "Cannot connect to the API"

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Should return: `{"ok":true}`
3. If not, start backend in Terminal 1

### Issue: Slow Responses

**Possible Causes**:
- Large number of documents
- Slow Ollama model
- Limited system resources

**Solution**:
1. Try smaller model: `ollama pull qwen2.5:1.5b-instruct`
2. Enable Fast Mode: `export FAST_MODE=1` in backend
3. Reduce corpus size temporarily

### Issue: Empty Responses

**Possible Causes**:
- No documents ingested
- Ollama not running

**Solution**:
```bash
# Check Ollama
ollama list

# Re-ingest documents
cd backend
python ingest.py
```

## Testing Scenarios

### Scenario 1: First-Time User

1. Clone repository
2. Follow Quick Start in README
3. Open app
4. Ask "What can you help me with?"
5. Verify friendly, informative response

### Scenario 2: Student Using for Study

1. Ask course-specific question
2. Verify relevant answer with sources
3. Ask follow-up question
4. Verify context is maintained
5. Check sources for references

### Scenario 3: Multiple Concurrent Users

1. Open app in 2-3 browser windows
2. Send questions from each
3. Verify each session is independent
4. No cross-contamination of chat history

### Scenario 4: Network Issues

1. Start app with backend running
2. Stop backend mid-conversation
3. Try to send message
4. Verify graceful error handling
5. Restart backend
6. Verify recovery

## Comparison Testing

### Test All Three UIs

Compare behavior across different UIs:

```bash
# Terminal 1: Backend (same for all)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Test each UI
cd ui
streamlit run app_simple.py --server.port 8501    # Simple UI
streamlit run app.py --server.port 8502           # Original UI
streamlit run app_public.py --server.port 8503    # Advanced UI
```

**Compare**:
- Response format
- Source display
- Error handling
- Overall UX

## Success Criteria

The app passes testing if:

✅ All basic functionality tests pass
✅ Error handling is graceful and user-friendly
✅ Performance is within acceptable ranges
✅ UI is responsive and intuitive
✅ Code is clean and well-commented
✅ Documentation is clear and helpful

## Reporting Issues

If you find issues:

1. Note the exact steps to reproduce
2. Include error messages
3. Check browser console for JavaScript errors (F12)
4. Include backend logs if relevant
5. Note your environment (OS, Python version, etc.)

## Continuous Testing

For ongoing development:

1. Test after each code change
2. Verify existing functionality still works
3. Add new test cases for new features
4. Update this guide as needed

---

**Last Updated**: 2024
**Version**: 1.0
**Author**: EduMate Team
