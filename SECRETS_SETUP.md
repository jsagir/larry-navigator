# 🔐 Secrets Configuration Guide

This guide shows how to configure Larry Navigator with the required API keys and credentials.

## ✅ No Hardcoded Secrets!

All API keys and credentials are loaded from environment variables or Streamlit secrets. **No secrets are committed to the repository.**

---

## 📋 Required Secrets

### 1. **SUPABASE_URL**
- Your Supabase project URL
- Format: `https://your-project-id.supabase.co`
- Get it from: [Supabase Dashboard → Project Settings → API](https://app.supabase.com/project/_/settings/api)

### 2. **SUPABASE_KEY**
- Your Supabase API key (anon/public or service_role)
- **For production (Streamlit Cloud):** Use anon/public key
- **For local development/migration:** Can use service_role key
- Get it from: [Supabase Dashboard → Project Settings → API](https://app.supabase.com/project/_/settings/api)

### 3. **GOOGLE_AI_API_KEY**
- Google AI Studio API key for Gemini models
- Format: `AIzaSy...`
- Get it from: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. **TAVILY_API_KEY** (Optional)
- For web research functionality
- Format: `tvly-...`
- Get it from: [Tavily](https://tavily.com/)

---

## 🚀 Setup Methods

### Method 1: Streamlit Cloud (Production)

1. Go to your Streamlit Cloud app
2. Click **Settings** → **Secrets**
3. Add these secrets in TOML format:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
GOOGLE_AI_API_KEY = "AIzaSy..."
TAVILY_API_KEY = "tvly-..."  # Optional
```

4. Save and redeploy

---

### Method 2: Local Development

#### Option A: .streamlit/secrets.toml (Recommended)

1. Copy the example file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` with your actual values:
   ```toml
   SUPABASE_URL = "https://ulmymxxmvsehjiyymqoi.supabase.co"
   SUPABASE_KEY = "your-key-here"
   GOOGLE_AI_API_KEY = "AIzaSy..."
   TAVILY_API_KEY = "tvly-..."
   ```

3. **Important:** `.streamlit/secrets.toml` is in `.gitignore` and will NOT be committed

4. Run the app:
   ```bash
   streamlit run larry_app.py
   ```

#### Option B: Environment Variables

Set environment variables before running scripts:

```bash
# Linux/Mac
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_KEY="your-key-here"
export GOOGLE_AI_API_KEY="AIzaSy..."
export TAVILY_API_KEY="tvly-..."

# Windows (PowerShell)
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-key-here"
$env:GOOGLE_AI_API_KEY="AIzaSy..."
$env:TAVILY_API_KEY="tvly-..."
```

---

## 🧪 Testing Configuration

### Test Streamlit App

```bash
streamlit run larry_app.py
```

Check the sidebar - it should show:
- ✅ Knowledge Base: X chunks (Supabase)
- ✅ Web Research: Enabled (if Tavily configured)

### Test Supabase Connection

```bash
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"
export GOOGLE_AI_API_KEY="your-key"

python3 test_supabase_search.py
```

### Run Migration (One-time Setup)

```bash
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-service-role-key"  # Use service_role for migrations
export GOOGLE_AI_API_KEY="your-key"

python3 setup_supabase_kb.py
```

---

## 🔍 How Code Loads Secrets

All Python files use this pattern:

```python
# 1. Try environment variable first
# 2. Fall back to Streamlit secrets (if available)
# 3. No hardcoded fallbacks!

import os
import streamlit as st

# For Streamlit apps
api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")

# For standalone scripts
api_key = os.getenv("GOOGLE_AI_API_KEY")
```

---

## 🔒 Security Best Practices

✅ **DO:**
- Use `.streamlit/secrets.toml` for local development
- Add secrets in Streamlit Cloud dashboard for production
- Use environment variables for CI/CD and scripts
- Use `anon/public` key for production apps
- Use `service_role` key only for migrations/admin tasks

❌ **DON'T:**
- Hardcode API keys in source files
- Commit `.streamlit/secrets.toml` to Git (it's in `.gitignore`)
- Share service_role keys publicly
- Use service_role keys in client-side code

---

## 📁 Files That Need Secrets

| File | Secrets Used | Purpose |
|------|-------------|---------|
| `larry_app.py` | All 3 required | Main Streamlit app |
| `larry_supabase_rag.py` | SUPABASE_URL, SUPABASE_KEY, GOOGLE_AI_API_KEY | RAG module |
| `setup_supabase_kb.py` | SUPABASE_URL, SUPABASE_SERVICE_KEY, GOOGLE_AI_API_KEY | One-time migration |
| `test_supabase_search.py` | All 3 required | Test script |
| `agents/*.py` | GOOGLE_AI_API_KEY | Diagnostic agents |

---

## ❓ Troubleshooting

### "❌ GOOGLE_AI_API_KEY not found"
- Check if secret is added to Streamlit Cloud or `.streamlit/secrets.toml`
- Verify environment variable is set: `echo $GOOGLE_AI_API_KEY`

### "⚠️ Knowledge Base: Not configured"
- Add `SUPABASE_URL` and `SUPABASE_KEY` to secrets
- Check URL format: `https://project-id.supabase.co` (no trailing slash)

### "⚠️ Knowledge Base: 0 chunks"
- Run the migration script: `python3 setup_supabase_kb.py`
- Check Supabase dashboard for data in `knowledge_base` table

### "API key expired"
- Generate a new Google AI API key
- Update in secrets.toml or Streamlit Cloud
- Restart app

---

## 📚 Additional Resources

- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Supabase API Keys](https://supabase.com/docs/guides/api/api-keys)
- [Google AI Studio](https://aistudio.google.com/)
- [Tavily API](https://docs.tavily.com/)
