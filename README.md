# 🎯 Larry - Your Personal Uncertainty Navigator

**An AI-powered chatbot that teaches innovation using Lawrence Aronhime's Problems Worth Solving (PWS) methodology**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg)](https://ai.google.dev/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-green.svg)](https://neo4j.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud%20Ready-FF4B4B.svg)](https://streamlit.io/)

---

## 📖 Overview

Larry is a conversational AI that embodies **Professor Lawrence Aronhime's teaching philosophy**: *Start with problems, not answers.*

**Built on 2,988 knowledge chunks (~2.66M words)** from comprehensive PWS materials, Larry helps you navigate innovation challenges through:
- 🎓 Socratic teaching (questions before answers)
- 📚 Framework-based thinking (systematic problem-solving)
- 💡 Case studies and stories (memorable examples)
- 🚀 Actionable guidance (what to do next)
- 🔗 Relationship-aware context (cross-references frameworks, authors, topics)

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

### 📚 **Comprehensive Knowledge Base v2.0**
- **2,988 Knowledge Chunks** (~2.66 million words)
- **PWS Library** (980 chunks): Prior art, reference books, methodologies
- **Course Material** (2,008 chunks): Lectures, notes, frameworks
- **Problem Types**: Un-defined, Ill-defined, Well-defined, Wicked
- **Top Frameworks** (2,000+ mentions): Design Thinking, Disruptive Innovation, Scenario Analysis, Jobs-to-be-Done, Nested Hierarchies, Blue Ocean Strategy
- **Top Authors** (1,800+ mentions): Clayton Christensen, Peter Drucker, Eric Ries, Steve Blank
- **Relationship Intelligence**: Cross-references between frameworks, topics, and methods

---

## 🌐 Two Ways to Use Larry

### 1️⃣ **Web Interface (Recommended)** 🎨
Beautiful **Mondrian-style** Streamlit app with modern geometric design
- Primary colors (Red #DE1B1B, Blue #0050D5, Yellow #FFD500)
- Clean, minimalist interface
- Real-time chat with message history
- Session statistics tracking

**Deploy to Streamlit Cloud (Free):**
```bash
1. Visit https://share.streamlit.io/
2. Connect repo: jsagir/larry-navigator
3. Set main file: larry_app.py
4. Add API key to secrets:
   GOOGLE_AI_API_KEY = "your-key-here"
5. Deploy! 🚀
```

**Or run locally:**
```bash
streamlit run larry_app.py
# Or use the launcher:
./run_larry.sh
```

See [STREAMLIT_DEPLOYMENT_GUIDE.md](STREAMLIT_DEPLOYMENT_GUIDE.md) for detailed instructions.

### 2️⃣ **Command Line Interface** 💻
Traditional terminal-based chat interface

```bash
python3 larry_chatbot.py
```

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
│           Google Gemini 2.5 Flash + File Search             │
│  ┌──────────────────────────────────────────────────┐       │
│  │    Aronhime System Prompt (teaching methodology) │       │
│  └──────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────┐       │
│  │  File Search Store: 2,988 chunks (~2.66M words) │       │
│  │  • PWS Library: 980 chunks (prior art)          │       │
│  │  • Course Material: 2,008 chunks (lectures)      │       │
│  │  • Relationship metadata (frameworks, authors)   │       │
│  └──────────────────────────────────────────────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│      Response (Hook → Frame → Framework → Story → etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow v2.0
1. **Source Material** (360 files, 298MB) → PWS Library + Course Material
2. **Intelligent Chunking** (`relationship_aware_chunker.py`)
   - ~1000 words per chunk, 200-word overlap
   - Extract frameworks, authors, topics
   - Build relationship metadata
3. **Processing** (`process_all_knowledge.py`) → 2,988 chunks (~2.66M words)
4. **Upload** (`upload_full_knowledge.py`) → Gemini File Search with metadata
5. **User Question** → Persona + Question Type detection
6. **Gemini 2.5 Flash** → RAG with File Search + Aronhime methodology
7. **Response** → Structured teaching (Hook → Frame → Framework → Story → Application → Challenge)

---

## 📂 Project Structure

```
larry-navigator/
├── larry_app.py                          # Streamlit web interface (Mondrian-style) 🎨
├── larry_chatbot.py                      # CLI chatbot interface
├── relationship_aware_chunker.py         # Advanced chunker with metadata
├── intelligent_chunker.py                # Smart ~1000-word chunker
├── process_all_knowledge.py              # Process PWS Library + Course Material
├── upload_full_knowledge.py              # Upload 2,988 chunks to File Search
├── check_upload_status.py                # Monitor upload progress
├── monitor_upload.py                     # Background upload monitor
├── build_larry_navigator.py              # Legacy File Search builder
├── extract_pws_content.py                # Neo4j content extractor (legacy)
├── test_larry.py                         # Sample question tester
├── neo4j_explorer.py                     # Database schema explorer
├── larry_store_info.json                 # File Search store configuration
├── larry_chunks_v2.json                  # 147 course material chunks
├── larry_full_knowledge_chunks.json      # 2,988 comprehensive chunks
├── run_larry.sh                          # Quick Streamlit launcher
├── requirements.txt                      # Python dependencies
├── .streamlit/config.toml                # Streamlit configuration
├── docs/                                 # Additional course materials
│   ├── lectures/                         # Lecture slides and notes
│   ├── frameworks/                       # Framework documentation
│   └── additional/                       # Books and references
├── README.md                             # This file
├── STREAMLIT_DEPLOYMENT_GUIDE.md         # Complete deployment guide
├── LARRY_README.md                       # Detailed user guide
├── .env                                  # API keys (DO NOT COMMIT)
├── .gitignore                            # Git ignore rules
└── pws-navigator-env/                    # Virtual environment (not in repo)
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

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Web interface (Streamlit/Gradio)
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
