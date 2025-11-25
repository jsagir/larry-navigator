# 🚀 Larry Navigator v2.0 - Deployment Guide

## Quick Deployment Checklist

### ✅ Pre-Deployment

- [ ] All dependencies in `requirements_v2.txt`
- [ ] File Search store configured (`larry_store_info.json` exists)
- [ ] Google AI API key ready
- [ ] Tavily API key ready (optional but recommended)
- [ ] Test locally first

### 📦 Files to Deploy

**Core Application:**
```
larry_v2_app.py
larry_store_info.json
requirements_v2.txt
```

**Modules (all must be deployed):**
```
agents/
├── __init__.py
├── definition_classifier.py
├── complexity_assessor.py
├── risk_uncertainty_evaluator.py
├── wickedness_classifier.py
├── diagnosis_consolidator.py
└── research_agent.py

components/
├── __init__.py
├── header.py
├── problem_dashboard.py
├── research_panel.py
└── quick_actions.py

styles/
├── __init__.py
├── theme.py
└── components.py

utils/
├── __init__.py
├── session_state.py
└── tavily_client.py

config/
├── __init__.py
└── prompts.py
```

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Deploy Larry Navigator v2.0"
git push origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Main file path: `larry_v2_app.py`
5. Python version: 3.11

### Step 3: Configure Secrets

In Streamlit Cloud UI → Settings → Secrets:

```toml
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
TAVILY_API_KEY = "tvly-your-key-here"
```

### Step 4: Deploy!

Click "Deploy" - should be live in ~2 minutes.

---

## 🏠 Local Development

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements_v2.txt
```

### 3. Set Environment Variables

**Option A: .env file**
```bash
# Create .env file
cat > .env << EOF
GOOGLE_AI_API_KEY=your-google-ai-api-key
TAVILY_API_KEY=your-tavily-api-key
EOF
```

**Option B: Export**
```bash
export GOOGLE_AI_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
```

**Option C: Streamlit secrets (recommended)**
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
GOOGLE_AI_API_KEY = "your-google-ai-api-key"
TAVILY_API_KEY = "your-tavily-api-key"
EOF
```

### 4. Run Application

```bash
streamlit run larry_v2_app.py
```

App should open at `http://localhost:8501`

---

## 🧪 Testing Checklist

### Basic Functionality

- [ ] App loads without errors
- [ ] Header displays with PWS badges
- [ ] Welcome message shows on first load
- [ ] Chat input accepts messages
- [ ] Larry responds to queries
- [ ] File Search is working (check sidebar status)
- [ ] Tavily search is working (check sidebar status)

### Diagnostic Agents

After sending 1-2 messages:

- [ ] Problem Dashboard appears
- [ ] Definition track updates
- [ ] Complexity (Cynefin) shows classification
- [ ] Risk-Uncertainty slider shows position
- [ ] Wickedness scale shows level
- [ ] Sidebar compact dashboard updates
- [ ] No errors in console

### Research Integration

Send: "What are the latest trends in AI?"

- [ ] Typing indicator shows "Researching the web..."
- [ ] Research panel appears with queries
- [ ] Citation cards display with:
  - [ ] Clickable titles
  - [ ] Content snippets
  - [ ] Relevance scores
  - [ ] URLs

### UI/UX

- [ ] Warm cream background (#FCFCF9)
- [ ] Teal accents (#2A9D8F)
- [ ] PWS badges visible: Real, Winnable, Worth It
- [ ] Chat messages display correctly
- [ ] Dashboard cards have proper styling
- [ ] Responsive on mobile (if applicable)

---

## 🐛 Troubleshooting

### Error: "GOOGLE_AI_API_KEY not found"

**Solution:**
- Check `.streamlit/secrets.toml` exists
- Verify key is quoted correctly: `GOOGLE_AI_API_KEY = "your-key"`
- No spaces in environment variable name
- Restart Streamlit after adding secrets

### Error: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements_v2.txt
```

Check that all subdirectories have `__init__.py`:
```bash
touch agents/__init__.py
touch components/__init__.py
touch styles/__init__.py
touch utils/__init__.py
touch config/__init__.py
```

### Error: "larry_store_info.json not found"

**Solution:**
File Search is not configured. Either:
1. Keep using File Search from v1 (copy `larry_store_info.json` to project root)
2. Or create new File Search store (see v1 migration docs)

App will show warning but still work for basic chat.

### Error: "Tavily API error"

**Solution:**
- Tavily is optional - app works without it
- Check `TAVILY_API_KEY` is correct in secrets
- Research features will be disabled if Tavily not configured

### Dashboard Not Updating

**Solution:**
- Diagnostic agents run after each user turn
- Check browser console for errors
- Refresh page (agents should re-run on next message)
- Verify Gemini API is responding

### Streamlit Cloud: "App is taking too long to load"

**Solution:**
- Check app logs in Streamlit Cloud UI
- Look for import errors or missing dependencies
- Verify `requirements_v2.txt` is complete
- Check file paths are correct (case-sensitive)

---

## ⚡ Performance Optimization

### Reduce Latency

1. **Use Gemini 2.0 Flash** for agents (already configured)
2. **Limit conversation history** to last 10 messages for agents
3. **Cache File Search config** (already implemented)
4. **Run agents in parallel** (future enhancement)

### Current Performance

- **First message**: ~3-5 seconds (Gemini + 6 agents)
- **Subsequent messages**: ~2-3 seconds
- **With Tavily research**: +2-4 seconds

### Scaling Considerations

- Gemini 2.0 Flash: 1500 RPM (requests per minute)
- File Search: 60 RPM
- Tavily: Depends on plan
- 6 agents = 6 API calls per user turn

**Recommendation:** Fine for 10-50 concurrent users. For larger scale, add caching/queueing.

---

## 🔄 Migration from v1.0

### What to Keep

```bash
# Copy these from v1 to v2 directory:
cp larry_store_info.json ../larry-v2/
cp .streamlit/secrets.toml ../larry-v2/.streamlit/
```

### What to Remove

v2.0 doesn't need:
- `larry_neo4j_rag.py` (no Neo4j)
- `larry_tools.py` (no LangChain)
- `larry_router.py` (simplified routing)
- `dark_theme_style.css` (new warm theme)
- Old `requirements.txt` (use `requirements_v2.txt`)

### Side-by-Side Testing

Run both versions:
```bash
# Terminal 1: v1.0
cd larry-navigator
streamlit run larry_app.py --server.port 8501

# Terminal 2: v2.0
cd larry-navigator-v2
streamlit run larry_v2_app.py --server.port 8502
```

Compare:
- v1: http://localhost:8501
- v2: http://localhost:8502

---

## 📊 Monitoring

### Key Metrics to Track

1. **Response Time**: How fast is Larry responding?
2. **Agent Success Rate**: Are all 6 agents completing?
3. **Research Trigger Rate**: How often is Tavily being used?
4. **User Engagement**: Average turns per session

### Streamlit Cloud Monitoring

- Check "Manage app" → Logs
- Look for agent errors
- Monitor Gemini API quota usage
- Track deployment uptime

---

## 🔐 Security Best Practices

### API Keys

- ✅ **DO**: Store in `.streamlit/secrets.toml` (gitignored)
- ✅ **DO**: Use environment variables in production
- ❌ **DON'T**: Hardcode API keys in code
- ❌ **DON'T**: Commit secrets to Git

### File Search Data

- All knowledge base data is in Google's File Search store
- No sensitive data stored in app
- Conversations not persisted (Streamlit session state only)

### User Privacy

- No user data collected
- No analytics by default
- Conversations ephemeral (lost on page refresh)

---

## 📝 Deployment Environments

### Local Development
```bash
streamlit run larry_v2_app.py
```
- Full debugging
- Immediate code changes
- Local File Search store

### Streamlit Cloud (Recommended)
- Free hosting
- Auto-deploys on Git push
- Built-in secrets management
- Custom domain support

### Docker (Advanced)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_v2.txt .
RUN pip install -r requirements_v2.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "larry_v2_app.py"]
```

```bash
docker build -t larry-v2 .
docker run -p 8501:8501 \
  -e GOOGLE_AI_API_KEY="your-key" \
  -e TAVILY_API_KEY="your-key" \
  larry-v2
```

---

## ✅ Pre-Launch Checklist

### Code

- [ ] All imports working
- [ ] No syntax errors
- [ ] All agent prompts configured
- [ ] UI components rendering correctly
- [ ] File Search store configured

### Configuration

- [ ] `requirements_v2.txt` complete
- [ ] API keys in secrets
- [ ] Environment variables set
- [ ] `.gitignore` includes secrets

### Testing

- [ ] Tested locally
- [ ] Tested all 4 diagnostic dimensions
- [ ] Tested research integration
- [ ] Tested error handling
- [ ] Tested mobile responsiveness

### Documentation

- [ ] README_V2.md complete
- [ ] Deployment guide (this file)
- [ ] Code comments adequate
- [ ] User instructions clear

---

## 🎉 Launch!

```bash
# Final commit
git add .
git commit -m "🚀 Launch Larry Navigator v2.0"
git push origin main

# Deploy to Streamlit Cloud
# App will be live at: https://your-app.streamlit.app
```

**Congratulations!** Larry Navigator v2.0 is now live. 🎯

---

## 📞 Support

Issues? Questions?

1. Check this deployment guide
2. Review README_V2.md
3. Check Streamlit Cloud logs
4. Open GitHub issue

**Happy deploying!** 🚀
