"""
Module Convenor Persona & Prompt Templates
==========================================
Defines the AI Module Convenor Assistant persona and intelligent prompt templates
for different types of academic guidance and student interactions.
"""

from typing import Dict, List, Optional
from enum import Enum


class InteractionIntent(Enum):
    """Different types of student interaction intents"""
    ASSIGNMENT_HELP = "assignment_help"
    CONCEPT_CLARIFICATION = "concept_clarification"
    EXAM_PREPARATION = "exam_preparation"
    GENERAL_QUERY = "general_query"
    PROGRESS_FEEDBACK = "progress_feedback"
    STUDY_PLANNING = "study_planning"


def detect_intent(query: str, conversation_history: Optional[List[Dict]] = None) -> InteractionIntent:
    """
    Detect the student's interaction intent from their query.
    
    Args:
        query: Student's question or message
        conversation_history: Recent conversation context
        
    Returns:
        Detected interaction intent
    """
    query_lower = query.lower()
    
    # Assignment-related keywords
    assignment_keywords = [
        "assignment", "homework", "coursework", "task", "project",
        "deadline", "submit", "submission", "rubric", "criteria",
        "grade", "grading", "marking", "feedback on my", "review my"
    ]
    
    # Concept clarification keywords
    concept_keywords = [
        "what is", "explain", "clarify", "understand", "confused",
        "how does", "why does", "difference between", "mean by",
        "define", "definition", "concept", "theory", "principle"
    ]
    
    # Exam preparation keywords
    exam_keywords = [
        "exam", "test", "assessment", "quiz", "revision",
        "prepare for", "study for", "practice", "review for"
    ]
    
    # Study planning keywords
    planning_keywords = [
        "study plan", "schedule", "organize", "time management",
        "how to study", "learning strategy", "study tips", "improve"
    ]
    
    # Progress/feedback keywords
    progress_keywords = [
        "how am i doing", "my progress", "feedback", "struggling with",
        "difficulty with", "help me with", "stuck on"
    ]
    
    # Check intent based on keywords
    if any(keyword in query_lower for keyword in assignment_keywords):
        return InteractionIntent.ASSIGNMENT_HELP
    elif any(keyword in query_lower for keyword in exam_keywords):
        return InteractionIntent.EXAM_PREPARATION
    elif any(keyword in query_lower for keyword in planning_keywords):
        return InteractionIntent.STUDY_PLANNING
    elif any(keyword in query_lower for keyword in progress_keywords):
        return InteractionIntent.PROGRESS_FEEDBACK
    elif any(keyword in query_lower for keyword in concept_keywords):
        return InteractionIntent.CONCEPT_CLARIFICATION
    else:
        return InteractionIntent.GENERAL_QUERY


class ModuleConvenorPersona:
    """
    Defines the Module Convenor Assistant persona with tailored prompt templates
    for different academic guidance scenarios.
    """
    
    # Base persona description
    BASE_PERSONA = (
        "You are an AI Module Convenor Assistant, modeled after an experienced university professor. "
        "You provide personalized academic guidance, feedback, and mentorship to students. "
        "Your style is supportive, encouraging, and pedagogically sound. "
        "You help students understand course concepts, complete assignments effectively, "
        "and develop strong study habits. You don't just answer questions - you guide learning."
    )
    
    # Tone guidelines
    TONE_GUIDELINES = (
        "Maintain a warm, approachable, yet professional tone. "
        "Be encouraging and constructive. Focus on learning outcomes. "
        "Use 'we' language to create collaboration. "
        "Provide structured guidance with clear action steps."
    )
    
    @staticmethod
    def get_system_prompt(
        intent: InteractionIntent,
        context_available: bool = True,
        conversation_context: Optional[str] = None
    ) -> str:
        """
        Generate an appropriate system prompt based on interaction intent.
        
        Args:
            intent: Detected interaction intent
            context_available: Whether course material context is available
            conversation_context: Recent conversation history
            
        Returns:
            Tailored system prompt
        """
        base = ModuleConvenorPersona.BASE_PERSONA
        
        if intent == InteractionIntent.ASSIGNMENT_HELP:
            specific_guidance = (
                "\n\nFor assignment help:\n"
                "- First, understand what the student is struggling with\n"
                "- Reference the assignment brief and rubric from the course materials\n"
                "- Provide structured guidance (e.g., outline, approach, key points)\n"
                "- Suggest what to focus on, but don't write the assignment for them\n"
                "- Encourage critical thinking and independent work\n"
                "- Remind them of deadlines and submission requirements if relevant"
            )
        elif intent == InteractionIntent.CONCEPT_CLARIFICATION:
            specific_guidance = (
                "\n\nFor concept clarification:\n"
                "- Start with a clear, concise explanation using course terminology\n"
                "- Use examples or analogies to illustrate the concept\n"
                "- Connect the concept to other topics they've learned\n"
                "- Check understanding by suggesting how they might apply this\n"
                "- Point to relevant sections in the course materials for deeper study"
            )
        elif intent == InteractionIntent.EXAM_PREPARATION:
            specific_guidance = (
                "\n\nFor exam preparation:\n"
                "- Identify key topics and learning objectives from the course\n"
                "- Suggest focused study strategies for different topic areas\n"
                "- Recommend practice activities and self-testing approaches\n"
                "- Provide time management advice for exam preparation\n"
                "- Build confidence while setting realistic expectations"
            )
        elif intent == InteractionIntent.STUDY_PLANNING:
            specific_guidance = (
                "\n\nFor study planning:\n"
                "- Help create realistic, achievable study schedules\n"
                "- Suggest evidence-based study techniques\n"
                "- Prioritize topics based on course structure and deadlines\n"
                "- Encourage regular review and active learning\n"
                "- Provide motivational support and practical tips"
            )
        elif intent == InteractionIntent.PROGRESS_FEEDBACK:
            specific_guidance = (
                "\n\nFor progress feedback:\n"
                "- Acknowledge their effort and any progress made\n"
                "- Provide constructive, specific feedback\n"
                "- Identify areas for improvement with actionable steps\n"
                "- Encourage reflection on their learning process\n"
                "- Suggest resources or strategies to address difficulties"
            )
        else:  # GENERAL_QUERY
            specific_guidance = (
                "\n\nFor general queries:\n"
                "- Provide clear, accurate information from course materials\n"
                "- Be concise but comprehensive\n"
                "- Anticipate follow-up questions\n"
                "- Encourage deeper engagement with the material"
            )
        
        # Add context handling
        if context_available:
            context_note = (
                "\n\nYou have access to relevant course materials (lectures, readings, assignment briefs). "
                "Base your responses on this content and cite sources using the provided markers [①, ②, ...]."
            )
        else:
            context_note = (
                "\n\nNote: No specific course materials were found for this query. "
                "Provide general academic guidance based on your educational expertise."
            )
        
        # Add conversation context if available
        conversation_note = ""
        if conversation_context:
            conversation_note = (
                f"\n\nRecent conversation context:\n{conversation_context}\n"
                "Use this context to provide continuity and personalized responses."
            )
        
        return base + specific_guidance + context_note + conversation_note + "\n\n" + ModuleConvenorPersona.TONE_GUIDELINES
    
    @staticmethod
    def format_academic_response(
        answer: str,
        sources: List[str],
        intent: InteractionIntent,
        include_suggestions: bool = True
    ) -> str:
        """
        Format the response with appropriate academic structure and suggestions.
        
        Args:
            answer: Base answer from LLM
            sources: List of source citations
            intent: Interaction intent
            include_suggestions: Whether to add follow-up suggestions
            
        Returns:
            Formatted response with structure and guidance
        """
        formatted = answer
        
        # Add follow-up suggestions based on intent
        if include_suggestions:
            if intent == InteractionIntent.ASSIGNMENT_HELP:
                formatted += (
                    "\n\n**Next Steps:**\n"
                    "- Review the assignment rubric carefully\n"
                    "- Create an outline before you start writing\n"
                    "- Check with me if you need clarification on any requirements"
                )
            elif intent == InteractionIntent.CONCEPT_CLARIFICATION:
                formatted += (
                    "\n\n**To Deepen Your Understanding:**\n"
                    "- Try explaining this concept in your own words\n"
                    "- Look for examples in the course materials\n"
                    "- Consider how this relates to other topics we've covered"
                )
            elif intent == InteractionIntent.EXAM_PREPARATION:
                formatted += (
                    "\n\n**Study Tips:**\n"
                    "- Practice active recall rather than just re-reading\n"
                    "- Create summary notes for each topic\n"
                    "- Test yourself regularly on key concepts"
                )
        
        return formatted


def compose_convenor_prompt(
    contexts: List[Dict],
    user_msg: str,
    conversation_context: Optional[str] = None,
    fast_mode: bool = False
) -> tuple[str, List[str], InteractionIntent]:
    """
    Build an intelligent Module Convenor prompt with context awareness.
    
    Args:
        contexts: Retrieved document chunks
        user_msg: Student's question
        conversation_context: Recent conversation history
        fast_mode: Whether to use faster, more concise prompting
        
    Returns:
        (prompt, sources, detected_intent)
    """
    # Detect interaction intent
    intent = detect_intent(user_msg)
    
    # Prepare context from documents
    sources = []
    ctx_text = []
    
    max_contexts = 3 if fast_mode else 4
    max_snippet_len = 800 if fast_mode else 1200
    
    for i, c in enumerate(contexts[:max_contexts], start=1):
        marker = chr(9311 + i)  # ①, ②, ...
        snippet = c["doc"][:max_snippet_len]
        ctx_text.append(f"[{marker}] {snippet}")
        meta = c.get("meta") or {}
        sources.append(f"{marker} {meta.get('file', 'Unknown')} (chunk {meta.get('chunk', 'N/A')})")
    
    # Get appropriate system prompt
    system_prompt = ModuleConvenorPersona.get_system_prompt(
        intent=intent,
        context_available=bool(contexts),
        conversation_context=conversation_context
    )
    
    # Build the full prompt
    context_block = "\n".join(ctx_text) if ctx_text else "(No specific course materials found)"
    
    prompt = (
        f"{system_prompt}\n\n"
        f"Course Materials Context:\n{context_block}\n\n"
        f"Student Question: {user_msg}\n\n"
        f"Your Response (as Module Convenor):"
    )
    
    return prompt, sources, intent
