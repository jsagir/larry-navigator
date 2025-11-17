# 🚀 Deploying Larry to Streamlit Cloud

## Prerequisites
- GitHub repository: https://github.com/jsagir/larry-navigator
- Streamlit Cloud account (free): https://share.streamlit.io/
- Google AI API key: `AIzaSyBWsQSUFztyMf9AGzpX25QWqioVaZsqUeI`

## Step 1: Prepare Repository

Make sure these files are committed to GitHub:
- ✅ `larry_app.py` (Mondrian-style Streamlit app)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (Streamlit configuration)
- ✅ `larry_store_info.json` (File Search store configuration)

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign Up
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Authorize Streamlit Cloud to access your repositories

### 2.2 Create New App
1. Click "New app"
2. Select:
   - **Repository:** `jsagir/larry-navigator`
   - **Branch:** `main`
   - **Main file path:** `larry_app.py`

### 2.3 Configure Secrets
1. Click "Advanced settings"
2. In the "Secrets" section, add:

```toml
GOOGLE_AI_API_KEY = "AIzaSyBWsQSUFztyMf9AGzpX25QWqioVaZsqUeI"
```

3. Click "Deploy!"

## Step 3: Wait for Deployment

Streamlit Cloud will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Launch `larry_app.py`
4. Provide you with a public URL like: `https://larry-navigator-xxxxx.streamlit.app`

**Estimated time:** 2-5 minutes

## Step 4: Test Larry

Once deployed:
1. Visit your app URL
2. Larry should load automatically (API key is in secrets)
3. Test with questions like:
   - "What is the Three Box Solution?"
   - "How do I validate an ill-defined problem?"
   - "Explain the Jobs-to-be-Done framework"

## Step 5: Share Your App

Your app will be publicly accessible at:
```
https://larry-navigator-xxxxx.streamlit.app
```

You can share this URL with:
- Students in PWS courses
- Entrepreneurs seeking innovation guidance
- Colleagues exploring uncertainty

---

## 🎯 Larry's Knowledge Base

After upload completes, Larry will have access to:
- **2,988 knowledge chunks**
- **2.66 million words** of PWS expertise
- **980 chunks** from PWS Library (prior art, frameworks)
- **2,008 chunks** from Course Material (lectures, notes)

### Top Frameworks Larry Knows:
1. Design Thinking (1,996 mentions)
2. Disruptive Innovation (1,977 mentions)
3. Scenario Analysis (1,872 mentions)
4. Jobs-to-be-Done (1,862 mentions)
5. Nested Hierarchies (1,856 mentions)

### Top Authors Larry References:
1. Clayton Christensen (1,758 mentions)
2. Peter Drucker (1,728 mentions)
3. Eric Ries (25 mentions)
4. Steve Blank (18 mentions)

---

## 📝 Updating Larry's Knowledge

To add more content later:

1. Add new files to `docs/` folder
2. Run chunking script:
   ```bash
   python3 process_all_knowledge.py
   ```
3. Upload new chunks:
   ```bash
   python3 upload_full_knowledge.py
   ```
4. Larry will automatically access updated knowledge!

---

## 🎨 Customizing Larry

### Change Colors (Mondrian Style)
Edit `larry_app.py` lines 32-240:
- Primary Red: `#DE1B1B`
- Primary Blue: `#0050D5`
- Primary Yellow: `#FFD500`
- Black: `#000000`
- White: `#FFFFFF`

### Change Teaching Style
Edit system prompt in `larry_app.py` lines 273-318:
- Adjust persona (currently: 10-year-old Socratic guide)
- Modify 6-step pattern (HOOK → FRAME → FRAMEWORK → STORY → APPLICATION → CHALLENGE)

### Add More Frameworks
Edit `relationship_aware_chunker.py` lines 17-23:
```python
FRAMEWORKS = [
    'Three Box Solution', 'Scenario Analysis', 'TRIZ',
    'Your New Framework Here'
]
```

---

## 🔍 Monitoring & Analytics

Streamlit Cloud provides:
- **Viewer count** (how many people use Larry)
- **Error logs** (if something breaks)
- **Resource usage** (memory, CPU)

Access at: https://share.streamlit.io/

---

## 🚨 Troubleshooting

### Issue: "API key not found"
**Fix:** Add API key to Streamlit secrets (Step 2.3)

### Issue: "File Search store not found"
**Fix:** Ensure `larry_store_info.json` is committed to GitHub

### Issue: "Module not found"
**Fix:** Add missing module to `requirements.txt` and redeploy

### Issue: "App crashes on startup"
**Fix:** Check Streamlit Cloud logs for error details

---

## 📊 Success Metrics

Larry is working correctly when:
- ✅ App loads without errors
- ✅ File Search retrieves relevant content
- ✅ Responses follow 6-step Aronhime pattern
- ✅ References specific frameworks and authors
- ✅ Chat history persists during session

---

## 🎉 You're Done!

Larry is now live and helping people navigate uncertainty with Lawrence Aronhime's wisdom!

Share the link and watch Larry teach the world about innovation! 🚀
