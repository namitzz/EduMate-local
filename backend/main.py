from typing import List, Dict, Optional
import re
import asyncio
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import ollama_complete, ollama_complete_stream
from retrieval import Retriever
import config


# --- Error Classification ---
class ErrorType(Enum):
    """Classification of different error types for better user feedback"""
    NO_CONTEXT = "no_context"
    RETRIEVAL_ERROR = "retrieval_error"
    MODEL_CONNECTION = "model_connection"
    MODEL_TIMEOUT = "model_timeout"
    MODEL_EMPTY_RESPONSE = "model_empty_response"
    MODEL_ERROR = "model_error"
    UNKNOWN = "unknown"


def get_error_message(error_type: ErrorType, sources: List[str] = None, error_details: str = None) -> str:
    """
    Generate user-friendly, actionable error messages based on error type.
    
    Args:
        error_type: The type of error that occurred
        sources: Optional list of sources that were found (for context-found-but-generation-failed cases)
        error_details: Optional technical details for logging
    
    Returns:
        A user-friendly error message with actionable guidance
    """
    if error_details:
        print(f"[ERROR DETAILS] {error_type.value}: {error_details}")
    
    if error_type == ErrorType.NO_CONTEXT:
        return (
            "I couldn't find relevant information in the course materials for your question.\n\n"
            "**Suggestions:**\n"
            "• Try rephrasing your question with different keywords\n"
            "• Ask about topics that are covered in the uploaded documents\n"
            "• Check if documents have been ingested (run `python ingest.py`)\n"
            "• Make your question more specific to the course content"
        )
    
    elif error_type == ErrorType.RETRIEVAL_ERROR:
        return (
            "There was an error searching through the course materials.\n\n"
            "**Possible causes:**\n"
            "• The vector database may not be initialized\n"
            "• Documents may not have been ingested yet\n\n"
            "**What to do:**\n"
            "• Run `python ingest.py` in the backend directory\n"
            "• Check that documents exist in the corpus/ folder\n"
            "• Restart the backend server if the issue persists"
        )
    
    elif error_type == ErrorType.MODEL_CONNECTION:
        # Extract URL from error_details if available
        url_info = ""
        if error_details and "URL:" in error_details:
            try:
                url_part = error_details.split("URL:")[1].split(")")[0].strip()
                url_info = f"\n\n**Connection attempted to:** {url_part}"
            except:
                pass
        
        return (
            "Unable to connect to the AI model (Ollama).\n\n"
            "**Possible causes:**\n"
            "• Ollama service is not running\n"
            "• Connection to Ollama was refused\n\n"
            "**What to do:**\n"
            "• Check if Ollama is running: `ollama list`\n"
            "• Start Ollama if needed\n"
            "• Verify OLLAMA_HOST configuration\n"
            "• If using Docker, ensure the ollama container is running"
            f"{url_info}"
        )
    
    elif error_type == ErrorType.MODEL_TIMEOUT:
        return (
            "The AI model took too long to respond (timeout).\n\n"
            "**Possible causes:**\n"
            "• The model is overloaded or slow\n"
            "• Your question may be too complex\n"
            "• The model might be loading for the first time\n\n"
            "**What to do:**\n"
            "• Try asking a simpler question\n"
            "• Wait a moment and try again (the model may be warming up)\n"
            "• Consider using a faster model like `qwen2.5:1.5b-instruct`"
        )
    
    elif error_type == ErrorType.MODEL_EMPTY_RESPONSE:
        if sources:
            return (
                "The AI model returned an empty response.\n\n"
                "I found relevant information in the course materials, but the model "
                "failed to generate an answer. This could be a temporary issue.\n\n"
                "**What to do:**\n"
                "• Try rephrasing your question\n"
                "• Check the sources below for relevant information\n"
                "• Try again in a moment\n"
                "• If this persists, restart the backend server"
            )
        else:
            return (
                "The AI model returned an empty response.\n\n"
                "**What to do:**\n"
                "• Try asking your question again\n"
                "• Rephrase your question more clearly\n"
                "• Check if Ollama is working: `ollama run mistral 'test'`\n"
                "• Restart the backend server if the issue persists"
            )
    
    elif error_type == ErrorType.MODEL_ERROR:
        return (
            "An error occurred while generating the answer.\n\n"
            "**What to do:**\n"
            "• Try asking your question again\n"
            "• Simplify your question if it's complex\n"
            "• Check backend logs for technical details\n"
            "• Restart the backend server if issues persist"
        )
    
    else:  # UNKNOWN
        return (
            "An unexpected error occurred.\n\n"
            "**What to do:**\n"
            "• Try your question again\n"
            "• Check backend logs for details\n"
            "• Restart the backend server\n"
            "• Report this issue if it continues"
        )

# --- FastAPI app ---
app = FastAPI(title="EduMate Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared retriever (Chroma is already persisted)
retriever = Retriever()

# Semaphore for concurrency control
generation_semaphore = asyncio.Semaphore(config.MAX_ACTIVE_GENERATIONS)


# --- Schemas ---
class ChatRequest(BaseModel):
    messages: List[Dict]


class ChatStreamRequest(BaseModel):
    messages: List[Dict]
    mode: Optional[str] = "docs"  # docs, coach, or facts


# --- Greeting detection ---
def is_greeting_or_chitchat(msg: str) -> bool:
    """
    Detect if the message is a greeting or simple chitchat that doesn't require
    retrieval from course materials.
    """
    msg_lower = msg.strip().lower()
    
    # Expanded greeting patterns to catch more variations
    # Support longer greetings (up to 30 chars)
    if len(msg_lower) <= 30:
        # Comprehensive greeting patterns
        greeting_patterns = [
            r'^(hi|hello|hey|hii|hiii|heya|heyy|heyyy|howdy|greetings|sup|yo|hola|aloha|salut)([!.?,\s]*)?$',
            r'^(hi|hello|hey)\s+(there|everyone|all)([!.?,\s]*)?$',
            r'^(good\s+(morning|afternoon|evening|day|night))([!.?,\s]*)?$',
            r'^(what\'?s?\s+up|wassup|whats\s+up|whatsup)([!.?,\s]*)?$',
            r'^(how\s+(are|r)\s+(you|u|ya))([!.?,\s]*)?$',
            r'^(how\'?s?\s+it\s+going)([!.?,\s]*)?$',
            r'^(nice\s+to\s+meet\s+you)([!.?,\s]*)?$',
            r'^(thanks|thank\s+you|thx|ty)([!.?,\s]*)?$',
            r'^(bye|goodbye|see\s+ya|cya|later)([!.?,\s]*)?$',
        ]
        
        for pattern in greeting_patterns:
            if re.match(pattern, msg_lower):
                return True
    
    return False


# --- Prompt builder ---
def compose_prompt(contexts: List[Dict], user_msg: str):
    """
    Build a grounded prompt from retrieved contexts with inline citation markers.
    Returns (prompt_str, sources_list).
    Optimized for faster generation.
    """
    # Limit to top 3 chunks in fast mode, trim each to avoid huge prompts
    max_contexts = 3 if config.FAST_MODE else 4
    contexts = contexts[:max_contexts]
    sources, ctx_text = [], []
    
    # Reduce snippet size for faster processing
    max_snippet_len = 800 if config.FAST_MODE else 1200
    
    for i, c in enumerate(contexts, start=1):
        marker = chr(9311 + i)  # ①, ②, ...
        snippet = c["doc"][:max_snippet_len]
        ctx_text.append(f"[{marker}] {snippet}")
        meta = c.get("meta") or {}
        sources.append(f"{marker} {meta.get('file')} (chunk {meta.get('chunk')})")

    # More concise system prompt for faster generation
    system = (
        "You are EduMate, a study assistant. Answer based on the context provided. "
        "Be clear and concise. Use citation markers [①, ②, ...] for sources. "
        "If the answer isn't in the context, say so briefly."
    )

    context_block = "\n".join(ctx_text) if ctx_text else "(no context)"
    prompt = (
        system
        + "\n\nContext:\n" + context_block
        + "\n\nQuestion: " + user_msg
        + "\n\nAnswer:"
    )
    return prompt, sources


# --- Health route ---
@app.get("/health")
def health():
    return {"ok": True}


# --- Streaming Chat route (new, additive) ---
@app.post("/chat_stream")
async def chat_stream(req: ChatStreamRequest):
    """
    Streaming endpoint for Fast Mode and public UI.
    Supports modes: docs (RAG), coach (study tips), facts (quick answers).
    """
    # Find the last user message
    last_user: Optional[str] = ""
    for m in reversed(req.messages):
        if (m.get("role") or "").lower() == "user":
            last_user = m.get("content", "")
            break
    if not last_user:
        raise HTTPException(status_code=400, detail="No user message provided")

    # Check if it's a greeting
    if is_greeting_or_chitchat(last_user):
        async def greeting_gen():
            greeting = (
                "Hello! I'm EduMate, your study assistant. "
                "I'm here to help you with questions about your course materials. "
                "What would you like to know?"
            )
            yield greeting
        return StreamingResponse(greeting_gen(), media_type="text/plain")

    # Build prompt based on mode
    prompt = ""
    mode = (req.mode or "docs").lower()
    
    if mode == "coach":
        # Study coaching mode - no retrieval, general study advice
        prompt = (
            "You are EduMate, a study coach. Provide helpful, encouraging study advice. "
            "Be concise and practical.\n\n"
            f"Question: {last_user}\n\nAnswer:"
        )
    elif mode == "facts":
        # Quick facts mode - no retrieval, concise answers
        prompt = (
            "You are EduMate. Provide a brief, factual answer.\n\n"
            f"Question: {last_user}\n\nAnswer:"
        )
    else:
        # Default: docs mode with retrieval (RAG)
        ctx = []
        retrieval_error = None
        try:
            ctx = retriever.retrieve(last_user, model_call=ollama_complete)
        except Exception as e:
            retrieval_error = e
            print(f"[ERROR] Retrieval error: {repr(e)}")

        # Handle retrieval failure
        if retrieval_error:
            async def retrieval_error_gen():
                yield get_error_message(ErrorType.RETRIEVAL_ERROR, error_details=str(retrieval_error))
            return StreamingResponse(retrieval_error_gen(), media_type="text/plain")

        # Handle no context found
        if not ctx:
            async def no_context_gen():
                yield get_error_message(ErrorType.NO_CONTEXT)
            return StreamingResponse(no_context_gen(), media_type="text/plain")

        # Build prompt with context (same as /chat endpoint)
        prompt, sources = compose_prompt(ctx, last_user)
        
        # In Fast Mode, replace last user message with full prompt
        # (This allows the streaming to work with the full RAG context)
        if config.FAST_MODE:
            # Use the composed prompt directly
            pass

    # Stream generation with semaphore and improved error handling
    async def generate_stream():
        async with generation_semaphore:
            try:
                async for token in ollama_complete_stream(prompt):
                    yield token
            except Exception as e:
                error_str = str(e)
                print(f"[ERROR] Stream generation failed: {repr(e)}")
                
                # Classify the error
                if "timeout" in error_str.lower():
                    error_type = ErrorType.MODEL_TIMEOUT
                elif "connection" in error_str.lower():
                    error_type = ErrorType.MODEL_CONNECTION
                else:
                    error_type = ErrorType.MODEL_ERROR
                
                yield f"\n\n{get_error_message(error_type, error_details=error_str)}"

    return StreamingResponse(generate_stream(), media_type="text/plain")


# --- Chat route ---
@app.post("/chat")
def chat(req: ChatRequest):
    # find the last user message
    last_user: Optional[str] = ""
    for m in reversed(req.messages):
        if (m.get("role") or "").lower() == "user":
            last_user = m.get("content", "")
            break
    if not last_user:
        raise HTTPException(status_code=400, detail="No user message provided")

    # Check if it's a greeting or chitchat
    if is_greeting_or_chitchat(last_user):
        greeting_response = (
            "Hello! I'm EduMate, your study assistant. "
            "I'm here to help you with questions about your course materials. "
            "What would you like to know?"
        )
        return {"answer": greeting_response, "sources": []}

    # retrieve context with improved error handling
    ctx = []
    retrieval_error = None
    try:
        ctx = retriever.retrieve(last_user, model_call=ollama_complete)
    except Exception as e:
        retrieval_error = e
        print(f"[ERROR] Retrieval error: {repr(e)}")

    # Handle retrieval failure
    if retrieval_error:
        error_msg = get_error_message(ErrorType.RETRIEVAL_ERROR, error_details=str(retrieval_error))
        return {"answer": error_msg, "sources": []}

    # Handle no context found
    if not ctx:
        error_msg = get_error_message(ErrorType.NO_CONTEXT)
        return {"answer": error_msg, "sources": []}

    # build prompt
    prompt, sources = compose_prompt(ctx, last_user)

    # debug logs
    try:
        print("\n[DEBUG] Retrieved context preview:",
              [c["doc"][:120].replace("\n", " ") for c in ctx][:3])
        print("[DEBUG] Prompt head:", prompt[:300].replace("\n", " "))
    except Exception:
        pass

    # call Ollama with improved error handling
    answer = ""
    error_type = None
    try:
        answer = ollama_complete(prompt)
        print(f"[DEBUG] Ollama response length: {len(answer)} chars")
    except RuntimeError as e:
        error_str = str(e)
        print(f"[ERROR] Ollama call error: {repr(e)}")
        
        # Classify the error based on the exception message
        if "Empty response" in error_str:
            error_type = ErrorType.MODEL_EMPTY_RESPONSE
        elif "ReadTimeout" in error_str or "timeout" in error_str.lower():
            error_type = ErrorType.MODEL_TIMEOUT
        elif "ConnectionError" in error_str or "connection" in error_str.lower():
            error_type = ErrorType.MODEL_CONNECTION
        else:
            error_type = ErrorType.MODEL_ERROR
        
        error_msg = get_error_message(error_type, sources=sources, error_details=error_str)
        return {"answer": error_msg, "sources": sources}
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[ERROR] Unexpected error during Ollama call: {repr(e)}")
        error_msg = get_error_message(ErrorType.MODEL_ERROR, sources=sources, error_details=str(e))
        return {"answer": error_msg, "sources": sources}

    # Handle empty or invalid response
    if not answer or answer.strip() == "":
        print("[WARNING] Ollama returned empty answer string")
        error_msg = get_error_message(ErrorType.MODEL_EMPTY_RESPONSE, sources=sources)
        return {"answer": error_msg, "sources": sources}

    return {"answer": answer, "sources": sources}

