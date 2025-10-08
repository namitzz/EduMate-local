# Manual Testing Guide for Error Handling

This guide provides step-by-step instructions for manually testing the improved error handling in EduMate.

## Prerequisites

- EduMate backend and UI running
- Access to terminal for backend operations
- Ollama installed (for testing connection issues)
- Sample documents in corpus/ folder

## Test Setup

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
uvicorn main:app --reload --port 8000

# Terminal 2: UI
cd ui
source .venv/bin/activate
streamlit run app_simple.py --server.port 8501
```

---

## Test 1: NO_CONTEXT Error

**Goal:** Verify the system properly handles queries with no relevant documents.

### Steps:
1. Ensure your corpus has specific content (e.g., Python programming docs)
2. Open UI at http://localhost:8501
3. Ask a question about unrelated content: "What is the capital of France?"
4. Observe the response

### Expected Result:
```
I couldn't find relevant information in the course materials for your question.

**Suggestions:**
• Try rephrasing your question with different keywords
• Ask about topics that are covered in the uploaded documents
• Check if documents have been ingested (run `python ingest.py`)
• Make your question more specific to the course content
```

### Pass Criteria:
- ✅ Message clearly states no content was found
- ✅ Provides specific suggestions
- ✅ No sources displayed
- ✅ No technical errors or stack traces shown

### Backend Logs to Check:
```
[DEBUG] Retrieved context preview: []
# or empty context list
```

---

## Test 2: RETRIEVAL_ERROR

**Goal:** Test error handling when the vector database is not initialized.

### Steps:
1. Stop the backend (Ctrl+C in Terminal 1)
2. Delete the vector database:
   ```bash
   cd backend
   rm -rf chroma_db/
   ```
3. Start the backend again (without running `python ingest.py`)
4. Ask a question in the UI

### Expected Result:
```
There was an error searching through the course materials.

**Possible causes:**
• The vector database may not be initialized
• Documents may not have been ingested yet

**What to do:**
• Run `python ingest.py` in the backend directory
• Check that documents exist in the corpus/ folder
• Restart the backend server if the issue persists
```

### Pass Criteria:
- ✅ Clear error message about database issue
- ✅ Actionable steps provided
- ✅ No crash or unhelpful Python traceback shown to user

### Backend Logs to Check:
```
[ERROR] Retrieval error: ...
[ERROR DETAILS] retrieval_error: ...
```

### Cleanup:
```bash
cd backend
python ingest.py  # Re-create vector database
```

---

## Test 3: MODEL_CONNECTION Error

**Goal:** Test handling when Ollama is not running.

### Steps:
1. Stop Ollama:
   ```bash
   # On Linux/Mac:
   pkill ollama
   
   # On Docker:
   docker stop <ollama-container-name>
   ```
2. Verify Ollama is stopped: `ollama list` should fail
3. Ask a question in the UI

### Expected Result:
```
Unable to connect to the AI model (Ollama).

**Possible causes:**
• Ollama service is not running
• Connection to Ollama was refused

**What to do:**
• Check if Ollama is running: `ollama list`
• Start Ollama if needed
• Verify OLLAMA_HOST configuration
• If using Docker, ensure the ollama container is running
```

### Pass Criteria:
- ✅ Clear message about connection issue
- ✅ Specific steps to check and fix
- ✅ No confusing technical jargon

### Backend Logs to Check:
```
[WARNING] Ollama ConnectionError on attempt 1/3: ...
[WARNING] Ollama ConnectionError on attempt 2/3: ...
[WARNING] Ollama ConnectionError on attempt 3/3: ...
[ERROR] Ollama call error: RuntimeError('Ollama ConnectionError after 3 retries: ...')
```

### Cleanup:
```bash
# Restart Ollama
ollama serve  # or docker start <ollama-container-name>
```

---

## Test 4: MODEL_TIMEOUT Error

**Goal:** Test timeout handling.

### Steps:
1. Edit `backend/models.py` temporarily:
   ```python
   # Find this line:
   r = requests.post(f"{url}/api/generate", json=payload, timeout=180)
   
   # Change to:
   r = requests.post(f"{url}/api/generate", json=payload, timeout=1)
   ```
2. Restart the backend (it will reload automatically with `--reload` flag)
3. Ask a complex question that would take time to answer

### Expected Result:
```
The AI model took too long to respond (timeout).

**Possible causes:**
• The model is overloaded or slow
• Your question may be too complex
• The model might be loading for the first time

**What to do:**
• Try asking a simpler question
• Wait a moment and try again (the model may be warming up)
• Consider using a faster model like `qwen2.5:1.5b-instruct`
```

### Pass Criteria:
- ✅ Timeout is detected and reported clearly
- ✅ Helpful suggestions provided
- ✅ User understands it's a timeout issue, not a bug

### Backend Logs to Check:
```
[WARNING] Ollama ReadTimeout on attempt 1/3: ...
[WARNING] Ollama ReadTimeout on attempt 2/3: ...
[WARNING] Ollama ReadTimeout on attempt 3/3: ...
[ERROR] Ollama call error: RuntimeError('Ollama ReadTimeout after 3 retries: ...')
```

### Cleanup:
```bash
# Restore the timeout to 180 in backend/models.py
# Backend will auto-reload
```

---

## Test 5: MODEL_EMPTY_RESPONSE Error (with sources)

**Goal:** Test handling when Ollama returns empty response but context was found.

### Steps (Requires Code Modification):
1. Edit `backend/models.py` temporarily:
   ```python
   # Find in ollama_complete():
   if text:
       return text
   
   # Change to:
   if text:
       return ""  # Force empty response for testing
   ```
2. Restart backend
3. Ask a question that should have an answer

### Expected Result:
```
The AI model returned an empty response.

I found relevant information in the course materials, but the model
failed to generate an answer. This could be a temporary issue.

**What to do:**
• Try rephrasing your question
• Check the sources below for relevant information
• Try again in a moment
• If this persists, restart the backend server
```

### Pass Criteria:
- ✅ Empty response detected
- ✅ Sources still displayed
- ✅ Guidance provided

### Backend Logs to Check:
```
[WARNING] Ollama returned empty answer string
[ERROR DETAILS] model_empty_response: ...
```

### Cleanup:
```bash
# Remove the test modification from backend/models.py
# Backend will auto-reload
```

---

## Test 6: Greeting Detection (Not an Error)

**Goal:** Verify greetings bypass retrieval and work correctly.

### Steps:
1. Send "hello" in the UI
2. Send "hi there"
3. Send "what's up"

### Expected Result:
```
Hello! I'm EduMate, your study assistant.
I'm here to help you with questions about your course materials.
What would you like to know?
```

### Pass Criteria:
- ✅ Greeting response is immediate
- ✅ No retrieval attempted (check logs)
- ✅ Friendly, welcoming message

### Backend Logs to Check:
```
# Should NOT see:
[DEBUG] Retrieved context preview: ...
```

---

## Test 7: Successful Query (Baseline)

**Goal:** Verify normal operation still works correctly.

### Steps:
1. Ensure Ollama is running and documents are ingested
2. Ask a question about content in your documents
3. Example: "What is a variable in Python?" (if you have Python docs)

### Expected Result:
- Answer is generated based on course materials
- Sources are displayed
- Response is relevant and helpful

### Pass Criteria:
- ✅ Answer generated successfully
- ✅ Sources shown
- ✅ No error messages

### Backend Logs to Check:
```
[DEBUG] Retrieved context preview: [...]
[DEBUG] Prompt head: ...
[DEBUG] Ollama response length: XXX chars
```

---

## Test 8: Streaming Endpoint (/chat_stream)

**Goal:** Verify error handling works in streaming mode.

### Prerequisites:
- Use `app_public.py` UI which supports streaming

### Steps:
1. Test each error scenario above with streaming UI
2. Verify errors stream correctly (not truncated)
3. Check error messages appear progressively

### Pass Criteria:
- ✅ Error messages stream properly
- ✅ No UI freezing
- ✅ Messages remain formatted

---

## Test 9: Retry Logic

**Goal:** Verify the retry mechanism works correctly.

### Steps:
1. Temporarily make Ollama flaky (e.g., stop and quickly restart during a query)
2. Watch backend logs for retry attempts

### Expected Backend Logs:
```
[WARNING] Ollama ConnectionError on attempt 1/3: ...
# (2s delay)
[WARNING] Ollama ConnectionError on attempt 2/3: ...
# (4s delay)
[WARNING] Ollama ConnectionError on attempt 3/3: ...
# OR success after retry:
[DEBUG] Ollama response length: XXX chars
```

### Pass Criteria:
- ✅ System retries 3 times
- ✅ Delays increase (2s, 4s, 6s)
- ✅ Success on retry doesn't show error to user
- ✅ All attempts logged

---

## Test 10: Multiple Concurrent Requests

**Goal:** Verify error handling under load.

### Steps:
1. Open multiple browser tabs with the UI
2. Send questions simultaneously from each tab
3. Include mix of error scenarios and valid queries

### Pass Criteria:
- ✅ Each request gets appropriate response
- ✅ Errors don't affect other requests
- ✅ No crashes or hangs

---

## Checklist Summary

Use this checklist to track your testing progress:

- [ ] Test 1: NO_CONTEXT - Unrelated question
- [ ] Test 2: RETRIEVAL_ERROR - No vector DB
- [ ] Test 3: MODEL_CONNECTION - Ollama stopped
- [ ] Test 4: MODEL_TIMEOUT - Timeout forced
- [ ] Test 5: MODEL_EMPTY_RESPONSE - Empty response forced
- [ ] Test 6: Greeting Detection - Greeting bypass
- [ ] Test 7: Successful Query - Normal operation
- [ ] Test 8: Streaming Endpoint - Streaming errors
- [ ] Test 9: Retry Logic - Retry mechanism
- [ ] Test 10: Concurrent Requests - Load testing

---

## Reporting Issues

If you find issues during testing:

### For Users:
1. Note which test failed
2. Copy the exact error message shown
3. Check what you expected vs. what you got
4. Report on GitHub Issues

### For Developers:
1. Capture backend logs (full output)
2. Note the exact steps to reproduce
3. Check if error classification is correct
4. Check if error message is helpful
5. Consider if new error type is needed

---

## Automated Testing

While manual testing is important, also run automated tests:

```bash
cd backend
python test_error_handling.py
```

Note: Some tests may fail in environments without network access. The core error classification tests should pass.

---

## Tips for Testers

1. **Test in order**: Start with Test 1 and work through sequentially
2. **Clean up**: Always run cleanup steps to restore normal operation
3. **Check logs**: Backend logs provide crucial debugging info
4. **Be thorough**: Test edge cases and unusual inputs
5. **Document**: Note any unexpected behavior
6. **Reset state**: Restart backend between major tests if needed

---

## Success Criteria for Error Handling

Overall, the error handling is successful if:

✅ Users never see Python tracebacks or technical errors
✅ Every error message is clear and actionable
✅ Users know what went wrong and what to do
✅ Errors are properly logged for debugging
✅ System degrades gracefully (no crashes)
✅ Retry logic works transparently
✅ Sources are shown when available, even with errors

---

**Last Updated**: 2024
**Version**: 1.0
**Author**: EduMate Team
