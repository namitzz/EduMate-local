# Visual Guide: app_simple.py

This document provides a visual representation of how the simple Streamlit app looks and works.

## Main Interface Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant                                  │
│ Ask me anything about your course materials!                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🤖 Hi! I'm EduMate, your AI study assistant. I can help you      │
│     with questions about your course materials. What would you     │
│     like to know?                                                  │
│                                                                     │
│  👤 What is machine learning?                                      │
│                                                                     │
│  🤖 Machine learning is a subset of artificial intelligence        │
│     that enables systems to learn and improve from experience      │
│     without being explicitly programmed...                         │
│                                                                     │
│     📚 Sources ▼                                                   │
│        - Introduction_to_ML.pdf                                    │
│        - AI_Fundamentals.docx                                      │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Type your question here...                                   [Send]│
└─────────────────────────────────────────────────────────────────────┘
```

## Sidebar

```
┌───────────────────────────┐
│ ℹ️ About                  │
│                           │
│ EduMate is a local AI     │
│ study assistant...        │
│                           │
│ ### Features:             │
│ - 💬 Natural conversation │
│ - 📚 Course documents     │
│ - 🎯 Sourced answers      │
│ - 🔒 Runs locally         │
│                           │
│ ### How to Use:           │
│ 1. Type your question     │
│ 2. Press Enter            │
│ 3. Wait for response      │
│ 4. Check sources          │
│                           │
│ ### API Status:           │
│ ✅ API is online          │
│ API URL:                  │
│ http://localhost:8000     │
│                           │
├───────────────────────────┤
│ 🗑️ Clear Chat History    │
└───────────────────────────┘
```

## Screen States

### 1. Initial Load

```
┌─────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant          │
│ Ask me anything about your course materials!│
├─────────────────────────────────────────────┤
│                                             │
│  🤖 Hi! I'm EduMate, your AI study         │
│     assistant. I can help you with         │
│     questions about your course materials. │
│     What would you like to know?           │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  Type your question here...           [Send]│
└─────────────────────────────────────────────┘
```

### 2. User Typing

```
┌─────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant          │
│ Ask me anything about your course materials!│
├─────────────────────────────────────────────┤
│                                             │
│  🤖 Hi! I'm EduMate...                     │
│                                             │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  What is neural networks?              [Send]│
│  └─ cursor blinking                         │
└─────────────────────────────────────────────┘
```

### 3. Loading State

```
┌─────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant          │
│ Ask me anything about your course materials!│
├─────────────────────────────────────────────┤
│                                             │
│  👤 What is neural networks?               │
│                                             │
│  🤖 ⏳ Thinking...                         │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  Type your question here...           [Send]│
└─────────────────────────────────────────────┘
```

### 4. Response with Sources

```
┌─────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant          │
│ Ask me anything about your course materials!│
├─────────────────────────────────────────────┤
│  👤 What is neural networks?               │
│                                             │
│  🤖 Neural networks are computing systems  │
│     inspired by biological neural networks │
│     that constitute animal brains. They    │
│     consist of interconnected nodes        │
│     (neurons) that process information...  │
│                                             │
│     📚 Sources ▼                           │
│     ├─ Deep_Learning_Basics.pdf            │
│     ├─ AI_Course_Notes.docx                │
│     └─ Neural_Networks_Lecture.pptx        │
│                                             │
├─────────────────────────────────────────────┤
│  Type your question here...           [Send]│
└─────────────────────────────────────────────┘
```

### 5. Error State (Backend Down)

```
┌─────────────────────────────────────────────┐
│ 🎓 EduMate - Your Study Assistant          │
│ Ask me anything about your course materials!│
├─────────────────────────────────────────────┤
│  👤 What is machine learning?              │
│                                             │
│  🤖 ❌ Cannot connect to the API. Make     │
│     sure the backend is running at         │
│     http://localhost:8000                  │
│                                             │
│  ⚠️ [Error displayed in red box]           │
│                                             │
├─────────────────────────────────────────────┤
│  Type your question here...           [Send]│
└─────────────────────────────────────────────┘
```

### 6. Sidebar - API Offline

```
┌───────────────────────────┐
│ ℹ️ About                  │
│                           │
│ EduMate is a local AI...  │
│                           │
│ ### API Status:           │
│ ❌ API is offline         │
│ API URL:                  │
│ http://localhost:8000     │
│                           │
│ ────────────────────────  │
│                           │
│ [🗑️ Clear Chat History]  │
└───────────────────────────┘
```

## User Flow Diagram

```
┌─────────────┐
│   Start     │
│   App       │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Check API Status│ ──► [Health Check]
└────────┬────────┘
         │
         ▼
  ┌──────────────┐
  │ Show Initial │
  │   Message    │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Wait for    │◄────────┐
  │ User Input   │         │
  └──────┬───────┘         │
         │                 │
         ▼                 │
  ┌──────────────┐         │
  │Display User  │         │
  │  Message     │         │
  └──────┬───────┘         │
         │                 │
         ▼                 │
  ┌──────────────┐         │
  │Show Loading  │         │
  │  Spinner     │         │
  └──────┬───────┘         │
         │                 │
         ▼                 │
  ┌──────────────┐         │
  │  Call API    │         │
  │   /chat      │         │
  └──────┬───────┘         │
         │                 │
    ┌────┴────┐            │
    │         │            │
    ▼         ▼            │
[Success] [Error]          │
    │         │            │
    ▼         ▼            │
┌────────┐ ┌──────┐        │
│ Show   │ │ Show │        │
│Answer  │ │Error │        │
│+Sources│ │ Msg  │        │
└───┬────┘ └───┬──┘        │
    │          │           │
    └────┬─────┘           │
         │                 │
         └─────────────────┘
```

## Code Structure Visualization

```
app_simple.py
├── Imports
│   ├── os
│   ├── streamlit
│   └── requests
│
├── Configuration
│   └── API_BASE_URL
│
├── Page Setup
│   ├── set_page_config()
│   ├── title()
│   └── caption()
│
├── Session State
│   └── messages[] initialization
│
├── Display Chat History
│   └── for each message:
│       └── chat_message()
│
├── Chat Input Handler
│   ├── Get user input
│   ├── Add to history
│   ├── Display user message
│   ├── Get assistant response
│   │   ├── spinner("Thinking...")
│   │   ├── POST /chat
│   │   ├── Handle response
│   │   │   ├── Display answer
│   │   │   └── Display sources
│   │   └── Error handling
│   │       ├── ConnectionError
│   │       ├── Timeout
│   │       └── Generic Exception
│   └── Add to history
│
└── Sidebar
    ├── About section
    ├── API health check
    └── Clear chat button
```

## Component Breakdown

### 1. Header Section
```python
st.title("🎓 EduMate - Your Study Assistant")
st.caption("Ask me anything about your course materials!")
```
- Large title with emoji
- Subtitle explaining purpose

### 2. Chat Messages
```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```
- Iterates through message history
- Displays with appropriate icon (👤 or 🤖)

### 3. Chat Input
```python
if user_input := st.chat_input("Type your question here..."):
    # Handle input
```
- Sticky input at bottom
- Send button integrated

### 4. Sources Display
```python
with st.expander("📚 Sources"):
    for source in sources:
        st.markdown(f"- {source}")
```
- Collapsible section
- List of document references

### 5. Error Display
```python
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to the API...")
```
- Red error box
- Clear error message

### 6. API Health Check
```python
health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
if health_response.status_code == 200:
    st.success("✅ API is online")
```
- Green/red indicator
- Real-time status

## Color Scheme

The app uses Streamlit's default theme:

- **Background**: Light gray/white
- **Chat User**: Light blue background
- **Chat Assistant**: Light gray background  
- **Success**: Green (✅)
- **Error**: Red (❌)
- **Info**: Blue (ℹ️)
- **Warning**: Yellow (⚠️)

## Responsive Behavior

### Desktop (> 1024px)
```
┌─────────────┬─────────────────────────────┐
│             │                             │
│   Sidebar   │      Main Chat Area         │
│   (25%)     │         (75%)               │
│             │                             │
└─────────────┴─────────────────────────────┘
```

### Tablet (768px - 1024px)
```
┌─────────────┬─────────────────────┐
│  Sidebar    │    Main Chat        │
│  (30%)      │      (70%)          │
│             │                     │
└─────────────┴─────────────────────┘
```

### Mobile (< 768px)
```
┌─────────────────────────────┐
│      Main Chat Area         │
│       (100%)                │
│                             │
│  [Sidebar hidden by default]│
│  [Hamburger menu to toggle] │
└─────────────────────────────┘
```

## Animation Flow

1. **Page Load**: Fade in (300ms)
2. **Message Appear**: Slide up (200ms)
3. **Spinner**: Rotate animation
4. **Sources Expand**: Slide down (150ms)
5. **Error**: Shake animation (400ms)

## Accessibility Features

- ✅ Semantic HTML structure
- ✅ Proper heading hierarchy
- ✅ ARIA labels on interactive elements
- ✅ Keyboard navigation support
- ✅ Screen reader friendly
- ✅ High contrast text
- ✅ Clear focus indicators

## Comparison: Simple vs Advanced UI

### app_simple.py
```
┌─────────────────────────────┐
│  🎓 Title                   │
├─────────────────────────────┤
│  💬 Chat Messages           │
│  📚 Sources (in expander)   │
├─────────────────────────────┤
│  [Input Box]                │
└─────────────────────────────┘
```

### app_public.py
```
┌─────────────────────────────┐
│  🎓 Title                   │
│  [Docs] [Coach] [Facts]     │ ← Mode selector
├─────────────────────────────┤
│  💬 Chat Messages           │
│  ▌ Streaming cursor         │ ← Live typing
├─────────────────────────────┤
│  [Input Box]                │
└─────────────────────────────┘
```

---

**This visual guide helps developers and users understand the app layout and behavior without needing to run it.**
