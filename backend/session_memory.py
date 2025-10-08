"""
Session Memory for Module Convenor Assistant
Provides short-term context tracking for personalized support
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import config


class SessionMemory:
    """
    Lightweight session-based memory for tracking conversation context.
    Stores recent messages per session to provide personalized support.
    """
    
    def __init__(self):
        # session_id -> list of messages
        self.sessions: Dict[str, List[Dict]] = {}
        # session_id -> last access time
        self.last_access: Dict[str, datetime] = {}
        # Session timeout (1 hour)
        self.timeout = timedelta(hours=1)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history"""
        if not config.ENABLE_SESSION_MEMORY:
            return
        
        # Clean up old sessions first
        self._cleanup_old_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # Keep only recent messages
        if len(self.sessions[session_id]) > config.MAX_SESSION_MESSAGES:
            self.sessions[session_id] = self.sessions[session_id][-config.MAX_SESSION_MESSAGES:]
        
        self.last_access[session_id] = datetime.now()
    
    def get_history(self, session_id: str, max_messages: int = 5) -> List[Dict]:
        """Get recent conversation history for context"""
        if not config.ENABLE_SESSION_MEMORY:
            return []
        
        if session_id not in self.sessions:
            return []
        
        # Return last N messages
        messages = self.sessions[session_id][-max_messages:]
        return [{"role": m["role"], "content": m["content"]} for m in messages]
    
    def get_context_summary(self, session_id: str) -> str:
        """
        Generate a brief summary of conversation context for the LLM.
        Helps the assistant understand what has been discussed.
        """
        if not config.ENABLE_SESSION_MEMORY:
            return ""
        
        history = self.get_history(session_id, max_messages=5)
        if not history:
            return ""
        
        # Build a concise context summary
        summary_parts = []
        for msg in history[:-1]:  # Exclude the current message
            role = msg["role"]
            content = msg["content"][:100]  # Truncate long messages
            summary_parts.append(f"{role.capitalize()}: {content}")
        
        if summary_parts:
            return "Previous conversation:\n" + "\n".join(summary_parts) + "\n\n"
        return ""
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.last_access:
            del self.last_access[session_id]
    
    def _cleanup_old_sessions(self):
        """Remove sessions that haven't been accessed recently"""
        now = datetime.now()
        expired_sessions = [
            sid for sid, last_time in self.last_access.items()
            if now - last_time > self.timeout
        ]
        
        for sid in expired_sessions:
            self.clear_session(sid)


# Global session memory instance
session_memory = SessionMemory()
