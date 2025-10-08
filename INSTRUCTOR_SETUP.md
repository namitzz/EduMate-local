# EduMate Module Convenor - Instructor Setup Guide

## Quick Start for Module Convenors

This guide will help you set up EduMate as your AI Module Convenor Assistant in under 10 minutes.

## 📋 Prerequisites

- Backend deployed on Fly.io (already configured)
- Access to course materials (PDFs, DOCX, PPTX)
- Basic understanding of your course structure

## 🗂️ Step 1: Organize Your Course Materials

Create a well-structured corpus for better responses:

### Recommended Directory Structure

```
backend/corpus/
├── course_info/
│   ├── Course_Handbook_2024.pdf
│   ├── Module_Overview.pdf
│   └── Assessment_Schedule.pdf
├── lectures/
│   ├── Week_01_Introduction.pdf
│   ├── Week_02_Fundamentals.pdf
│   ├── Week_03_Advanced_Topics.pdf
│   └── ...
├── assignments/
│   ├── Assignment_1_Brief.pdf
│   ├── Assignment_1_Rubric.pdf
│   ├── Assignment_2_Brief.pdf
│   └── Assignment_2_Rubric.pdf
├── readings/
│   ├── Required_Reading_Chapter_1.pdf
│   ├── Supplementary_Reading_1.pdf
│   └── ...
└── sample_solutions/
    ├── Example_Solution_1.pdf
    └── Past_Exam_Solutions.pdf
```

### File Naming Best Practices

✅ **Good Names**:
- `Assignment_1_Database_Design_Brief.pdf`
- `Lecture_05_Normalization_Theory.pdf`
- `Rubric_Final_Project.pdf`
- `Course_Handbook_CS101_2024.pdf`

❌ **Avoid**:
- `Untitled.pdf`
- `Document1.docx`
- `ass1.pdf`
- `lecture.pptx`

**Why?**: Clear names help the AI provide better context and citations.

### Supported File Formats

- **PDF** (.pdf) - Lectures, readings, assignment briefs
- **DOCX** (.docx) - Word documents
- **PPTX** (.pptx) - PowerPoint presentations
- **TXT** (.txt) - Plain text files
- **HTML** (.html) - Web-based content

## 📚 Step 2: Add Your Materials

### Option A: Local Development

1. **Copy files to corpus directory**:
   ```bash
   cd backend
   mkdir -p corpus
   # Copy your files into corpus/
   ```

2. **Run ingestion**:
   ```bash
   python ingest.py
   ```

3. **Verify**:
   ```bash
   # Check chroma_db directory was created
   ls -la chroma_db/
   ```

### Option B: Production (Fly.io)

1. **Prepare your corpus locally**:
   ```bash
   backend/corpus/
   ```

2. **Deploy to Fly.io**:
   ```bash
   cd backend
   fly deploy
   ```

The ingestion happens automatically during deployment.

## 🎯 Step 3: Customize the Persona (Optional)

Edit `backend/persona.py` to match your teaching style:

### Example Customization

```python
# In backend/persona.py

BASE_PERSONA = (
    "You are an AI Module Convenor Assistant for CS101: Introduction to Databases, "
    "modeled after Prof. Jane Smith. "
    "You provide supportive, practical guidance with a focus on real-world applications. "
    "Your style is encouraging and uses industry examples. "
    # ... rest of persona
)
```

### Tone Adjustments

You can adjust:
- **Formality level**: Professional vs. casual
- **Encouragement style**: Supportive vs. challenging
- **Detail level**: Concise vs. comprehensive
- **Example types**: Theoretical vs. practical

## 🎨 Step 4: Configure Interaction Modes

### Assignment Help Settings

Edit the assignment help guidance in `persona.py`:

```python
if intent == InteractionIntent.ASSIGNMENT_HELP:
    specific_guidance = (
        "\n\nFor assignment help:\n"
        "- Reference assignment requirements from [course name]\n"
        "- Focus on [your specific priorities]\n"
        "- Encourage [your preferred approach]\n"
        # ... customize further
    )
```

### Exam Preparation Focus

Adjust exam prep guidance based on your assessment style:

```python
elif intent == InteractionIntent.EXAM_PREPARATION:
    specific_guidance = (
        "\n\nFor exam preparation:\n"
        "- The exam focuses on [your key topics]\n"
        "- [Your exam format]: MCQ, essays, practical\n"
        "- Recommended study approach: [your strategy]\n"
    )
```

## ⚙️ Step 5: Configure Settings

Edit `backend/config.py`:

```python
# Memory settings
MAX_CONVERSATION_HISTORY = 10  # Number of turns to remember
ENABLE_CONVERSATION_MEMORY = True  # Context tracking

# RAG settings
TOP_K = 3  # Number of document chunks to retrieve
CHUNK_SIZE = 600  # Size of document chunks
FAST_MODE = True  # Faster responses

# LLM settings
TEMPERATURE = 0.3  # Creativity (0.0-1.0)
MAX_TOKENS = 400  # Response length
```

### Recommended Settings by Use Case

**For Large Courses (100+ students)**:
```python
FAST_MODE = True
TOP_K = 3
MAX_TOKENS = 400
TEMPERATURE = 0.2  # More consistent
```

**For Small Seminars**:
```python
FAST_MODE = False
TOP_K = 5
MAX_TOKENS = 600
TEMPERATURE = 0.4  # More creative
```

**For Technical Courses**:
```python
TEMPERATURE = 0.2  # Precise answers
TOP_K = 4
CHUNK_SIZE = 800  # Larger context
```

## 🧪 Step 6: Test Your Setup

### Quick Test Questions

Try asking the assistant:

1. **Course Info**: "What are the assessment requirements?"
2. **Concept**: "Explain [key concept from your course]"
3. **Assignment**: "How should I approach assignment 1?"
4. **Exam**: "What should I focus on for the exam?"
5. **Follow-up**: "Can you give me an example?"

### Verify Responses

Check that the assistant:
- ✅ References your course materials
- ✅ Uses appropriate academic tone
- ✅ Provides structured guidance
- ✅ Cites sources correctly
- ✅ Maintains conversation context

### Health Check

```bash
curl https://edumate-local.fly.dev/health
# Should return: {"ok": true}
```

## 📊 Step 7: Monitor Usage

### View Session Patterns

Check what students are asking about:

```bash
curl https://edumate-local.fly.dev/memory/{session_id}
```

### Common Questions

Look for patterns to identify:
- Topics students struggle with
- Assignment areas needing clarification
- Common misconceptions
- Areas where materials need expansion

## 💡 Best Practices

### Do's ✅

1. **Keep materials updated**: Add new content regularly
2. **Use clear file names**: Help the AI find relevant content
3. **Include rubrics**: Essential for assignment guidance
4. **Add examples**: Past work helps students understand expectations
5. **Test regularly**: Try questions students might ask
6. **Update persona**: Adjust tone based on feedback

### Don'ts ❌

1. **Don't upload solutions**: Guide, don't give answers
2. **Don't use unclear names**: "doc1.pdf" isn't helpful
3. **Don't ignore context**: Session memory is powerful, use it
4. **Don't overload**: Too many documents can dilute quality
5. **Don't forget privacy**: No student personal data in corpus

## 🔄 Maintenance

### Weekly Tasks

- [ ] Check for new course materials to add
- [ ] Review common student questions
- [ ] Test key assignment guidance
- [ ] Update any changed rubrics

### Per Semester

- [ ] Remove outdated materials
- [ ] Update course handbook
- [ ] Refresh lecture content
- [ ] Test all assignment briefs
- [ ] Adjust persona if needed

### When Issues Arise

1. **Poor answers**: Check if relevant documents are in corpus
2. **Wrong citations**: Verify file names and content
3. **Unclear guidance**: Adjust persona prompts
4. **Slow responses**: Enable FAST_MODE
5. **Context loss**: Check session_id is being sent

## 🎓 Pedagogical Considerations

### Academic Integrity

The assistant is designed to:
- **Guide, not solve**: Provides structure, not complete answers
- **Encourage thinking**: Asks reflection questions
- **Build skills**: Teaches approach, not just content
- **Maintain standards**: Upholds academic expectations

### Accessibility

The assistant helps:
- **24/7 availability**: Students can get help anytime
- **Multiple explanations**: Different ways to understand concepts
- **Self-paced learning**: No pressure of asking in class
- **Language support**: Clear, structured responses

### Effectiveness Metrics

Track (informally):
- Reduction in basic questions during office hours
- Improved assignment submission quality
- Better exam preparation (based on questions asked)
- Student satisfaction with support

## 🚀 Advanced Features

### Custom Intent Types

Add your own interaction types in `persona.py`:

```python
class InteractionIntent(Enum):
    # Existing intents...
    LAB_SUPPORT = "lab_support"  # Your custom intent
    PROJECT_GUIDANCE = "project_guidance"
```

### Integration Ideas

- **Office Hours**: Use assistant output as starting point
- **FAQ Updates**: Identify common questions to document
- **Content Gaps**: See what students ask that isn't covered
- **Assessment Design**: Understand what students find difficult

## 📞 Support

### Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:
- Deployment issues
- Ingestion problems
- Performance tuning
- Memory management

### Community

- GitHub Issues: [Report bugs or suggest features]
- Discussions: [Share best practices]

## 📚 Additional Resources

- [MODULE_CONVENOR_GUIDE.md](MODULE_CONVENOR_GUIDE.md) - Detailed feature guide
- [QUICKSTART.md](QUICKSTART.md) - Fast deployment
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details

---

## Quick Reference Card

```
📁 Add materials → corpus/
🔄 Ingest docs → python ingest.py
🎨 Customize → backend/persona.py
⚙️ Configure → backend/config.py
🚀 Deploy → fly deploy
✅ Test → Ask common questions
📊 Monitor → Check /memory endpoint
```

**Need help?** Check the documentation or open an issue on GitHub!
