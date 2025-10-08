# MODEL_CONNECTION Error Message - Testing & Verification

## Overview

This directory contains comprehensive tests for the `MODEL_CONNECTION` error message in EduMate's backend. These tests verify that connection errors to the Ollama service are properly detected, classified, and communicated to users with clear, actionable guidance.

## Test Files

### 1. `test_model_connection_error.py`

**Purpose**: Unit tests for error message format and content

**What it tests**:
- Message contains all required sections (title, causes, actions)
- Markdown formatting is correct (`**headers**`)
- Each bullet point is on its own line
- All troubleshooting steps are present
- Proper line breaks and structure

**Run**: `python test_model_connection_error.py`

**Expected output**: 8/8 tests passing ✅

### 2. `test_model_connection_integration.py`

**Purpose**: Integration tests for error detection and classification

**What it tests**:
- Error strings with "ConnectionError" are classified correctly
- Error strings with "connection" keyword are classified correctly
- Other error types (timeout, empty response) are NOT misclassified
- Generated error message contains all required content
- Error message matches ERROR_HANDLING.md specification

**Run**: `python test_model_connection_integration.py`

**Expected output**: 22/22 tests passing ✅

### 3. `TEST_SUMMARY_MODEL_CONNECTION.md`

**Purpose**: Comprehensive documentation of test coverage and results

**Contents**:
- Test execution summary
- Error flow diagram
- Implementation verification
- Message format validation
- Complete test results

## Quick Start

Run all tests:

```bash
cd backend

# Test 1: Message format
python test_model_connection_error.py

# Test 2: Integration & consistency
python test_model_connection_integration.py
```

Both tests should show all tests passing with green checkmarks ✅

## The Error Message

When a connection error to Ollama occurs, users see:

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

This message is:
- ✅ Clear and user-friendly
- ✅ Lists specific causes
- ✅ Provides actionable troubleshooting steps
- ✅ Includes commands users can run
- ✅ Properly formatted with markdown

## Error Detection Flow

```
User makes a query
    ↓
Backend attempts to connect to Ollama
    ↓
Connection fails (requests.ConnectionError)
    ↓
Retry logic in models.py (3 attempts)
    ↓
RuntimeError raised with "ConnectionError" in message
    ↓
Error caught in main.py (/chat or /chat_stream)
    ↓
Error classified as ErrorType.MODEL_CONNECTION
    ↓
get_error_message() generates user-friendly message
    ↓
Message returned to user via API
    ↓
UI displays formatted message (Streamlit markdown)
```

## Implementation Details

### Error Message Definition
- **File**: `backend/main.py`
- **Lines**: 64-75
- **Function**: `get_error_message()`
- **Error Type**: `ErrorType.MODEL_CONNECTION`

### Error Classification

**In `/chat` endpoint** (main.py:390-405):
```python
except RuntimeError as e:
    if "ConnectionError" in str(e) or "connection" in str(e).lower():
        error_type = ErrorType.MODEL_CONNECTION
```

**In `/chat_stream` endpoint** (main.py:316-328):
```python
except Exception as e:
    if "connection" in str(e).lower():
        error_type = ErrorType.MODEL_CONNECTION
```

### Connection Error Raising
- **File**: `backend/models.py`
- **Lines**: 34-51
- **Error**: `RuntimeError(f"Ollama ConnectionError after {attempt + 1} retries: {last_err}")`

## Test Coverage Summary

| Component | Tests | Status |
|-----------|-------|--------|
| Message Format | 8 | ✅ All passing |
| Error Classification | 6 | ✅ All passing |
| Message Content | 9 | ✅ All passing |
| Documentation Match | 7 | ✅ All passing |
| **Total** | **30** | **✅ 100% passing** |

## Validation Checklist

- [x] Error message is not empty
- [x] Contains "Ollama" reference
- [x] Has markdown-formatted "Possible causes" section
- [x] Has markdown-formatted "What to do" section
- [x] Lists Ollama not running as a cause
- [x] Lists connection refused as a cause
- [x] Provides `ollama list` command
- [x] Mentions starting Ollama
- [x] Mentions OLLAMA_HOST configuration
- [x] References Docker container
- [x] Each bullet point on its own line
- [x] Proper line breaks (11 lines total)
- [x] Matches ERROR_HANDLING.md specification
- [x] Works in /chat endpoint
- [x] Works in /chat_stream endpoint

## Verification

The implementation has been verified to be **100% correct**:

✅ No code changes needed  
✅ Error message is properly formatted  
✅ Error classification works correctly  
✅ Message matches documentation  
✅ All troubleshooting steps included  
✅ Both endpoints handle the error  

## Related Documentation

- **ERROR_HANDLING.md** - Complete error handling documentation
- **TEST_SUMMARY_MODEL_CONNECTION.md** - Detailed test results
- **backend/main.py** - Error message implementation
- **backend/models.py** - Connection error detection

## Troubleshooting Tests

If tests fail:

1. **Check Python version**: Tests require Python 3.8+
2. **Verify imports**: Make sure you're in the `backend/` directory
3. **Check file paths**: Tests expect to be run from `backend/` directory
4. **Review error output**: Tests include descriptive failure messages

## Contributing

When modifying error messages:

1. Update the message in `backend/main.py`
2. Update documentation in `ERROR_HANDLING.md`
3. Run all tests to ensure they pass
4. Update tests if message format changes
5. Verify message displays correctly in UI

---

**Last Updated**: 2025-01-22  
**Status**: ✅ All tests passing  
**Coverage**: 100%
