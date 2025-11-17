# 🎯 Larry - Your Personal Uncertainty Navigator

**An AI-powered chatbot that teaches innovation using Lawrence Aronhime's Problems Worth Solving (PWS) methodology**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-green.svg)](https://neo4j.com/)

---

## 📖 Overview

Larry is a conversational AI that embodies **Professor Lawrence Aronhime's teaching philosophy**: *Start with problems, not answers.*

Built on 1,136 knowledge chunks from PWS course materials, Larry helps you navigate innovation challenges through:
- 🎓 Socratic teaching (questions before answers)
- 📚 Framework-based thinking (systematic problem-solving)
- 💡 Case studies and stories (memorable examples)
- 🚀 Actionable guidance (what to do next)

---

## ✨ Features

### 🧠 **Intelligent Persona Detection**
Larry automatically adapts responses for:
- 👨‍🎓 **Students** - Course navigation, exam prep, concept clarity
- 🚀 **Entrepreneurs** - Idea validation, opportunity identification
- 🏢 **Corporate Teams** - Systematic innovation, portfolio management
- 💼 **Consultants** - Frameworks, facilitation, advisory
- 🔬 **Researchers** - Theory, literature, foundations

### 🎓 **Aronhime Teaching Method**
Every response follows the proven structure:
1. **HOOK** - Provocative question to challenge thinking
2. **FRAME** - Why this matters and what you'll learn
3. **FRAMEWORK** - Systematic thinking tools
4. **STORY** - Memorable case studies (successes + failures)
5. **APPLICATION** - Actionable next steps
6. **CHALLENGE** - Follow-up question to deepen understanding

### 📚 **Comprehensive Knowledge Base**
- **10 Core PWS Lectures** (N01-N10)
- **Problem Types**: Un-defined, Ill-defined, Well-defined, Wicked
- **Innovation Frameworks**: Three Box Solution, Scenario Analysis, TRIZ, Jobs-to-be-Done, and more
- **Tools**: Trending to Absurd, Beautiful Questions, Red Teaming, Mom Test
- **1,136 Knowledge Chunks** from Neo4j graph database

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Google AI API Key ([Get one here](https://ai.google.dev/gemini-api/docs/api-key))
- Neo4j database with PWS content (optional - for rebuilding)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/larry-navigator.git
cd larry-navigator

# Create virtual environment
python3 -m venv pws-navigator-env
source pws-navigator-env/bin/activate  # On Windows: pws-navigator-env\Scripts\activate

# Install dependencies
pip install google-genai neo4j

# Configure API key
# Edit larry_chatbot.py and replace YOUR_API_KEY with your Google AI API key
```

### Usage

```bash
# Interactive chat
python3 larry_chatbot.py

# Test with sample questions
python3 test_larry.py

# Quick launcher (Linux/Mac)
./larry
```

---

## 💬 Example Conversations

### For Students:
```
You: What is Creative Destruction?

Larry:
HOOK: Have you ever wondered why Blockbuster—with thousands of stores
and millions of customers—went bankrupt while a startup called Netflix thrived?

FRAME: That's Creative Destruction, and it explains why dominant companies
often fail when innovation strikes...

[Larry continues with Framework, Story, Application, Challenge]
```

### For Entrepreneurs:
```
You: How do I validate my startup idea?

Larry:
HOOK: Here's what most entrepreneurs get wrong: they ask "Do you like my idea?"
instead of "What's your current problem?"

FRAME: Validation isn't about collecting compliments—it's about discovering
if your problem is worth solving...

[Larry provides Mom Test framework, examples, and next steps]
```

### For Corporate Teams:
```
You: What is the Three Box Solution?

Larry:
HOOK: Let me challenge your thinking: Why do successful companies fail
to innovate, despite having resources and talent?

FRAME: The Three Box Solution addresses exactly this—how to manage today's
business while creating tomorrow's opportunities...

[Larry explains framework with GE case study]
```

---

## 🎨 Question Types Larry Handles

1. **Definitional** - "What is X?" → Definition + context + curriculum location
2. **How-To** - "How do I X?" → Step-by-step + tools + examples
3. **Diagnostic** - "What type is this?" → Classification framework
4. **Comparison** - "X vs Y?" → Side-by-side analysis
5. **Application** - "How do I apply X?" → Industry-specific guidance
6. **Strategic** - "What's the best approach?" → Recommendations
7. **Navigation** - "Where can I learn X?" → Learning paths
8. **Examples/Cases** - "Show me an example" → Case studies

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Question                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Larry Navigator (larry_chatbot.py)             │
│  ┌──────────────────┐  ┌─────────────────────────────┐     │
│  │ Persona Detector │→│ Question Classifier (8 types)│     │
│  └──────────────────┘  └─────────────────────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Google Gemini 2.0 Flash + File Search             │
│  ┌──────────────────────────────────────────────────┐       │
│  │    Aronhime System Prompt (teaching methodology) │       │
│  └──────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────┐       │
│  │  File Search Store: 10 PWS Lectures (N01-N10)   │       │
│  └──────────────────────────────────────────────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│      Response (Hook → Frame → Framework → Story → etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Neo4j** → Extract 1,136 PWS chunks (`extract_pws_content.py`)
2. **Chunks** → Upload to Gemini File Search (`build_larry_navigator.py`)
3. **User Question** → Persona + Question Type detection
4. **Gemini** → Generate Aronhime-style response with retrieved context
5. **Response** → Structured teaching with frameworks and stories

---

## 📂 Project Structure

```
larry-navigator/
├── larry_chatbot.py              # Main chatbot interface
├── build_larry_navigator.py      # File Search store builder
├── extract_pws_content.py        # Neo4j content extractor
├── test_larry.py                 # Sample question tester
├── neo4j_explorer.py             # Database schema explorer
├── neo4j_document_query.py       # Document structure analyzer
├── larry                         # Quick launcher script
├── README.md                     # This file
├── LARRY_README.md               # Detailed user guide
├── .gitignore                    # Git ignore rules
└── pws-navigator-env/            # Virtual environment (not in repo)
```

---

## 🛠️ Configuration

### API Keys
Edit `larry_chatbot.py` and `build_larry_navigator.py`:
```python
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
```

### Neo4j Connection
Edit extraction scripts with your Neo4j credentials:
```python
URI = "neo4j+s://your-instance.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "your-password"
```

---

## 🧪 Testing

```bash
# Run sample questions
python3 test_larry.py

# Ask specific question
python3 -c "from larry_chatbot import LarryNavigator; \
larry = LarryNavigator('YOUR_API_KEY', 'larry_store_info.json'); \
print(larry.chat('What is the Innovator''s Dilemma?'))"
```

---

## 📝 Development

### Rebuilding File Search Store
```bash
# 1. Extract from Neo4j
python3 extract_pws_content.py

# 2. Upload to Gemini
python3 build_larry_navigator.py
```

### Adding New Content
1. Add content to Neo4j as `DocumentChunk` nodes
2. Run `extract_pws_content.py`
3. Run `build_larry_navigator.py`

### Customizing Teaching Style
Edit `LARRY_SYSTEM_PROMPT` in `larry_chatbot.py` to adjust:
- Response structure
- Language patterns
- Emphasis techniques
- Persona adaptations

---

## 🌐 Web Interface & Deployment

Larry now includes a Streamlit web interface for easy browser-based interaction!

### Local Web Access

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web interface
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

### Deployment Options

#### Option 1: Streamlit Cloud (Easiest - Free)

1. Push your repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository and branch
5. Set main file path to `app.py`
6. Add your `GOOGLE_AI_API_KEY` in Secrets (Settings > Secrets)
7. Click "Deploy"

**Secrets format for Streamlit Cloud:**
```toml
GOOGLE_AI_API_KEY = "your-api-key-here"
```

#### Option 2: Docker Container

```bash
# Build the Docker image
docker build -t larry-navigator .

# Run the container
docker run -p 8501:8501 \
  -e GOOGLE_AI_API_KEY="your-api-key" \
  larry-navigator
```

Access at `http://localhost:8501`

#### Option 3: Cloud Platforms

**Google Cloud Run:**
```bash
gcloud run deploy larry-navigator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_AI_API_KEY="your-api-key"
```

**Render / Railway / Heroku:**
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `streamlit run app.py --server.port=$PORT`
- Add `GOOGLE_AI_API_KEY` environment variable

### Environment Variables

For production deployment, set:
- `GOOGLE_AI_API_KEY` - Your Google AI API key

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [x] Web interface (Streamlit/Gradio)
- [ ] Voice mode (speech-to-text/text-to-speech)
- [ ] Session memory (conversation context)
- [ ] Framework visualizations (diagrams)
- [ ] Multi-modal support (images/videos)
- [ ] Additional PWS content
- [ ] More persona types
- [ ] Enhanced question classification

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Credits

- **Lawrence Aronhime** - Creator of Problems Worth Solving (PWS) methodology
- **Google Gemini** - AI model and File Search capability
- **Neo4j** - Graph database for knowledge storage
- **Built with** - Python, google-genai SDK

---

## 📧 Contact

Questions? Issues? Feedback?
- Open an issue on GitHub
- Email: [your-email@example.com]

---

## 🎯 Philosophy

> *"The best teachers don't give you the answers. They give you better questions."*
>
> — Larry, embodying Lawrence Aronhime's teaching methodology

Larry transforms passive learners into active thinkers through systematic frameworks, memorable stories, and productive discomfort. Navigate uncertainty with confidence! 🚀

---

**Ready to start?** Run `python3 larry_chatbot.py` and ask your first question!
