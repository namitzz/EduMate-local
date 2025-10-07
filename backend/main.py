from typing import List, Dict, Optional
import re
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import ollama_complete, ollama_complete_stream
from retrieval import Retriever
import config

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
    
    # Very short messages (likely greetings)
    if len(msg_lower) <= 15:
        # Common greeting patterns
        greeting_patterns = [
            r'^(hi|hello|hey|hii|hiii|heya|heyy|heyyy|howdy|greetings|sup|yo)([!.?]*)?$',
            r'^(good\s+(morning|afternoon|evening|day|night))([!.?]*)?$',
            r'^(what\'?s?\s+up|wassup|whats\s+up)([!.?]*)?$',
            r'^(how\s+(are|r)\s+(you|u))([!.?]*)?$',
            r'^(how\'?s?\s+it\s+going)([!.?]*)?$',
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
    """
    # limit to top 4 chunks, trim each to avoid huge prompts
    contexts = contexts[:4]
    sources, ctx_text = [], []
    for i, c in enumerate(contexts, start=1):
        marker = chr(9311 + i)  # ①, ②, ...
        snippet = c["doc"][:1200]  # trim to ~1200 chars
        ctx_text.append(f"[{marker}] {snippet}")
        meta = c.get("meta") or {}
        sources.append(f"{marker} {meta.get('file')} (chunk {meta.get('chunk')})")

    system = (
        "You are EduMate, a helpful study assistant. Answer the user's question based on the provided context. "
        "If the information is in the context, provide a clear and direct answer. "
        "If the answer is not in the context, politely say so and suggest the user consult other resources. "
        "Be concise but complete. Add inline citation markers [①, ②, ...] when referencing specific sources."
    )

    context_block = "\n".join(ctx_text) if ctx_text else "(no context)"
    prompt = (
        system
        + "\n\nContext:\n" + context_block
        + "\n\nUser question:\n" + user_msg
        + "\n\nAnswer (with inline markers for citations where relevant):\n"
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
            "You are EduMate, a supportive study coach. "
            "Provide helpful, encouraging study advice and strategies. "
            f"User question: {last_user}\n\nAnswer:"
        )
    elif mode == "facts":
        # Quick facts mode - no retrieval, concise answers
        prompt = (
            "You are EduMate. Provide a brief, factual answer. "
            f"Question: {last_user}\n\nAnswer:"
        )
    else:
        # Default: docs mode with retrieval (RAG)
        ctx = []
        try:
            ctx = retriever.retrieve(last_user, model_call=ollama_complete)
        except Exception as e:
            print("Retrieval error:", repr(e))

        if not ctx:
            async def no_context_gen():
                yield ("I couldn't find that in the provided course materials. "
                       "Please try rephrasing or ask about another section.")
            return StreamingResponse(no_context_gen(), media_type="text/plain")

        # Build prompt with context (same as /chat endpoint)
        prompt, sources = compose_prompt(ctx, last_user)
        
        # In Fast Mode, replace last user message with full prompt
        # (This allows the streaming to work with the full RAG context)
        if config.FAST_MODE:
            # Use the composed prompt directly
            pass

    # Stream generation with semaphore
    async def generate_stream():
        async with generation_semaphore:
            try:
                async for token in ollama_complete_stream(prompt):
                    yield token
            except Exception as e:
                print(f"[ERROR] Stream generation failed: {e}")
                yield f"\n\n[Error generating response: {e}]"

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

    # retrieve context
    ctx = []
    try:
        ctx = retriever.retrieve(last_user, model_call=ollama_complete)
    except Exception as e:
        print("Retrieval error:", repr(e))

    if not ctx:
        msg = ("I couldn't find that in the provided course materials. "
               "Please try rephrasing or ask about another section.")
        return {"answer": msg, "sources": []}

    # build prompt
    prompt, sources = compose_prompt(ctx, last_user)

    # debug logs
    try:
        print("\n[DEBUG] Retrieved context preview:",
              [c["doc"][:120].replace("\n", " ") for c in ctx][:3])
        print("[DEBUG] Prompt head:", prompt[:300].replace("\n", " "))
    except Exception:
        pass

    # call Ollama
    answer = ""
    try:
        answer = ollama_complete(prompt)
        print(f"[DEBUG] Ollama response length: {len(answer)} chars")
    except Exception as e:
        print("Ollama call error:", repr(e))
        answer = "[Error: Ollama call failed]"

    if not answer or answer.strip() in {"", "[Error: Ollama call failed]"}:
        # Enhanced fallback message with actionable guidance
        fallback = (
            "I found relevant information in the course materials, but I'm having trouble "
            "generating a complete answer right now. Here are some suggestions:\n\n"
            "• Try rephrasing your question more specifically\n"
            "• Break complex questions into simpler parts\n"
            "• Check the sources panel on the left for relevant document sections\n\n"
            "If the issue persists, the system may need to be restarted."
        )
        return {"answer": fallback, "sources": sources}

    return {"answer": answer, "sources": sources}

