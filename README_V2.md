# 🎯 Larry Navigator v2.0

**Your PWS Innovation Mentor with 4-Dimensional Problem Diagnosis**

Larry Navigator v2.0 is a complete redesign that transforms problem exploration into a **diagnostic, educational experience** using the PWS (Real • Winnable • Worth It) methodology.

---

## 🌟 What's New in v2.0

### Complete Redesign
- **Warm Educational UI**: Cream & teal color palette designed for learning
- **4-Dimensional Problem Diagnosis**: Real-time classification across 4 frameworks
- **6 Background Diagnostic Agents**: Continuous analysis running behind the scenes
- **Integrated Web Research**: Tavily search with beautiful citation cards
- **Simplified Architecture**: 100% Gemini-powered (no Claude, no LangChain)

### From v1.0 to v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **UI Theme** | Dark minimalist | Warm educational |
| **Problem Classification** | Basic (3 types) | 4-Dimensional diagnosis |
| **AI Models** | Gemini + Claude | Gemini only |
| **Background Agents** | None | 6 diagnostic agents |
| **Dependencies** | 8 packages | 4 core packages |
| **Visual Teaching** | Minimal | PWS badges, progress tracks |
| **Research Integration** | Text-only | Beautiful citation cards |

---

## 🧠 4-Dimensional Problem Diagnosis

Larry analyzes every conversation across **4 diagnostic dimensions**:

### 1️⃣ Definition Track
**undefined → ill-defined → well-defined**

- **Undefined**: Exploratory, many unknowns
- **Ill-defined**: Some clarity, boundaries unclear
- **Well-defined**: Clear problem statement, known constraints

### 2️⃣ Complexity (Cynefin Framework)
**simple → complicated → complex → chaotic**

- **Simple**: Clear cause-effect, best practices exist
- **Complicated**: Analyzable, requires expertise
- **Complex**: Emergent patterns, requires experimentation
- **Chaotic**: No patterns, immediate action needed

### 3️⃣ Risk-Uncertainty Position
**0.0 (Risk/Known Unknowns) → 1.0 (Uncertainty/Unknown Unknowns)**

- **Risk**: Quantifiable, historical data available
- **Moderate**: Mix of known and unknown unknowns
- **Uncertainty**: Novel situation, can't estimate probabilities

### 4️⃣ Wickedness Scale
**tame → messy → complex → wicked**

- **Tame**: Well-bounded, clear stopping rule
- **Messy**: Multiple stakeholders, some interconnections
- **Complex**: High interconnectedness, no clear solutions
- **Wicked**: No definitive formulation, one-shot solutions

---

## 🤖 Six Diagnostic Agents

Running continuously in the background:

1. **Definition Classifier**: Classifies problem definition state
2. **Complexity Assessor**: Maps to Cynefin framework
3. **Risk-Uncertainty Evaluator**: Positions on knowability spectrum
4. **Wickedness Classifier**: Assesses problem wickedness
5. **Diagnosis Consolidator**: Synthesizes all outputs into coherent insight
6. **Research Agent**: Triggers Tavily searches when needed

All agents use **Gemini 2.0 Flash** for fast, structured JSON outputs.

---

## 🎨 Visual Design Philosophy

### Warm Educational Theme

**Color Palette:**
- **Cream Background** (#FCFCF9): Warm, inviting learning space
- **Teal Primary** (#2A9D8F): Trust, clarity, guidance
- **Orange Accents** (#E76F51): Energy, challenge, curiosity

### PWS Triad (Always Visible)

```
🔥 Real     🎯 Winnable     💎 Worth It
```

Constant visual reinforcement of the three validation criteria.

### Problem Dashboard

4x4 grid displaying all diagnostic dimensions with:
- **Progress indicators**: Dots showing movement along tracks
- **Color coding**: Each dimension has semantic colors
- **Confidence scores**: How certain the diagnosis is
- **Live updates**: Dashboard refreshes after each turn

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_v2.txt
```

### 2. Configure API Keys

Create `.streamlit/secrets.toml`:

```toml
GOOGLE_AI_API_KEY = "your-google-ai-api-key"
TAVILY_API_KEY = "your-tavily-api-key"  # Optional
```

### 3. Run the App

```bash
streamlit run larry_v2_app.py
```

### 4. Start Exploring

Larry will greet you with:
- PWS framework introduction
- Example starting points
- Quick action buttons

---

## 📁 Project Structure

```
larry-navigator/
├── larry_v2_app.py              # Main Streamlit app
│
├── agents/                      # Diagnostic agents
│   ├── definition_classifier.py
│   ├── complexity_assessor.py
│   ├── risk_uncertainty_evaluator.py
│   ├── wickedness_classifier.py
│   ├── diagnosis_consolidator.py
│   └── research_agent.py
│
├── components/                  # UI components
│   ├── header.py               # Larry header with PWS badges
│   ├── problem_dashboard.py    # 4D diagnostic dashboard
│   ├── research_panel.py       # Tavily search results
│   └── quick_actions.py        # Action buttons & prompts
│
├── styles/                      # CSS and theming
│   ├── theme.py                # Warm color system
│   └── components.py           # Component-specific styles
│
├── utils/                       # Utilities
│   ├── session_state.py        # State management
│   └── tavily_client.py        # Tavily wrapper
│
├── config/                      # Configuration
│   └── prompts.py              # All agent system prompts
│
├── requirements_v2.txt          # Dependencies
└── README_V2.md                # This file
```

---

## 🎯 PWS Methodology

Every problem is evaluated through **three lenses**:

### 🔥 Real
- Is there evidence this problem exists?
- Do people actually experience this pain?
- How widespread is it?

### 🎯 Winnable
- Can this problem be solved?
- Do we have (or can we build) the capabilities?
- What similar problems have been solved?

### 💎 Worth It
- Is the value worth the effort?
- How many people/organizations benefit?
- What's the opportunity cost of NOT solving this?

**Larry's Promise**: Only spend time on problems that pass all three tests.

---

## 🔬 How Diagnostic Agents Work

### Trigger: After Every User Turn

After you send a message, Larry:

1. **Responds** with conversational guidance (using Gemini 3 + File Search)
2. **Analyzes** the conversation with 6 background agents
3. **Updates** the problem dashboard with new diagnosis
4. **Consolidates** insights across all dimensions

### Example Agent Flow

```
User: "My team is struggling with product roadmap prioritization."

Definition Classifier →
  Classification: "ill-defined"
  Confidence: 0.75
  Signals: ["mentions symptoms", "unclear root cause"]

Complexity Assessor →
  Complexity: "complex"
  Confidence: 0.80
  Characteristics: ["emergent behavior", "multiple stakeholders"]

Risk-Uncertainty Evaluator →
  Position: 0.62
  Known unknowns: ["stakeholder priorities"]
  Unknown unknowns: ["market shifts"]

Wickedness Classifier →
  Wickedness: "messy"
  Score: 0.52
  Characteristics: ["multiple stakeholders", "no clear solution"]

Diagnosis Consolidator →
  Summary: "This is an ill-defined, complex problem with moderate uncertainty..."
  Recommended Approach: "Focus on stakeholder alignment first"
```

Dashboard updates in real-time to reflect this diagnosis.

---

## 🔍 Web Research Integration

### When Research Triggers

The **Research Agent** analyzes each message and decides if web search would help:

**Triggers:**
- "What's the latest..."
- "Current trends in..."
- "How are others solving..."
- "Best practices for..."

**Doesn't Trigger:**
- General problem exploration (uses File Search instead)
- Company-specific questions
- Personal situations

### Research Flow

1. **Research Agent** generates 1-3 focused queries
2. **Tavily** executes searches in parallel
3. **Results** displayed as beautiful citation cards with:
   - Title (clickable)
   - Content snippet
   - Relevance score
   - URL
4. **Synthesis** (optional) combines findings

---

## 💡 Usage Examples

### Example 1: Exploring New Idea

**You:** "I'm thinking about building a tool for..."

**Larry's Dashboard Updates:**
- Definition: **undefined** (exploratory phase)
- Complexity: **complex** (new territory)
- Risk-Uncertainty: **0.75** (high uncertainty)
- Wickedness: **messy** (stakeholders unclear)

**Larry's Response:**
- Asks probing questions
- Challenges assumptions
- Suggests frameworks (Jobs to be Done, etc.)

### Example 2: Clarifying Existing Problem

**You:** "Our users complain about X but we're not sure if it's worth fixing."

**Larry's Dashboard Updates:**
- Definition: **ill-defined** (symptoms known, root cause unclear)
- Complexity: **complicated** (analyzable)
- Risk-Uncertainty: **0.40** (some data available)
- Wickedness: **messy** (multiple perspectives)

**Larry's Response:**
- PWS check: Is it Real, Winnable, Worth It?
- Suggests data to gather
- Introduces validation frameworks

### Example 3: Well-Defined Problem

**You:** "We need to reduce API response time from 200ms to 50ms."

**Larry's Dashboard Updates:**
- Definition: **well-defined** (clear success criteria)
- Complexity: **complicated** (requires technical expertise)
- Risk-Uncertainty: **0.25** (known unknowns)
- Wickedness: **tame** (bounded problem)

**Larry's Response:**
- Solution-focused guidance
- Technical frameworks
- Implementation approaches

---

## 🎓 Learning Resources

Larry has access to **1,424 knowledge chunks** covering:

- **Jobs to be Done** framework
- **Kano Model** for feature prioritization
- **Innovation frameworks** (Blue Ocean, etc.)
- **Problem-solving methodologies**
- **Product management best practices**
- **Wickedness** theory (Rittel & Webber)
- **Cynefin** framework
- **Risk vs. Uncertainty** (Knight's distinction)

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GOOGLE_AI_API_KEY=your-google-ai-api-key

# Optional (enables web research)
TAVILY_API_KEY=your-tavily-api-key
```

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in UI (Settings → Secrets)
4. Deploy!

No additional configuration needed.

---

## 🔧 Development

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements_v2.txt

# Set environment variables
export GOOGLE_AI_API_KEY="your-key"
export TAVILY_API_KEY="your-key"  # optional

# Run app
streamlit run larry_v2_app.py
```

### Adding New Agents

1. Create agent file in `agents/`
2. Add system prompt to `config/prompts.py`
3. Integrate into `run_diagnostic_agents_background()` in `larry_v2_app.py`
4. Update dashboard rendering if needed

### Customizing UI

All CSS is in:
- `styles/theme.py`: Color system, base styles
- `styles/components.py`: Component-specific styles

Change colors in `:root` CSS variables.

---

## 📊 Architecture Decisions

### Why Gemini Only?

**v1.0 Issues:**
- Multiple LLMs (Gemini + Claude) created complexity
- Different personalities confusing
- LangChain overhead
- Dependency hell

**v2.0 Solution:**
- Single AI provider (Google Gemini)
- Unified personality
- Native File Search integration
- Simpler deployment

### Why 6 Separate Agents?

**Modularity:**
- Each agent has one clear responsibility
- Can test/improve agents independently
- Easy to add new diagnostic dimensions

**Transparency:**
- User sees which dimensions are updating
- Clear reasoning for each classification
- Consolidated synthesis maintains coherence

### Why Warm Theme (Not Dark)?

**Educational Context:**
- Dark theme = focus, productivity
- Warm theme = learning, exploration, safety
- Research shows warm colors increase openness to new ideas
- Cream background reduces eye strain for reading-heavy tasks

---

## 🚧 Future Enhancements

### Planned Features

- [ ] **Agent Activity Indicator**: Show which agents are running
- [ ] **Diagnosis History**: Track how diagnosis evolves over conversation
- [ ] **Export Diagnosis**: Download assessment as PDF
- [ ] **Framework Library**: Browse all available frameworks
- [ ] **Saved Sessions**: Resume previous problem explorations
- [ ] **Multi-language Support**: Internationalization

### Experimental Features

- [ ] **Voice Input**: Speak your problem
- [ ] **Collaborative Mode**: Multiple users exploring same problem
- [ ] **Integration with Notion/Obsidian**: Export insights
- [ ] **Custom Agent Training**: Fine-tune agents for specific domains

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

Built with:
- **Streamlit**: Web app framework
- **Google Gemini**: AI reasoning & File Search
- **Tavily AI**: Web research
- **PWS Methodology**: Aronhime's course materials
- **Cynefin Framework**: Dave Snowden
- **Wickedness Theory**: Rittel & Webber

---

## 📮 Contact & Support

Questions? Issues? Ideas?

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/issues)
- **Documentation**: This README + inline code comments
- **Community**: [Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ for problem solvers, innovators, and critical thinkers.**

🎯 **Larry Navigator v2.0** - *Because every great solution starts with understanding the problem.*
