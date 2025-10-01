from typing import List, Dict, Optional
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import ollama_complete
from retrieval import Retriever

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


# --- Schemas ---
class ChatRequest(BaseModel):
    messages: List[Dict]


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
        "You are EduMate, a study assistant. Use ONLY the provided context. "
        "If the answer is not in the context, say you don't have that information. "
        "Be concise and clear. Add inline markers [①, ②, ...] when citing."
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
    except Exception as e:
        print("Ollama call error:", repr(e))
        answer = "[Error: Ollama call failed]"

    if not answer or answer.strip() in {"", "[Error: Ollama call failed]"}:
        fallback = ("I retrieved context but couldn't generate an answer. "
                    "Please retry or narrow your question.")
        return {"answer": fallback, "sources": sources}

    return {"answer": answer, "sources": sources}

