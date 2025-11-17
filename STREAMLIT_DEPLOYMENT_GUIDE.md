# 🚀 Deploying Larry to Streamlit Cloud - Complete Guide

## 📋 Prerequisites

✅ GitHub repository: **https://github.com/jsagir/larry-navigator**
✅ Streamlit Cloud account: **https://share.streamlit.io/**
✅ Google AI API key: Get from https://aistudio.google.com/apikey
✅ Exa.ai API key (Optional): Get from https://exa.ai/
✅ All code committed and pushed to GitHub ✓

---

## 🎯 Step-by-Step Deployment

### **Step 1: Verify GitHub Repository**

Make sure these files are in your repo:
- ✅ `larry_app.py` (De Stijl Streamlit app with Exa integration)
- ✅ `larry_system_prompt_v3.py` (v3.0 adaptive system prompt)
- ✅ `larry_web_search.py` (Exa.ai search integration)
- ✅ `requirements.txt` (google-genai, streamlit, exa_py)
- ✅ `larry_store_info.json` (File Search configuration)
- ✅ `.streamlit/config.toml` (Streamlit configuration)

**Verify on GitHub**: https://github.com/jsagir/larry-navigator

---

### **Step 2: Sign In to Streamlit Cloud**

1. Go to **https://share.streamlit.io/**
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit Cloud to access your repositories
4. You'll see your Streamlit Cloud dashboard

---

### **Step 3: Deploy New App**

1. Click **"New app"** button (top right)
2. Fill in the deployment form:

**Repository:**
```
jsagir/larry-navigator
```

**Branch:**
```
main
```

**Main file path:**
```
larry_app.py
```

**App URL (optional):**
```
larry-navigator
```
(This will create: https://larry-navigator.streamlit.app)

---

### **Step 4: Configure Secrets (CRITICAL)**

Before clicking "Deploy", click **"Advanced settings..."**

In the **Secrets** section, paste this configuration:

```toml
# Google AI API Key (REQUIRED)
GOOGLE_AI_API_KEY = "your-google-ai-api-key-here"

# Exa.ai API Key (OPTIONAL - for web search)
EXA_API_KEY = "your-exa-api-key-here"
```

**Where to get API keys:**

**Google AI API Key (Required):**
1. Go to https://aistudio.google.com/apikey
2. Click "Create API key"
3. Copy the key (starts with `AIza...`)
4. Paste into secrets above

**Exa.ai API Key (Optional but Recommended):**
1. Go to https://exa.ai/
2. Sign up for free account
3. Navigate to API settings
4. Copy your API key
5. Paste into secrets above

**Example secrets configuration:**
```toml
GOOGLE_AI_API_KEY = "AIzaSyBWsQSUFztyMf9AGzpX25QWqioVaZsqUeI"
EXA_API_KEY = "exa_1234567890abcdef"
```

---

### **Step 5: Deploy!**

1. After adding secrets, click **"Deploy!"**
2. Streamlit Cloud will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start the app
   - Give you a public URL

**Deployment time:** 2-5 minutes

You'll see a build log showing:
```
[... installing dependencies ...]
✅ google-genai>=1.50.0
✅ streamlit>=1.31.0
✅ exa_py>=1.0.0
[... starting app ...]
```

---

### **Step 6: Access Your App**

Once deployed, your app will be available at:

**Your App URL:**
```
https://larry-navigator-xxxxx.streamlit.app
```

(Replace `xxxxx` with your actual Streamlit app ID)

---

## 🎨 What You'll See

### **Left Panel: Persona & Problem Detection**
- 🎭 **Detected Persona** (Entrepreneur/Corporate/Student/Researcher)
- 📊 **Problem Type Timeline** (Undefined/Ill-Defined/Well-Defined)
- 📈 **Innovation Portfolio Tracker** (NOW/NEW/NEXT)
- 🔑 **API Key Configuration**
- 📚 **Knowledge Base Status** (2,988 chunks)

### **Center Panel: Chat Interface**
Larry's responses with **7 visual message types**:
1. ❓ **Provocative Questions** (Red blocks)
2. 🧭 **Frameworks** (Blue blocks)
3. ⚡ **Actions** (Yellow blocks)
4. 🔍 **Diagnostics** (White with accents)
5. 🔎 **Web Search Results** (Hyperlinked citations)
6. 💡 **Case Stories** (Split layout)
7. 💬 **Regular Responses** (Standard text)

### **Right Panel: Tools & Context**
- 📊 **Session Stats**
- 🔧 **Quick Tools** (3-Box Portfolio, JTBD, MECE, etc.)
- 📚 **Frameworks Library**
- 💡 **Example Questions**

---

## 🧪 Testing Your Deployment

Try these test questions:

**Test 1: Basic Knowledge (File Search)**
```
What is the Three Box Solution?
```
Expected: Larry explains framework from PWS knowledge base

**Test 2: Persona Detection**
```
How do I validate my startup idea?
```
Expected: Persona badge changes to "ENTREPRENEUR"

**Test 3: Web Search (if Exa API key configured)**
```
What are the latest AI trends in 2024?
```
Expected:
- 🔎 Web search results with hyperlinked citations
- Sources from 2022-2025 only
- Synthesis combining web research + PWS frameworks

**Test 4: Problem Type Classification**
```
How do I build an MVP for my app?
```
Expected: Problem type shows "WELL-DEFINED"

---

## 🔧 Troubleshooting

### **Issue: "API key not found"**
**Fix:** Go to App settings → Secrets → Add GOOGLE_AI_API_KEY

### **Issue: "File Search store not found"**
**Fix:** Ensure `larry_store_info.json` is in GitHub repo

### **Issue: "Module not found: exa_py"**
**Fix:** Check `requirements.txt` includes `exa_py>=1.0.0`

### **Issue: "Web search not working"**
**Fix:**
1. Verify EXA_API_KEY is in secrets
2. Check Streamlit logs for Exa errors
3. Web search is optional - app works without it

### **Issue: "App crashes on startup"**
**Fix:**
1. Check Streamlit Cloud logs (bottom of app page)
2. Verify all imports are correct
3. Ensure larry_system_prompt_v3.py is in repo

### **Issue: "Slow response times"**
**Cause:** File Search with 2,988 chunks + Exa search can take 3-10 seconds
**Normal behavior** - Larry is searching extensively!

---

## 📊 Success Metrics

Larry is working correctly when:
- ✅ App loads without errors
- ✅ De Stijl design displays correctly (geometric layout)
- ✅ Persona detection works (badge changes based on question)
- ✅ Problem type classifier shows correct category
- ✅ File Search retrieves relevant PWS content
- ✅ Exa search returns hyperlinked sources (if API key configured)
- ✅ Responses follow Aronhime teaching pattern
- ✅ All 7 message types render properly
- ✅ Chat history persists during session

---

## 🔄 Updating Your App

When you push changes to GitHub:

```bash
git add .
git commit -m "Update Larry"
git push origin main
```

Streamlit Cloud will **automatically redeploy** within 1-2 minutes!

---

## 🎯 Knowledge Base Info

**Current Status:**
- **Total Chunks:** 2,988 (~2.66M words)
- **PWS Library:** 980 chunks (prior art, frameworks, books)
- **Course Material:** 2,008 chunks (lectures, notes, assignments)
- **File Search Store:** `larrypwsnavigatorv2-7pkxk5lhy0xc`

**Top Frameworks:**
1. Design Thinking (1,996 mentions)
2. Disruptive Innovation (1,977 mentions)
3. Scenario Analysis (1,872 mentions)
4. Jobs-to-be-Done (1,862 mentions)
5. Three Box Solution (1,856 mentions)

**Top Authors:**
1. Clayton Christensen (1,758 mentions)
2. Peter Drucker (1,728 mentions)
3. Eric Ries (25 mentions)
4. Steve Blank (18 mentions)

---

## 🎉 You're Live!

**Share your app:**
```
https://larry-navigator.streamlit.app
```

**Who can use it:**
- Johns Hopkins PWS students
- Entrepreneurs validating ideas
- Corporate innovation teams
- Researchers exploring frameworks
- Anyone navigating uncertainty!

---

## 📝 Optional: Custom Domain

Want a custom domain like `larry.yourname.com`?

1. Buy domain from Namecheap/GoDaddy
2. Go to Streamlit App Settings → General
3. Add custom domain
4. Update DNS records as instructed

---

## 🆘 Support

**Streamlit Cloud Issues:**
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community: https://discuss.streamlit.io/

**Larry Issues:**
- GitHub: https://github.com/jsagir/larry-navigator/issues

---

**🤖 Larry v3.0 with Exa.ai Integration - Ready to Navigate Uncertainty!** 🚀
