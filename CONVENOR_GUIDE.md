# Module Convenor Assistant - User Guide

## Overview

EduMate has been enhanced from a basic Q&A chatbot to an **AI-powered Module Convenor Assistant** that provides intelligent, personalized academic guidance inspired by Prof. Zeng's mentorship style.

## What's New?

### 🎓 Convenor Mode (Recommended)

The new **Convenor Mode** transforms EduMate into an intelligent academic guide that:

1. **Understands Assignment Context**
   - Detects assignment types (essay, report, lab, presentation, etc.)
   - Recognizes your academic intent (need help, want feedback, seeking explanation)
   - Identifies deadline-related queries

2. **Provides Personalized Guidance**
   - Maintains conversation memory across your session
   - Tailors responses based on previous discussions
   - Offers academic mentorship, not just answers

3. **Acts Like Prof. Zeng**
   - Friendly and supportive mentorship style
   - Encourages critical thinking and independent learning
   - Provides guidance while respecting your learning journey

## How to Use

### Starting a Conversation

1. **Open the Streamlit UI** (default: http://localhost:8501)
2. **Select Convenor Mode** in the sidebar (recommended)
3. **Ask your question** naturally, as you would to a module convenor

### Example Conversations

#### Assignment Help
```
You: "I'm working on my essay about machine learning. Can you help me understand 
the key concepts I should cover?"

EduMate: "Of course! For your essay on machine learning, let me guide you through 
the key concepts you should cover based on our course materials [①]...

Consider structuring your essay around:
1. Supervised vs. Unsupervised Learning [①]
2. Key algorithms covered in Week 3-5 [②]
3. Real-world applications [③]

As you work on this, think about: How do these concepts connect to the learning 
outcomes we discussed? What examples from the lectures best illustrate these ideas?

Would you like me to dive deeper into any specific area?"
```

#### Feedback Request
```
You: "I'm not sure if my approach to the lab assignment is correct. Can you 
give me feedback?"

EduMate: "I'd be happy to provide guidance! From our course materials [①], the 
lab assignment should focus on...

To assess your approach, consider these questions:
- Does it address all the required components mentioned in the brief [②]?
- Have you incorporated the concepts from Week 4 lectures [③]?
- Is your methodology sound and well-justified?

What specific part of your approach are you uncertain about? That will help me 
provide more targeted feedback."
```

#### Concept Explanation
```
You: "Can you explain the difference between supervised and unsupervised learning?"

EduMate: "Great question! Let me explain this clearly with reference to our 
course materials [①]...

**Supervised Learning:** [explanation with examples from course]
**Unsupervised Learning:** [explanation with examples from course]

To help you understand this better, consider: What problems would each approach 
be suitable for? Can you think of examples from the assignments where we've used 
each type?

The key distinction is in the role of labeled data, which we covered in depth 
in Week 3 [②]."
```

### Session Memory

EduMate remembers your conversation within a session (1 hour timeout):

```
You: "What are the learning outcomes for this module?"
EduMate: [Provides learning outcomes from course materials]

You: "How does my assignment relate to these?"
EduMate: "Based on what we just discussed about the learning outcomes, your 
assignment directly addresses..." [References previous answer]
```

### Tips for Best Results

1. **Be Specific**: "Help me with my essay on AI ethics" is better than "Help me with my essay"

2. **Ask Follow-ups**: EduMate remembers context, so build on previous questions

3. **Request Feedback**: Don't just ask for answers - ask for guidance on your thinking

4. **Use Convenor Mode**: It's designed for comprehensive academic support

## Available Modes

### 🎓 Convenor Mode (Recommended)
**Best for:**
- Assignment help and guidance
- Concept explanations with academic context
- Feedback on your approach
- Understanding course requirements
- Personalized learning support

**Features:**
- RAG retrieval from course materials
- Session memory for context
- Assignment context understanding
- Module convenor personality

### 📚 Document Q&A Mode
**Best for:**
- Quick lookups in course materials
- Finding specific information
- Getting cited references

**Features:**
- RAG retrieval with citations
- Concise, factual answers
- No session memory

### 💪 Study Coach Mode
**Best for:**
- General study advice
- Time management tips
- Motivation and study strategies

**Features:**
- No document retrieval
- General academic coaching
- Encouraging tone

### ⚡ Quick Facts Mode
**Best for:**
- Very quick questions
- Yes/no answers
- Simple definitions

**Features:**
- No document retrieval
- Very brief responses
- Fast answers

## Understanding Assignment Context

EduMate can detect and understand:

### Assignment Types
- Essays and papers
- Reports and write-ups
- Presentations and slides
- Labs and practicals
- Projects and coursework

### Student Intent
- **Needs Help**: "I'm stuck on...", "I don't understand..."
- **Wants Feedback**: "Can you review...", "What do you think about..."
- **Wants Explanation**: "Explain...", "What is...", "How does..."
- **Deadline Query**: "When is...", "Deadline for...", "Due date..."

### Guidance Context

Based on your question, EduMate provides:
- Targeted assignment guidance
- Relevant course material references
- Academic mentorship advice
- Critical thinking prompts

## Session Management

### Session Lifecycle
1. **New Session**: Started automatically when you open the app
2. **Active Session**: Lasts for 1 hour from last activity
3. **Session Timeout**: After 1 hour of inactivity
4. **Clear Session**: Use "Clear Conversation" button in sidebar

### What's Stored
- Last 10 messages (configurable)
- Conversation context for continuity
- No personal data or assignments stored
- Automatic cleanup after timeout

### Privacy
- Session data is temporary (1-hour lifetime)
- Stored in memory only (not persisted to disk)
- Each user has isolated sessions
- No tracking across sessions

## Advanced Features

### Citation Markers

EduMate uses numbered markers to cite sources:

```
"The learning outcomes [①] state that students should... This is reinforced 
in the assessment criteria [②]..."

Sources:
① module_handbook.pdf (chunk 3)
② assessment_brief.pdf (chunk 1)
```

### Context-Aware Prompts

When using Convenor Mode, your prompts are enhanced with:
- Previous conversation summary
- Assignment type detection
- Student intent analysis
- Guidance context

This happens automatically - you just ask questions naturally!

### Error Handling

If EduMate encounters issues:
- **No Context Found**: Suggests rephrasing or checking documents
- **Retrieval Error**: Provides troubleshooting steps
- **Model Timeout**: Recommends simpler questions

## Best Practices

### For Assignment Help
1. Start with your specific question or problem
2. Provide context about what you've already tried
3. Ask for guidance, not just answers
4. Build on the conversation with follow-ups

### For Concept Understanding
1. Ask for explanations with examples
2. Request connections to course materials
3. Follow up with "How does this relate to...?"
4. Ask for practice suggestions

### For Feedback
1. Describe your current approach
2. Ask specific questions about your thinking
3. Request guidance on improvement areas
4. Discuss alternative perspectives

## Troubleshooting

### "I'm not getting good responses"
- Try Convenor Mode instead of other modes
- Be more specific in your questions
- Provide more context about your needs
- Check that documents are ingested (corpus/)

### "EduMate doesn't remember previous messages"
- Ensure you're using the same session (don't refresh)
- Check that session memory is enabled (should be by default)
- Sessions timeout after 1 hour of inactivity

### "No relevant sources found"
- Check that course materials are in backend/corpus/
- Run `python backend/ingest.py` to update the index
- Try rephrasing your question with different keywords

## Configuration

### For Administrators

Edit `backend/config.py` to customize:

```python
# Session memory settings
ENABLE_SESSION_MEMORY = True
MAX_SESSION_MESSAGES = 10  # Number of messages to remember

# Convenor personality
CONVENOR_NAME = "Prof. Zeng"
CONVENOR_STYLE = "friendly and supportive, like a dedicated module convenor"

# Performance tuning
FAST_MODE = True
TOP_K = 3  # Number of documents to retrieve
MAX_TOKENS = 400  # Response length
```

## FAQ

**Q: Does EduMate replace the module convenor?**  
A: No! EduMate is a supplementary tool that provides guidance based on course materials. It can't replace human judgment, complex discussions, or personalized academic advice from your actual module convenor.

**Q: Can I use this for exam answers?**  
A: EduMate is designed to help you learn and understand, not to provide direct exam answers. Use it for study guidance, concept clarification, and academic support.

**Q: Is my conversation data saved?**  
A: Session data is temporary (1-hour lifetime) and stored in memory only. Nothing is persisted beyond the session timeout.

**Q: What documents can EduMate access?**  
A: Only documents in the `backend/corpus/` directory that have been ingested. It doesn't have access to the internet or any other sources.

**Q: How accurate are the responses?**  
A: EduMate is powered by GPT-3.5-turbo and retrieves information from course materials. While generally accurate, always verify important information and think critically about the guidance provided.

## Getting Help

If you encounter issues or have suggestions:
1. Check the logs in the backend console
2. Verify the API is healthy (green status in sidebar)
3. Try clearing your session and starting fresh
4. Check the GitHub repository for updates

## Future Enhancements

Potential upcoming features:
- Progress tracking across multiple sessions
- Assignment deadline tracking and reminders
- Personalized study plans
- Integration with learning analytics
- Multi-file upload capability
- Enhanced feedback on submitted work

---

**Remember**: EduMate is here to guide your learning journey, not to replace your own critical thinking and academic development. Use it as a supportive tool to enhance your understanding and achieve your learning goals! 🎓
