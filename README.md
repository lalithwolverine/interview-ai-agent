# Interview Practice Partner - AI Agent

A sophisticated conversational AI agent that helps users prepare for job interviews by conducting mock interviews with intelligent follow-up questions, adaptive difficulty, and comprehensive feedback.

## 🎯 Project Overview

This project is an **Interview Practice Partner** - an AI-powered chatbot that conducts mock interviews for different job roles (Software Engineer, Sales Representative, Retail Associate). The agent demonstrates advanced agentic behavior through a combination of heuristics and LLM-powered decision making.

## ✨ Key Features

- **Voice Mode**: Questions read aloud using text-to-speech; answers captured via microphone input
- **Role-Based Mock Interviews**: Practice for Software Engineer, Sales Representative, or Retail Associate positions
- **Agentic Behavior**: Heuristics layer + LLM instructions for intelligent follow-up decisions
- **Adaptive Difficulty**: Automatically escalates difficulty after 3 consecutive strong answers
- **LLM-Powered Evaluation**: JSON-based evaluation with communication, technical, and examples scores
- **Topic Enforcement**: AI strictly stays on interview topic, redirects off-topic requests
- **Question Bank**: Curated questions with difficulty buckets (easy, medium, hard) and randomness
- **Session Persistence**: Saves interview sessions to JSON files
- **Edge Case Handling**: Gracefully handles silent users, nonsense inputs, and off-topic requests
- **Token Control**: Conservative token limits and error handling for API responses

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   HTML/CSS   │  │  JavaScript  │  │   Chat UI    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTP/REST
┌────────────────────────────┼────────────────────────────────┐
│                    Flask Backend (Python)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              InterviewAgent                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ Heuristics   │  │ QuestionBank │  │ LLMService  │ │  │
│  │  │  Analyzer    │  │              │  │             │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │  │
│  └─────────┼──────────────────┼──────────────────┼───────┘  │
│            │                  │                  │           │
│  ┌─────────┴──────────┐      │      ┌──────────┴────────┐ │
│  │ Session Management │      │      │  Prompt Templates │ │
│  │  - State tracking  │      │      │  - Question gen   │ │
│  │  - File export     │      │      │  - Evaluation     │ │
│  └────────────────────┘      │      └───────────────────┘ │
└───────────────────────────────┼──────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                      │
          ┌─────────┴─────────┐  ┌─────────┴─────────┐
          │  Google Gemini API│  │  Local File System │
          │  - Question gen   │  │  - Session files   │
          │  - Evaluation     │  │  - data/ directory│
          └───────────────────┘  └───────────────────┘
          │
          └─── Browser Web Speech API (TTS/STT)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Modern browser with Web Speech API support (Chrome, Edge, Safari)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd 8fold
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - **Important**: The application will exit with an error if the API key is missing.

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start practicing your interview!

## 📖 Usage Guide

### Starting an Interview

1. **Select a Role**: Type the role name (engineer, sales, or retail) or click the quick action buttons
2. **Answer Questions**: Respond naturally as you would in a real interview
3. **Follow-up Questions**: The AI will ask intelligent follow-up questions based on your responses
4. **Adaptive Difficulty**: After 3 strong answers, questions become more challenging
5. **Get Feedback**: After completing questions, type "feedback" or "summary" to see your analysis

### Example Interactions

#### The Efficient User
```
User: engineer
Bot: Tell me about yourself and your experience...
User: I'm a software engineer with 5 years of experience...
Bot: [After 3 strong answers] [Increased difficulty] Design a scalable system...
```

#### The Confused User
```
User: umm i dont know
Bot: I'm here to help you practice for job interviews...
User: maybe software?
Bot: Tell me about yourself...
```

## 🧪 Demo Scenarios

The application includes four demo transcripts demonstrating different user types:

### 1. **The Confused User** (`demo/transcripts/confused_user.md`)
- **Behavior**: Unsure what they want, provides brief answers
- **Handling**: Multiple prompts to extract detailed information
- **Key Features**: Heuristics detect short answers, system guides user

### 2. **The Efficient User** (`demo/transcripts/efficient_user.md`)
- **Behavior**: Wants quick results, provides detailed answers immediately
- **Handling**: System escalates difficulty after 3 strong answers
- **Key Features**: Difficulty escalation, minimal follow-ups needed

### 3. **The Chatty User** (`demo/transcripts/chatty_user.md`)
- **Behavior**: Goes off-topic frequently, provides lengthy responses
- **Handling**: System extracts key information through focused follow-ups
- **Key Features**: Follow-up questions help focus responses

### 4. **Edge Case User** (`demo/transcripts/edge_case_user.md`)
- **Behavior**: Provides invalid inputs, goes off-topic, requests beyond capabilities
- **Handling**: Graceful error handling, redirection, polite declines
- **Key Features**: Nonsense detection, off-topic handling, capability boundaries

### Reproducing the Demos

To reproduce the demo scenarios:

1. **Confused User**: Start interview, provide brief answers, observe system prompts
2. **Efficient User**: Provide detailed, structured answers with metrics, observe difficulty escalation
3. **Chatty User**: Provide lengthy, tangential answers, observe follow-up questions
4. **Edge Case**: Try nonsense inputs, off-topic requests, observe error handling

## 🏛️ Design Decisions

### AI Quality & Intelligence

1. **Heuristics + LLM Hybrid Approach**
   - **Reason**: Heuristics provide fast, reliable decisions for common cases (short answers, nonsense detection)
   - **LLM**: Used for nuanced follow-up generation and evaluation
   - **Trade-off**: Speed vs. sophistication

2. **Single HF Model for Both Tasks**
   - **Reason**: Simplifies architecture, reduces API complexity
   - **Model**: DialoGPT-large for conversational capabilities
   - **Trade-off**: May not be optimal for each task, but sufficient for MVP

3. **JSON-Only Evaluation Responses**
   - **Reason**: Ensures structured, parseable feedback
   - **Implementation**: Strict prompt engineering + JSON extraction + validation
   - **Fallback**: Default evaluation schema if parsing fails

4. **Difficulty Escalation**
   - **Reason**: Adapts to user skill level, provides appropriate challenge
   - **Trigger**: 3 consecutive strong answers (heuristic-based)
   - **Benefit**: Keeps advanced users engaged

### Safety & Limitations

1. **Profanity Detection**
   - Simple keyword-based detection
   - Redirects to professional communication
   - **Limitation**: May miss subtle inappropriate content

2. **Off-Topic Handling**
   - Detects common off-topic phrases
   - Polite redirection back to interview
   - **Limitation**: May not catch all off-topic responses

3. **Token Control**
   - Conservative `max_tokens` limit (200)
   - Response size validation
   - Error handling for oversized responses
   - **Limitation**: May truncate some valid responses

4. **API Error Handling**
   - Retry logic (3 attempts)
   - Fallback to heuristics if API fails
   - Graceful degradation
   - **Limitation**: Reduced functionality if API unavailable

5. **Session Data Privacy**
   - Sessions saved locally in `data/` directory
   - No external data transmission beyond API calls
   - **Limitation**: No encryption at rest

### Conversation Quality & Voice Mode

1. **Voice Mode Implementation**
   - **Text-to-Speech (TTS)**: Uses Web Speech API to read questions aloud
   - **Speech-to-Text (STT)**: Captures microphone input for answers
   - **Auto-listening**: After reading a question, automatically starts listening for answer
   - **Browser Support**: Works in Chrome, Edge, Safari (Web Speech API)
   - **Design Decision**: Voice mode enhances accessibility and simulates real interview experience

2. **Topic Enforcement**
   - **Strict Interview Focus**: AI is explicitly instructed to ONLY conduct interviews
   - **Off-Topic Detection**: Multi-layer detection (heuristics + LLM)
   - **Polite Redirection**: "Let's focus on the interview. [restate question]"
   - **Design Decision**: Prevents scope creep, maintains professional interview environment

3. **Handling Different User Types**

   **The Confused User**:
   - Detects brief/uncertain answers via heuristics
   - Provides clear guidance: "Could you please elaborate?"
   - Offers encouragement and step-by-step prompts
   - LLM generates supportive follow-ups

   **The Efficient User**:
   - Recognizes detailed, structured answers
   - Acknowledges thoroughness quickly
   - Escalates difficulty after 3 strong answers
   - Minimal follow-ups, moves forward efficiently

   **The Chatty User**:
   - Detects lengthy, tangential responses
   - Extracts key information through focused follow-ups
   - Gently redirects: "That's interesting. Can you relate that to [role]?"
   - Maintains engagement while staying on topic

   **Edge Case Users**:
   - Nonsense detection: "I didn't quite understand that..."
   - Off-topic requests: "Let's focus on the interview..."
   - Invalid inputs: Clear error messages with redirection
   - Beyond capabilities: Polite decline with interview focus reminder

4. **Conversation Quality Priorities**
   - **Natural Flow**: Questions feel like real interview, not robotic
   - **Context Awareness**: Follow-ups reference previous answers
   - **Empathetic Tone**: Supportive for nervous users, professional for all
   - **Adaptive Responses**: Adjusts based on user's communication style
   - **Design Decision**: Quality over speed - better to have thoughtful responses than instant but generic ones

### Technical Implementation

1. **Question Bank with Difficulty Buckets**
   - Curated questions for each role and difficulty level
   - Random selection prevents repetition
   - **Benefit**: Consistent quality, appropriate challenge

2. **Session File Schema**
   - JSON format: `{sessionId, role, mode, startedAt, events[], aggregatedFeedback}`
   - Events include timestamps, speaker, text, and optional evaluation
   - **Benefit**: Complete interview record for analysis

3. **Prompt Engineering**
   - Separate prompts for question generation and evaluation
   - Exact prompts stored in `llmPrompts.py`
   - **Enhanced Prompts**: Include explicit instructions for topic enforcement and user type handling
   - **Benefit**: Easy to iterate and improve, ensures consistent behavior

## 📁 Project Structure

```
8fold/
├── app.py                 # Main Flask application
├── llmPrompts.py          # LLM prompt templates
├── test_app.py            # Unit tests
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore file
├── README.md             # This file
├── data/                 # Session files (created at runtime)
│   └── <sessionId>.json
├── demo/
│   └── transcripts/      # Demo transcripts
│       ├── confused_user.md
│       ├── efficient_user.md
│       ├── chatty_user.md
│       └── edge_case_user.md
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # Styling (dark minimalist theme)
    └── script.js         # Frontend JavaScript
```

## 🧪 Testing

### Running Unit Tests

```bash
python -m pytest test_app.py -v
```

Or using unittest:

```bash
python test_app.py
```

### Test Coverage

The test suite includes:

1. **Session Creation Tests**: Verify session initialization and role assignment
2. **LLM JSON Parsing Tests**: Validate JSON extraction and schema validation
3. **Session File Export Tests**: Verify session file structure and data integrity
4. **Heuristics Tests**: Test answer analysis and nonsense detection

### Mock API Responses

Tests use mocked Hugging Face API responses to avoid API calls during testing.

## 🔧 Configuration

### Environment Variables

- `HUGGINGFACE_API_KEY` (required): Your Hugging Face API token

### API Configuration

- **Model**: `gemini-1.5-flash` (Google Gemini)
- **Max Tokens**: 200 (conservative limit)
- **Timeout**: 30 seconds
- **Retries**: 3 attempts
- **Voice API**: Browser Web Speech API (no external API needed)

### Customization

You can customize:
- **Questions**: Edit `QuestionBank` class in `app.py`
- **Heuristics**: Modify `HeuristicsAnalyzer` class
- **Prompts**: Update `llmPrompts.py`
- **UI**: Edit `templates/index.html` and `static/style.css`

## 📊 Evaluation Schema

The LLM returns evaluation in this exact JSON format:

```json
{
  "scores": {
    "communication": 0-5,
    "technical": 0-5,
    "examples": 0-5
  },
  "overall": 0-100,
  "should_followup": true/false,
  "followup_question": "string or empty",
  "feedback": ["item1", "item2", ...]
}
```

- **Scores**: Integer 0-5 for each dimension
- **Overall**: Integer 0-100
- **should_followup**: Boolean indicating if follow-up needed
- **followup_question**: Question string if should_followup is true
- **feedback**: Array of feedback strings

## 🔒 Security

- API key read from environment variables only
- Application exits with clear error if API key missing
- No API key in code or version control
- Session files stored locally (no external transmission)
- CORS enabled for frontend-backend communication

## 🐛 Troubleshooting

### API Errors
- **503 Error**: Model is loading, wait a few seconds and retry
- **Timeout**: Check internet connection, increase timeout if needed
- **Invalid JSON**: System falls back to default evaluation

### Missing API Key
- Ensure `.env` file exists with `HUGGINGFACE_API_KEY`
- Application will exit with error message if missing

### Session Files
- Check `data/` directory exists
- Verify write permissions
- Files saved every 5 conversation turns

## 🚧 Future Enhancements

- Voice input/output support
- Database for session persistence across restarts
- Multiple interview rounds
- Industry-specific question sets
- Real-time speech-to-text
- Advanced AI models integration
- User accounts and progress tracking
- Analytics dashboard

## 📝 License

This project is created for educational purposes.

## 👤 Author

Created as part of an AI agent assignment focusing on conversational AI, agentic behavior, and technical implementation.

---

**Note**: This project demonstrates advanced AI functionality including heuristics-based decision making, LLM integration, adaptive difficulty, and comprehensive error handling.
