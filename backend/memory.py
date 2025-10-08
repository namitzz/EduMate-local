"""
Conversation Memory Module
===========================
Maintains short-term conversation context to enable personalized academic guidance.
Stores anonymized conversation history for context-aware responses.
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class ConversationMemory:
    """
    Manages conversation context and student interaction history.
    Provides context for tailored academic guidance.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of conversation turns to retain
        """
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict]] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Unique session identifier
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata (sources, intent, etc.)
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.metadata[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "interaction_count": 0
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        self.metadata[session_id]["last_updated"] = datetime.now().isoformat()
        self.metadata[session_id]["interaction_count"] += 1
        
        # Trim history to max_history
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of conversation messages
        """
        return self.conversations.get(session_id, [])
    
    def get_recent_context(self, session_id: str, num_messages: int = 4) -> str:
        """
        Get recent conversation context as formatted text.
        
        Args:
            session_id: Unique session identifier
            num_messages: Number of recent messages to include
            
        Returns:
            Formatted conversation context
        """
        history = self.conversations.get(session_id, [])
        if not history:
            return ""
        
        recent = history[-num_messages:]
        context_lines = []
        
        for msg in recent:
            role = "Student" if msg["role"] == "user" else "You"
            context_lines.append(f"{role}: {msg['content'][:200]}")
        
        return "\n".join(context_lines)
    
    def detect_patterns(self, session_id: str) -> Dict[str, any]:
        """
        Analyze conversation patterns to identify student needs.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary of detected patterns and insights
        """
        history = self.conversations.get(session_id, [])
        if not history:
            return {}
        
        patterns = {
            "interaction_count": len(history),
            "topics_mentioned": [],
            "questions_asked": 0,
            "needs_clarification": False,
            "assignment_related": False
        }
        
        # Analyze recent messages
        for msg in history[-5:]:
            if msg["role"] == "user":
                content_lower = msg["content"].lower()
                patterns["questions_asked"] += 1
                
                # Detect assignment-related queries
                if any(keyword in content_lower for keyword in ["assignment", "homework", "deadline", "submit", "rubric"]):
                    patterns["assignment_related"] = True
                
                # Detect confusion/clarification needs
                if any(keyword in content_lower for keyword in ["confused", "don't understand", "unclear", "explain again"]):
                    patterns["needs_clarification"] = True
        
        return patterns
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.metadata:
            del self.metadata[session_id]


# Global memory instance
_memory = ConversationMemory(max_history=10)


def get_memory() -> ConversationMemory:
    """Get the global conversation memory instance."""
    return _memory
