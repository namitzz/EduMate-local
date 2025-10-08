"""
Module Convenor Assistant Helper Functions
Provides intelligent context understanding for academic guidance
"""
import re
from typing import Dict, Optional, List
from datetime import datetime


class AssignmentContextAnalyzer:
    """
    Analyzes student queries to understand assignment context, deadlines,
    and academic intent for personalized guidance.
    """
    
    # Common assignment-related keywords
    ASSIGNMENT_KEYWORDS = [
        'assignment', 'homework', 'coursework', 'project', 'task',
        'essay', 'report', 'paper', 'presentation', 'lab', 'practical'
    ]
    
    DEADLINE_KEYWORDS = [
        'deadline', 'due', 'submit', 'submission', 'hand in', 'turn in',
        'date', 'when', 'time', 'extension'
    ]
    
    HELP_KEYWORDS = [
        'help', 'stuck', 'confused', 'don\'t understand', 'unclear',
        'struggling', 'difficult', 'problem', 'issue', 'trouble'
    ]
    
    FEEDBACK_KEYWORDS = [
        'feedback', 'improve', 'better', 'grade', 'mark', 'score',
        'suggestion', 'advice', 'review', 'check'
    ]
    
    CONCEPT_KEYWORDS = [
        'explain', 'what is', 'how does', 'why', 'define', 'meaning',
        'concept', 'theory', 'principle', 'idea'
    ]
    
    @staticmethod
    def detect_intent(query: str) -> Dict[str, bool]:
        """
        Detect the academic intent behind a student query.
        Returns a dictionary of intent flags.
        """
        query_lower = query.lower()
        
        intent = {
            'is_assignment_related': any(kw in query_lower for kw in AssignmentContextAnalyzer.ASSIGNMENT_KEYWORDS),
            'is_deadline_query': any(kw in query_lower for kw in AssignmentContextAnalyzer.DEADLINE_KEYWORDS),
            'needs_help': any(kw in query_lower for kw in AssignmentContextAnalyzer.HELP_KEYWORDS),
            'wants_feedback': any(kw in query_lower for kw in AssignmentContextAnalyzer.FEEDBACK_KEYWORDS),
            'wants_explanation': any(kw in query_lower for kw in AssignmentContextAnalyzer.CONCEPT_KEYWORDS),
        }
        
        return intent
    
    @staticmethod
    def extract_assignment_type(query: str) -> Optional[str]:
        """Extract the type of assignment being discussed"""
        query_lower = query.lower()
        
        assignment_types = {
            'essay': ['essay', 'paper'],
            'report': ['report', 'write-up'],
            'presentation': ['presentation', 'slides', 'present'],
            'lab': ['lab', 'practical', 'experiment'],
            'project': ['project'],
            'coursework': ['coursework'],
        }
        
        for atype, keywords in assignment_types.items():
            if any(kw in query_lower for kw in keywords):
                return atype
        
        return None
    
    @staticmethod
    def get_guidance_context(query: str) -> str:
        """
        Generate additional context for the LLM about the student's intent.
        This helps the Module Convenor provide more targeted guidance.
        """
        intent = AssignmentContextAnalyzer.detect_intent(query)
        assignment_type = AssignmentContextAnalyzer.extract_assignment_type(query)
        
        context_parts = []
        
        if intent['is_assignment_related']:
            if assignment_type:
                context_parts.append(f"This is about a {assignment_type}.")
            else:
                context_parts.append("This is about coursework/assignments.")
        
        if intent['needs_help']:
            context_parts.append("The student needs help understanding something.")
        
        if intent['wants_feedback']:
            context_parts.append("The student wants feedback or suggestions for improvement.")
        
        if intent['is_deadline_query']:
            context_parts.append("The student is asking about deadlines or submission dates.")
        
        if intent['wants_explanation']:
            context_parts.append("The student wants a concept explained.")
        
        if context_parts:
            return "[Context: " + " ".join(context_parts) + "]"
        
        return ""


def enhance_convenor_prompt(base_prompt: str, query: str, session_context: str = "") -> str:
    """
    Enhance a prompt with Module Convenor personality and context awareness.
    
    Args:
        base_prompt: The basic prompt template
        query: The student's query
        session_context: Previous conversation context
        
    Returns:
        Enhanced prompt with convenor style and context
    """
    guidance_context = AssignmentContextAnalyzer.get_guidance_context(query)
    
    # Build the enhanced prompt
    enhanced = base_prompt
    
    # Add session context if available
    if session_context:
        enhanced = session_context + enhanced
    
    # Add guidance context
    if guidance_context:
        enhanced = enhanced.replace(
            "Question: " + query,
            guidance_context + "\nQuestion: " + query
        )
    
    return enhanced


def get_convenor_system_prompt() -> str:
    """
    Get the Module Convenor system prompt that defines the assistant's personality
    and behavior as an intelligent academic guide.
    """
    from config import CONVENOR_NAME, CONVENOR_STYLE
    
    return f"""You are EduMate, an AI assistant acting as a mini version of {CONVENOR_NAME}, the module convenor.

Your role is to provide intelligent, personalized academic guidance - not just answer questions, but act as a supportive mentor who:

1. **Understands Context**: Consider the student's coursework, assignment type, and academic progress when responding
2. **Provides Guidance**: Offer tailored advice, not just facts - help students think critically and develop understanding
3. **Gives Feedback**: When appropriate, suggest areas for improvement or deeper exploration
4. **Maintains Mentorship Style**: Be {CONVENOR_STYLE}, encouraging independent learning while providing clear support
5. **Cites Sources**: Use citation markers [①, ②, ...] to reference course materials

Remember: You're not just a Q&A bot - you're an intelligent guide helping students succeed in their academic journey."""
