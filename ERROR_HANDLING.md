# Error Handling Improvements Documentation

## Overview

EduMate's error handling has been significantly improved to provide users with specific, actionable feedback when issues occur. Instead of generic error messages, users now receive detailed guidance based on the type of error that occurred.

## Error Types

The system now classifies errors into 7 specific types:

### 1. NO_CONTEXT
**When it occurs:** No relevant information found in the course materials.

**User sees:**
```
I couldn't find relevant information in the course materials for your question.

**Suggestions:**
• Try rephrasing your question with different keywords
• Ask about topics that are covered in the uploaded documents
• Check if documents have been ingested (run `python ingest.py`)
• Make your question more specific to the course content
```

**Common causes:**
- User asking about topics not in the corpus
- Query too vague or uses uncommon terminology
- No documents have been ingested yet

**How to fix:**
- Rephrase the question
- Ensure documents are in the corpus/ folder
- Run `python ingest.py` to build the vector index

---

### 2. RETRIEVAL_ERROR
**When it occurs:** Error during the retrieval process (searching the vector database).

**User sees:**
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

**Common causes:**
- ChromaDB not initialized
- Corrupt vector database
- Embedding model issues

**How to fix:**
- Delete `backend/chroma_db/` and re-run `python ingest.py`
- Verify sentence-transformers model is installed
- Check backend logs for detailed error

---

### 3. MODEL_CONNECTION
**When it occurs:** Cannot connect to the Ollama service.

**User sees:**
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

**Common causes:**
- Ollama not started
- Wrong OLLAMA_HOST URL
- Ollama container stopped (Docker)
- Firewall blocking connection

**How to fix:**
- Start Ollama: `ollama serve` (local) or `docker compose up ollama` (Docker)
- Check OLLAMA_HOST in `backend/config.py` or `.env`
- Verify connectivity: `curl http://localhost:11434/api/tags`

---

### 4. MODEL_TIMEOUT
**When it occurs:** Ollama takes too long to respond (>180 seconds).

**User sees:**
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

**Common causes:**
- Large model on slow hardware
- First request (model loading)
- Complex, long-context prompt
- System under heavy load

**How to fix:**
- Wait and retry (first request often slow)
- Use smaller/faster model: `ollama pull qwen2.5:1.5b-instruct`
- Simplify the question
- Increase timeout in `backend/models.py` if needed

---

### 5. MODEL_EMPTY_RESPONSE
**When it occurs:** Ollama returns an empty string (no text generated).

**User sees (with sources):**
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

**User sees (without sources):**
```
The AI model returned an empty response.

**What to do:**
• Try asking your question again
• Rephrase your question more clearly
• Check if Ollama is working: `ollama run mistral 'test'`
• Restart the backend server if the issue persists
```

**Common causes:**
- Model configuration issue
- Prompt too short or malformed
- Model struggling with the question
- Ollama service glitch

**How to fix:**
- Test Ollama directly: `ollama run mistral "What is Python?"`
- Restart Ollama service
- Check model is properly downloaded: `ollama list`
- Try a different model

---

### 6. MODEL_ERROR
**When it occurs:** General error during answer generation.

**User sees:**
```
An error occurred while generating the answer.

**What to do:**
• Try asking your question again
• Simplify your question if it's complex
• Check backend logs for technical details
• Restart the backend server if issues persist
```

**Common causes:**
- HTTP error from Ollama
- JSON parsing error
- Unexpected model behavior

**How to fix:**
- Check backend console for detailed error
- Verify Ollama status: `ollama ps`
- Restart both backend and Ollama
- Check system resources (RAM, CPU)

---

### 7. UNKNOWN
**When it occurs:** Unexpected error that doesn't fit other categories.

**User sees:**
```
An unexpected error occurred.

**What to do:**
• Try your question again
• Check backend logs for details
• Restart the backend server
• Report this issue if it continues
```

**Common causes:**
- Bugs in code
- Unexpected system state
- External service issues

**How to fix:**
- Check backend logs
- Restart services
- Report issue with logs if persistent

---

## For Developers

### Error Flow

1. User submits a question
2. System attempts to retrieve context → **RETRIEVAL_ERROR** or **NO_CONTEXT**
3. System builds prompt and calls Ollama
4. Ollama connection → **MODEL_CONNECTION**
5. Ollama processing → **MODEL_TIMEOUT**
6. Ollama response → **MODEL_EMPTY_RESPONSE** or **MODEL_ERROR**
7. Success or **UNKNOWN**

### Adding New Error Types

To add a new error type:

1. Add to `ErrorType` enum in `backend/main.py`:
```python
class ErrorType(Enum):
    YOUR_NEW_ERROR = "your_new_error"
```

2. Add case in `get_error_message()`:
```python
elif error_type == ErrorType.YOUR_NEW_ERROR:
    return (
        "User-friendly description\n\n"
        "**Possible causes:**\n"
        "• Cause 1\n"
        "• Cause 2\n\n"
        "**What to do:**\n"
        "• Action 1\n"
        "• Action 2"
    )
```

3. Use in endpoint:
```python
except SpecificException as e:
    error_msg = get_error_message(ErrorType.YOUR_NEW_ERROR, error_details=str(e))
    return {"answer": error_msg, "sources": []}
```

### Logging

All errors are logged with `print()` statements that include:
- Error type and classification
- Technical details (exception messages)
- Attempt numbers (for retries)

Example log output:
```
[ERROR] Retrieval error: ConnectionError(...)
[ERROR DETAILS] retrieval_error: Connection refused
[WARNING] Ollama ReadTimeout on attempt 1/3: timeout
```

### Testing

Run the error handling test suite:
```bash
cd backend
python test_error_handling.py
```

Note: Tests require dependencies but skip network-dependent tests.

### Best Practices

1. **Always log technical details**: Use `error_details` parameter
2. **Classify specifically**: Use the most specific error type
3. **Be user-friendly**: Avoid technical jargon in user messages
4. **Provide actions**: Always tell users what they can do
5. **Maintain context**: Pass `sources` when available

---

## Manual Testing Guide

### Test NO_CONTEXT
1. Ask about a topic not in your documents
2. Expected: Clear message saying content not found
3. Verify: Suggestions to rephrase or check documents

### Test RETRIEVAL_ERROR
1. Delete or corrupt `backend/chroma_db/`
2. Send a query
3. Expected: Message about database initialization
4. Fix: Run `python ingest.py`

### Test MODEL_CONNECTION
1. Stop Ollama: `pkill ollama` or stop container
2. Send a query
3. Expected: Message about Ollama not running
4. Verify: Tells user to check `ollama list`

### Test MODEL_TIMEOUT
1. Set timeout very low in `backend/models.py` (e.g., `timeout=1`)
2. Send a complex query
3. Expected: Timeout message with suggestions
4. Restore normal timeout

### Test MODEL_EMPTY_RESPONSE
Difficult to test naturally. Can mock in code:
```python
# In models.py, temporarily:
if text:
    text = ""  # Force empty
    return text
```

### Test MODEL_ERROR
1. Set wrong OLLAMA_HOST in config
2. Send a query
3. Expected: Connection or HTTP error message

---

## Migration Notes

### Old vs New Messages

**Old (NO_CONTEXT):**
```
I couldn't find that in the provided course materials.
Please try rephrasing or ask about another section.
```

**New (NO_CONTEXT):**
```
I couldn't find relevant information in the course materials for your question.

**Suggestions:**
• Try rephrasing your question with different keywords
• Ask about topics that are covered in the uploaded documents
• Check if documents have been ingested (run `python ingest.py`)
• Make your question more specific to the course content
```

**Old (Ollama failure with context found):**
```
I found relevant information in the course materials, but I'm having trouble
generating a complete answer right now. Here are some suggestions:

• Try rephrasing your question more specifically
• Break complex questions into simpler parts
• Check the sources panel on the left for relevant document sections

If the issue persists, the system may need to be restarted.
```

**New (MODEL_EMPTY_RESPONSE with sources):**
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

---

## Future Improvements

Potential enhancements:
1. Add retry suggestions with countdown timer
2. Automatic retry for transient failures
3. Error recovery recommendations based on error frequency
4. Telemetry to track which errors occur most often
5. User feedback on error message helpfulness
6. Link to troubleshooting docs for each error type

---

**Last Updated**: 2024
**Version**: 2.0
**Author**: EduMate Team
