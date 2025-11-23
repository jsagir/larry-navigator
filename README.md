# 🎯 Larry Navigator

**Your AI Thinking Partner for Complex Decisions**

Larry Navigator is a hyper-modern AI-powered decision support system powered by Google's latest **Gemini 3 Pro Preview** model. Built on Lawrence Aronhime's Problems Worth Solving (PWS) methodology, Larry helps you navigate uncertainty, challenge assumptions, and make breakthrough decisions.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Gemini 3](https://img.shields.io/badge/Gemini-3%20Pro%20Preview-orange.svg)](https://ai.google.dev/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-green.svg)](https://neo4j.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud%20Ready-FF4B4B.svg)](https://streamlit.io/)

**Live Demo:** https://larrynav.streamlit.app/

---

## ✨ Features

### 🤖 **Gemini 3 Pro Preview Integration**
- Powered by Google's latest **Gemini 3 Pro Preview** model (released November 18, 2025)
- Real-time streaming responses with dynamic thinking
- State-of-the-art reasoning and problem-solving capabilities
- 50% improvement over Gemini 2.5 Pro in coding and reasoning

### 🧠 **Intelligent Query Routing**
Larry automatically routes your questions to the best knowledge source:
- **File Search** (Default) - Fast Gemini responses with document context
- **Neo4j Knowledge Graph** - MCP-style Text-to-Cypher for connections and insights
- **Web Search** - Real-time information via Exa.ai neural search for current events

### 🎨 **Modern Professional Interface**
- Clean, minimal design with soft blue/orange color palette
- Dashboard metrics (Uncertainty, Risk, Conversations)
- Quick Start suggestions for easy onboarding
- Clarity indicator showing decision progress
- Mobile-responsive design
- Real-time streaming response display

### 🛡️ **Production-Ready Security**
- Input sanitization and validation
- Rate limiting (10 messages per 60 seconds)
- Prompt injection detection
- Session isolation for multi-user support
- Graceful error handling

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- Google AI API Key ([Get one here](https://ai.google.dev/gemini-api/docs/api-key))
- Optional: Exa.ai API key, Neo4j credentials

### **Installation**

```bash
# Clone the repository
git clone https://github.com/jsagir/larry-navigator.git
cd larry-navigator

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file or use Streamlit Cloud secrets
GOOGLE_AI_API_KEY=your_google_ai_key
EXA_API_KEY=your_exa_key  # Optional
NEO4J_URI=bolt://localhost:7687  # Optional
NEO4J_USER=neo4j  # Optional
NEO4J_PASSWORD=your_password  # Optional
```

### **Run Locally**
```bash
streamlit run larry_app.py
```

### **Deploy to Streamlit Cloud**
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure secrets in app settings
4. Deploy! 🚀

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed deployment guide.

---

## 🏗️ Architecture

### **Core Components**

**Chat System (`larry_chat.py`)**
- Streaming chat handler with Gemini 3 Pro Preview
- Conversation history management (last 10 messages)
- Automatic tool selection based on query intent

**Intelligent Router (`larry_router.py`)**
- Natural language query classification
- Keyword-based routing logic:
  - Neo4j: "knowledge graph", "what do I know about", "connections"
  - Web Search: "latest", "current", "news", "stock price"
  - File Search: Everything else (default)

**Neo4j Integration (`larry_neo4j_tool.py`)**
- MCP-style Text-to-Cypher conversion
- Automatic schema retrieval
- Natural language knowledge graph queries
- Works like Claude Desktop's MCP integration

**Security Layer (`larry_security.py`)**
- Input sanitization (max 10,000 chars)
- Rate limiting (10 msgs/60s)
- Prompt injection detection

**Web Search (`larry_tools.py`)**
- Exa.ai neural search integration
- Current events and real-time information

---

## 📊 Performance

- **First Token:** <2 seconds (streaming)
- **Full Response:** 3-10 seconds depending on complexity
- **Concurrent Users:** Scales with Streamlit Cloud plan
- **Rate Limit:** 10 messages per minute per user

---

## 🎨 UI Features

### **Dashboard Metrics**
- **Uncertainty Score** - Current decision uncertainty level (0-100%)
- **Risk Score** - Assessed risk level (0-100%)
- **Conversation Count** - Number of exchanges

### **Quick Start Prompts**
- "I'm facing a tough decision about..."
- "Help me think through..."
- "What am I not considering about..."
- "Challenge my assumptions on..."

### **Clarity Indicator**
Visual progress bar showing decision clarity:
- Starts at 20%
- Increases 5% per message
- "Ready to decide" at 70%+

---

## 📂 Project Structure

```
larry-navigator/
├── larry_app.py                    # Main Streamlit application
├── larry_chat.py                   # Streaming chat handler (Gemini 3)
├── larry_router.py                 # Intelligent query routing
├── larry_neo4j_tool.py            # Neo4j MCP-style integration
├── larry_tools.py                  # Web search and utility tools
├── larry_security.py               # Security measures
├── larry_config.py                 # Centralized configuration
├── larry_system_prompt_v3.py      # System prompt (PWS methodology)
├── modern_larry_style.css         # Modern UI styling
├── requirements.txt                # Python dependencies
├── larry_store_info.json          # File search store config
├── DEPLOYMENT_CHECKLIST.md        # Deployment verification
├── README.md                       # This file
└── .streamlit/config.toml         # Streamlit configuration
```

---

## 🔧 Configuration

All configuration is centralized in `larry_config.py`:

```python
# Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # For Neo4j Cypher
CLAUDE_MAX_TOKENS = 8192
CLAUDE_TEMPERATURE_DEFAULT = 0.2
CLAUDE_TEMPERATURE_PRECISE = 0.0

# UI Configuration
CLARITY_BASE_SCORE = 20
CLARITY_INCREMENT_PER_MESSAGE = 5
CLARITY_READY_THRESHOLD = 70

# Memory Configuration
CONVERSATION_MEMORY_WINDOW = 5
```

---

## 🧪 Testing

### **Import Validation**
```bash
python3 -c "import larry_router, larry_chat, larry_neo4j_tool, larry_security; print('✅ All imports successful')"
```

### **Syntax Check**
```bash
python3 -m py_compile larry_app.py larry_chat.py larry_router.py
```

---

## 💬 Example Queries

### **File Search (Default)**
```
You: How do I validate my startup idea?
Larry: [Streams response using Gemini 3 with document context]
```

### **Neo4j Knowledge Graph**
```
You: What's in my knowledge graph?
Larry: [Generates Cypher query, executes, returns results]
```

### **Web Search**
```
You: What's the latest news about AI?
Larry: [Searches web via Exa.ai, returns current information]
```

---

## 🛠️ Development

### **Adding New Features**
1. Update relevant module (e.g., `larry_tools.py`)
2. Test imports: `python3 -c "import larry_tools"`
3. Commit and push to GitHub
4. Streamlit Cloud auto-deploys

### **Customizing Routing**
Edit `larry_router.py` to adjust keyword triggers:
```python
neo4j_keywords = ["knowledge graph", "what do I know about", ...]
web_keywords = ["latest", "current", "news", ...]
```

### **Updating System Prompt**
Edit `larry_system_prompt_v3.py` to adjust Larry's personality and teaching style.

---

## 📝 License

**Copyright © 2025 Jonathan Sagir. All Rights Reserved.**

This software and associated documentation files (the "Software") are the proprietary and confidential property of Jonathan Sagir.

### **STRICT PROPRIETARY LICENSE**

**NO PERMISSION IS GRANTED** to any person to use, copy, modify, merge, publish, distribute, sublicense, or sell copies of the Software, or to permit persons to whom the Software is furnished to do so.

**Restrictions:**
- ❌ **No use** without explicit written permission from the copyright holder
- ❌ **No copying** or redistribution in any form
- ❌ **No modification** or creation of derivative works
- ❌ **No commercial use** or monetization
- ❌ **No reverse engineering**, decompilation, or disassembly
- ❌ **No public deployment** or hosting
- ❌ **No sublicensing** or transfer of rights

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.**

**IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

**For licensing inquiries, contact:** Jsagir@gmail.com

---

## 👨‍💻 Developer

**Jonathan Sagir**
- **Email:** Jsagir@gmail.com
- **GitHub:** [@jsagir](https://github.com/jsagir)
- **Repository:** https://github.com/jsagir/larry-navigator

---

## 🙏 Acknowledgments

**Built with:**
- **Google Gemini 3 Pro Preview** - State-of-the-art AI reasoning (November 2025)
- **Streamlit** - Modern web application framework
- **Anthropic Claude** - Neo4j Cypher query generation
- **Exa.ai** - Neural web search
- **Neo4j** - Knowledge graph database

**Inspired by:**
- **Lawrence Aronhime's PWS (Problems Worth Solving) methodology** for breakthrough innovation and systematic problem-solving

---

## 📞 Support

For questions, issues, or licensing inquiries:
- **Email:** Jsagir@gmail.com
- **GitHub Issues:** For authorized users only

---

## 🎯 Philosophy

> *"The best teachers don't give you the answers. They give you better questions."*
>
> — Larry, embodying Lawrence Aronhime's teaching methodology

Larry transforms passive learners into active thinkers through systematic frameworks, intelligent routing, and the latest AI technology. Navigate uncertainty with confidence! 🚀

---

**Last Updated:** November 23, 2025  
**Version:** Gemini 3 Pro Preview with Fast Streaming  
**Status:** Production Ready ✅
