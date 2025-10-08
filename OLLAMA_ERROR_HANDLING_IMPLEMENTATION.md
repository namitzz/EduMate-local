# Ollama Connection Error Handling - Implementation Summary

## Overview

The EduMate application provides comprehensive error messages when it cannot connect to the Ollama AI service. This document explains the complete implementation and how it works across different deployment scenarios.

## Error Message Format

When an Ollama connection error occurs, users see:

```
Unable to connect to the AI model (Ollama).

**Possible causes:**
• Ollama service is not running
• Connection to Ollama was refused
• Wrong OLLAMA_HOST configuration for your deployment type

**What to do:**
• For local development: Ensure Ollama is running (`ollama list`)
• For Docker: Verify the ollama container is running
• For cloud/public API: Check OLLAMA_HOST is set to your public endpoint
  (e.g., https://api.ollama.ai, NOT localhost)
• Verify OLLAMA_HOST/OLLAMA_URL environment variable is correct
• Check if your API endpoint requires authentication

**Connection attempted to:** http://localhost:11434
```

## Implementation Details

### 1. Error Generation (`backend/models.py`)

**Synchronous requests** (`ollama_complete`):
- Tries to connect 3 times with exponential backoff
- On failure, raises `RuntimeError` with format: `"Ollama ConnectionError after 3 retries (URL: {url}): {error}"`
- The URL is explicitly included in the error message

**Asynchronous streaming** (`ollama_complete_stream`):
- Handles streaming connection errors
- Yields error message with format: `"[Streaming error (URL: {url}): {error}]"`
- Consistent with synchronous error format

### 2. Error Classification (`backend/main.py`)

The error is classified based on keywords in the error message:
- `"connection"` → `ErrorType.MODEL_CONNECTION`
- `"timeout"` → `ErrorType.MODEL_TIMEOUT`
- `"Empty response"` → `ErrorType.MODEL_EMPTY_RESPONSE`
- Other errors → `ErrorType.MODEL_ERROR`

### 3. Error Message Generation (`backend/main.py`)

The `get_error_message()` function:
1. Receives the error type and error details
2. Extracts the URL from error details if present:
   ```python
   if error_details and "URL:" in error_details:
       url_part = error_details.split("URL:")[1].split(")")[0].strip()
       url_info = f"\n\n**Connection attempted to:** {url_part}"
   ```
3. Appends the URL info to the user-friendly message
4. Returns the complete formatted message

### 4. Error Display

The formatted error message is returned to the user through:
- **REST API** (`/chat` endpoint): In the `answer` field of the JSON response
- **Streaming API** (`/chat/stream` endpoint): As part of the streamed text

## Key Features

### ✅ Deployment-Specific Guidance

The error message includes troubleshooting steps for:
- **Local development**: Check if Ollama is running locally
- **Docker deployments**: Verify the Ollama container is running
- **Cloud/Public API**: Ensure OLLAMA_HOST points to the public endpoint

### ✅ URL Visibility

The error message shows the exact URL that was attempted:
- `http://localhost:11434` for local development
- `http://ollama:11434` for Docker deployments
- Custom URLs for cloud deployments

This helps users immediately understand which configuration is being used.

### ✅ Backward Compatibility

The URL extraction is optional:
- If error details contain `(URL: ...)`, the URL is extracted and displayed
- If not, the error message still works without the URL section
- No breaking changes to existing deployments

### ✅ Consistent Format

Both synchronous and asynchronous error paths use the same URL format:
- Pattern: `(URL: {url})`
- This ensures URL extraction always works
- Users get consistent error messages regardless of which code path is used

## Configuration Flow

The connection URL is determined by:

```
1. OLLAMA_URL environment variable (if set)
   ↓
2. OLLAMA_HOST environment variable (if set)
   ↓
3. Default: http://localhost:11434
```

### Deployment Examples

**Local Development:**
```bash
# No environment variables
# Uses: http://localhost:11434
ollama list  # Verify Ollama is running
```

**Docker Deployment:**
```yaml
# docker-compose.yml
services:
  api:
    environment:
      OLLAMA_HOST: http://ollama:11434  # Container-to-container
```

**Cloud Deployment:**
```bash
# Set environment variable
export OLLAMA_HOST=https://api.ollama.ai
# or
export OLLAMA_URL=https://your-ollama-instance.com
```

## Testing

The implementation is verified with comprehensive tests:

1. **`test_model_connection_error.py`**: Tests error message format and structure
2. **`test_connection_error_url_extraction.py`**: Tests URL extraction logic
   - With URL in error details
   - Without URL (backward compatibility)
   - Various URL formats (localhost, Docker, cloud, IP addresses)
   - Streaming error format
3. **`test_model_connection_integration.py`**: Tests complete error flow from models.py to main.py

All tests pass, confirming the implementation works correctly.

## Troubleshooting

If you see the connection error:

1. **Check the URL shown in the error message**
   - Is it correct for your deployment type?
   
2. **For local development** (`http://localhost:11434`):
   ```bash
   ollama list  # Check if Ollama is running
   curl http://localhost:11434/api/tags  # Test connectivity
   ```

3. **For Docker** (`http://ollama:11434`):
   ```bash
   docker ps  # Check if ollama container is running
   docker logs edumate-ollama  # Check Ollama container logs
   ```

4. **For cloud deployments**:
   - Verify OLLAMA_HOST environment variable is set correctly
   - Ensure the URL is publicly accessible
   - Check if authentication is required

## Related Files

- `backend/models.py` - Error generation and retry logic
- `backend/main.py` - Error classification and message formatting
- `backend/config.py` - OLLAMA_HOST configuration
- `DEPLOYMENT.md` - Deployment-specific configuration guide
- `OLLAMA_CONNECTION_QUICK_REFERENCE.md` - Quick reference for configuration
- `OLLAMA_CONNECTION_FIX_SUMMARY.md` - Summary of the fix implementation

## Conclusion

The Ollama connection error handling provides:
- ✅ Clear, actionable error messages
- ✅ Deployment-specific troubleshooting guidance
- ✅ Visibility into which URL was attempted
- ✅ Consistent behavior across sync and async code paths
- ✅ Backward compatibility
- ✅ Comprehensive test coverage

This ensures users can quickly diagnose and fix Ollama connection issues regardless of their deployment environment.
