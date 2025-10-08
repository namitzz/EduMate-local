# Example Usage: app_simple.py

This document shows real-world examples of using the simple Streamlit app.

## Prerequisites

1. Backend running: `uvicorn main:app --reload --port 8000`
2. UI running: `streamlit run app_simple.py`
3. Documents ingested: `python backend/ingest.py`

## Example Session 1: Getting Started

### User Opens App

**Screen shows:**
```
🎓 EduMate - Your Study Assistant
Ask me anything about your course materials!

🤖 Hi! I'm EduMate, your AI study assistant. I can help you with 
   questions about your course materials. What would you like to know?

[Type your question here...]
```

### User Asks First Question

**User types:** "What is machine learning?"

**App response:**
```
👤 What is machine learning?

🤖 Machine learning is a subset of artificial intelligence that enables 
   systems to learn and improve from experience without being explicitly 
   programmed. It focuses on developing algorithms that can analyze data, 
   identify patterns, and make decisions with minimal human intervention.

   📚 Sources ▼
   - Introduction_to_AI.pdf
   - ML_Fundamentals.docx
```

### User Asks Follow-up

**User types:** "Can you explain supervised learning?"

**App response:**
```
👤 Can you explain supervised learning?

🤖 Supervised learning is a type of machine learning where the algorithm 
   learns from labeled training data. In this approach, the model is 
   provided with input-output pairs and learns to map inputs to correct 
   outputs. Common examples include classification and regression tasks.

   📚 Sources ▼
   - ML_Types.pdf
   - Supervised_Learning_Notes.docx
```

## Example Session 2: Study Help

### User Seeks Study Guidance

**User types:** "How should I prepare for the exam?"

**App response:**
```
👤 How should I prepare for the exam?

🤖 Based on the course materials, here are key preparation tips:

   1. Review all lecture slides and notes
   2. Practice the example problems in chapters 3-5
   3. Understand the key concepts: neural networks, gradient descent, 
      and backpropagation
   4. Complete the practice questions at the end of each module
   5. Create summary notes for each topic

   📚 Sources ▼
   - Exam_Preparation_Guide.pdf
   - Study_Tips.txt
```

## Example Session 3: Deep Dive

### User Explores Complex Topic

**User types:** "What are the main differences between CNN and RNN?"

**App response:**
```
👤 What are the main differences between CNN and RNN?

🤖 Convolutional Neural Networks (CNN) and Recurrent Neural Networks (RNN) 
   differ in several key ways:

   **CNNs:**
   - Designed for spatial data (images)
   - Use convolutional layers to detect features
   - Excellent for computer vision tasks
   
   **RNNs:**
   - Designed for sequential data (text, time series)
   - Have memory of previous inputs
   - Ideal for natural language processing

   📚 Sources ▼
   - Neural_Network_Architectures.pdf
   - Deep_Learning_Chapter_4.docx
   - CNN_vs_RNN_Comparison.pptx
```

## Example Session 4: Error Handling

### Backend Temporarily Down

**User types:** "What is reinforcement learning?"

**App response:**
```
👤 What is reinforcement learning?

⚠️ ❌ Cannot connect to the API. Make sure the backend is running 
   at http://localhost:8000
```

**Sidebar shows:**
```
### API Status:
❌ API is offline
API URL: http://localhost:8000
```

### User Restarts Backend and Retries

**App response:**
```
👤 What is reinforcement learning?

🤖 Reinforcement learning is a type of machine learning where an agent 
   learns to make decisions by interacting with an environment. The agent 
   receives rewards or penalties based on its actions and learns to 
   maximize cumulative reward over time.

   📚 Sources ▼
   - RL_Introduction.pdf
```

## Example Session 5: Multiple Questions

### Conversation Flow

```
Chat History:
─────────────────────────────────────────────

🤖 Hi! I'm EduMate, your AI study assistant...

👤 What is gradient descent?

🤖 Gradient descent is an optimization algorithm used to minimize 
   the loss function in machine learning models...
   📚 Sources ▼

👤 How does it work?

🤖 Gradient descent works by iteratively moving in the direction 
   of steepest descent, updating parameters to reduce error...
   📚 Sources ▼

👤 What's the learning rate?

🤖 The learning rate is a hyperparameter that determines the size 
   of steps taken during gradient descent optimization...
   📚 Sources ▼

👤 Thanks!

🤖 You're welcome! Feel free to ask if you have more questions 
   about your course materials. Happy studying! 📚

[Type your question here...]
```

## Example Session 6: Using Clear History

### Before Clearing

```
Chat shows 10 messages...

User clicks [🗑️ Clear Chat History] in sidebar
```

### After Clearing

```
🤖 Hi! I'm EduMate, your AI study assistant. I can help you with 
   questions about your course materials. What would you like to know?

[Type your question here...]
```

*All previous messages are removed*

## Common Query Patterns

### 1. Conceptual Questions
```
"What is [concept]?"
"Explain [topic]"
"Define [term]"
```

### 2. Comparison Questions
```
"What's the difference between [A] and [B]?"
"Compare [concept1] with [concept2]"
"[Topic1] vs [Topic2]"
```

### 3. How-To Questions
```
"How do I [task]?"
"How does [system] work?"
"What are the steps to [process]?"
```

### 4. Study Help
```
"How should I prepare for [exam]?"
"What are the key concepts in [chapter]?"
"Summary of [topic]"
```

### 5. Code/Implementation
```
"Show me an example of [algorithm]"
"How to implement [function]?"
"Code for [task]"
```

## Sample Queries by Subject

### Computer Science
- "What is Big O notation?"
- "Explain binary search trees"
- "How does quicksort work?"
- "What are design patterns?"

### Mathematics
- "What is a derivative?"
- "Explain linear algebra"
- "How to solve matrix equations?"
- "What is probability distribution?"

### Data Science
- "What is data preprocessing?"
- "Explain feature engineering"
- "How to handle missing data?"
- "What is cross-validation?"

### Biology
- "What is photosynthesis?"
- "Explain cell division"
- "How does DNA replication work?"
- "What are enzymes?"

### History
- "What caused World War I?"
- "Explain the Renaissance period"
- "Who was [historical figure]?"
- "What happened in [event]?"

## Expected Response Times

| Query Type | Expected Time | Example |
|------------|---------------|---------|
| Greeting | < 1 second | "Hi" |
| Simple fact | 2-4 seconds | "What is X?" |
| Explanation | 4-6 seconds | "Explain Y" |
| Complex analysis | 6-10 seconds | "Compare A vs B" |
| Multi-part | 8-12 seconds | "Explain X, Y, and Z" |

## Tips for Best Results

### ✅ Good Queries
- "What is supervised learning?" - Clear and specific
- "Explain gradient descent in simple terms" - Request for clarity
- "How do I implement a neural network?" - Actionable
- "Compare CNN and RNN architectures" - Comparative

### ❌ Less Effective Queries
- "Help" - Too vague
- "Everything about AI" - Too broad
- "asdfjkl" - Not a real question
- "?" - No context

## Advanced Usage

### Multi-turn Conversations
```
👤 What is machine learning?
🤖 [Explains ML basics]

👤 Can you give me an example?
🤖 [Provides example using context from previous answer]

👤 How would I implement this?
🤖 [Builds on previous responses to give implementation guidance]
```

### Asking for Clarification
```
👤 What is neural networks?
🤖 [Provides technical explanation]

👤 Can you explain that in simpler terms?
🤖 [Provides simplified explanation]
```

### Requesting Specific Information
```
👤 What's in chapter 5 about decision trees?
🤖 [Focuses on chapter 5 content]

👤 Give me the key formulas from that chapter
🤖 [Lists relevant formulas]
```

## Troubleshooting Common Issues

### Issue: No Sources Shown
**Possible cause:** Question is too general or greeting
**Solution:** Ask more specific questions about course content

### Issue: Irrelevant Answer
**Possible cause:** Topic not in course materials
**Solution:** Rephrase or ask about topics covered in your courses

### Issue: Slow Response
**Possible cause:** Complex query or high server load
**Solution:** Wait patiently or simplify the question

### Issue: Error Message
**Possible cause:** Backend connection issue
**Solution:** Check API status in sidebar, restart backend if needed

## Session Statistics

### Typical Usage Session
- **Duration**: 10-20 minutes
- **Questions asked**: 5-15
- **Topics covered**: 2-5
- **Total messages**: 10-30

### Power User Session
- **Duration**: 30-60 minutes
- **Questions asked**: 20-40
- **Topics covered**: 5-10
- **Total messages**: 40-80

## Export Your Session

While not built-in, you can:
1. Take screenshots
2. Copy-paste conversations
3. Use browser's save page function
4. Request export feature (see customization guide)

## Next Steps

After trying the examples:
1. Ask your own questions
2. Explore your course materials
3. Try different query styles
4. Use clear history to start fresh topics
5. Check the Testing Guide for more scenarios

## Learn More

- 📖 [README_SIMPLE.md](README_SIMPLE.md) - Full documentation
- 🧪 [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing scenarios
- 👁️ [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Visual reference
- ⚡ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Developer guide

---

**Happy Learning with EduMate! 🎓**
