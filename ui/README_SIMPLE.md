# EduMate Simple Streamlit App

A beginner-friendly Streamlit chat interface for EduMate. This is a simplified version perfect for learning and quick deployment.

## Features

- 💬 Clean chat interface with conversation history
- 📚 Source citations for answers
- 🎯 Real-time API health monitoring
- 🗑️ Clear chat history button
- ⚡ Simple and easy to understand code

## Prerequisites

1. **Backend API must be running**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Install dependencies**
   ```bash
   cd ui
   pip install -r requirements.txt
   ```

## Quick Start

### Option 1: Default Settings (Recommended)

```bash
cd ui
streamlit run app_simple.py
```

Then open http://localhost:8501 in your browser.

### Option 2: Custom API URL

If your API is running on a different host or port:

```bash
cd ui
export API_BASE=http://localhost:8000
streamlit run app_simple.py
```

### Option 3: Different Port

```bash
cd ui
streamlit run app_simple.py --server.port 8502
```

## Usage

1. **Start chatting**: Type your question in the chat input box
2. **View sources**: Click the "Sources" expander to see document references
3. **Clear history**: Click the "Clear Chat History" button in the sidebar
4. **Check API status**: The sidebar shows if the backend is online

## Example Questions

Try asking:
- "What is machine learning?"
- "Explain neural networks"
- "How do I prepare for exams?"
- "What are the key concepts in this course?"

## Configuration

### Environment Variables

- `API_BASE`: Backend API URL (default: `http://localhost:8000`)

Example:
```bash
export API_BASE=http://192.168.1.10:8000
streamlit run app_simple.py
```

## Troubleshooting

### API Connection Error

**Problem**: "Cannot connect to the API"

**Solution**:
1. Make sure the backend is running:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
2. Check the API URL in the sidebar
3. Verify you can access http://localhost:8000/health in your browser

### Timeout Error

**Problem**: "Request timed out"

**Solution**:
- The query might be too complex
- The backend might be processing a large number of documents
- Try a simpler question first
- Wait for the current request to complete

### Empty Response

**Problem**: No answer from the API

**Solution**:
- Check if there are documents in the `corpus/` directory
- Run the ingestion script:
  ```bash
  cd backend
  python ingest.py
  ```

## Code Structure

The app is organized into clear sections:

1. **Configuration**: API URL and settings
2. **Page Configuration**: Streamlit page setup
3. **Header**: Title and caption
4. **Session State**: Initialize chat history
5. **Display Chat History**: Show all messages
6. **Chat Input and Response**: Handle user input and API calls
7. **Sidebar Information**: About, status, and controls

## Comparison with Other UIs

| Feature | app_simple.py | app.py | app_public.py |
|---------|---------------|---------|---------------|
| **Complexity** | ⭐ Basic | ⭐⭐ Intermediate | ⭐⭐⭐ Advanced |
| **Streaming** | ❌ No | ❌ No | ✅ Yes |
| **Modes** | ❌ No | ❌ No | ✅ Yes (docs/coach/facts) |
| **Sources Panel** | ✅ In expander | ✅ Sidebar | ❌ No |
| **Custom CSS** | ❌ No | ❌ No | ✅ Yes |
| **Health Check** | ✅ Yes | ❌ No | ❌ No |
| **Best For** | Learning | Basic use | Production |

## When to Use This App

Use `app_simple.py` when you:
- Are learning how Streamlit works
- Want a quick, no-frills interface
- Need a template to build upon
- Want to understand the basics before using advanced features

For production use with all features, use `app_public.py` instead.

## Extending This App

Here are some ideas to enhance this app:

1. **Add streaming**: Use the `/chat_stream` endpoint
2. **Add modes**: Support docs/coach/facts modes
3. **Add custom CSS**: Style the interface
4. **Add file upload**: Allow document uploads (requires backend changes)
5. **Add export**: Export conversation history
6. **Add themes**: Light/dark mode toggle

## Learn More

- 📖 [Main README](../README.md) - Full project documentation
- 🚀 [Quick Start Guide](../QUICK_START.md) - Fast setup instructions
- 🔧 [Deployment Guide](../DEPLOYMENT.md) - Production deployment

## Need Help?

1. Check the sidebar for API status
2. Review the backend logs: `uvicorn main:app --reload --port 8000`
3. Verify Ollama is running: `ollama list`
4. Check the [main documentation](../README.md)

---

**Happy Learning! 🎓**
