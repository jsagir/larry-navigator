# 🔧 Fixing the PWS Knowledge Base

## ❌ Current Problem

The PWS Knowledge Base with 1,136 chunks is **DISABLED** because:

1. **Missing File**: `pws_chunks.json` doesn't exist in the repository
2. **Placeholder Store**: `larry_store_info.json` is just a placeholder
3. **Code Disabled**: File Search was intentionally disabled in `larry_chatbot.py` lines 182-183

```python
# Build conversation (File Search temporarily disabled due to SDK issues)
# TODO: Re-enable File Search once API format is confirmed
```

## 🎯 Why This Matters

Without the knowledge base, Larry only uses:
- ✅ Gemini's general AI knowledge
- ✅ System prompt (Aronhime teaching style)
- ❌ Specific PWS course content (1,136 chunks)
- ❌ Lecture-specific examples
- ❌ Exact framework definitions from the course

**Impact**: Larry can teach *about* innovation, but doesn't cite specific PWS materials.

---

## ✅ Solution Options

### Option 1: Generate PWS Chunks from Neo4j (Ideal)

If you have access to the Neo4j database with PWS content:

```bash
# 1. Configure Neo4j connection in extract_pws_content.py
# Edit lines with your credentials:
URI = "neo4j+s://your-instance.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "your-password"

# 2. Extract PWS content
python3 extract_pws_content.py

# This creates: pws_chunks.json (with 1,136 chunks)

# 3. Build File Search store
python3 build_larry_navigator.py

# This creates: larry_store_info.json (with real store ID)

# 4. Use the enhanced version
python3 larry_with_knowledge.py
```

**Result**: Full PWS knowledge base integrated! 🎉

---

### Option 2: Request Pre-Built Chunks (Quick)

If you don't have Neo4j access:

1. **Contact the course administrator** for `pws_chunks.json`
2. Place it in the repo root
3. Run: `python3 build_larry_navigator.py`
4. Start using: `python3 larry_with_knowledge.py`

---

### Option 3: Manual Content Creation (Flexible)

Create your own knowledge base:

```bash
# Create pws_chunks.json manually
cat > pws_chunks.json << 'EOF'
[
  {
    "content": "Creative Destruction is...",
    "lecture_number": "N01",
    "title": "Introduction to PWS",
    "week": 1,
    "position": 1,
    "complexity": "foundational",
    "personas": ["student", "entrepreneur"],
    "problem_types": ["general"],
    "frameworks": ["Creative Destruction"]
  },
  {
    "content": "Un-defined problems are...",
    "lecture_number": "N02",
    "title": "Un-Defined Problems",
    "week": 2,
    "position": 1,
    "complexity": "intermediate",
    "personas": ["all"],
    "problem_types": ["un-defined"],
    "frameworks": ["Problem Typology"]
  }
  // Add more chunks...
]
EOF

# Then build the store
python3 build_larry_navigator.py
```

**Format for each chunk:**
```json
{
  "content": "The actual text content (can be several paragraphs)",
  "lecture_number": "N01-N10",
  "title": "Lecture title",
  "week": 1-10,
  "position": 1-100,
  "complexity": "foundational|intermediate|advanced",
  "personas": ["student", "entrepreneur", "corporate", "consultant", "researcher"],
  "problem_types": ["un-defined", "ill-defined", "well-defined", "wicked"],
  "frameworks": ["Framework Name", "Another Framework"]
}
```

---

### Option 4: Use Without Knowledge Base (Current State)

Keep using Larry without PWS-specific content:

```bash
# Use the enhanced version without File Search
python3 larry_chatbot_enhanced.py
```

**Pros:**
- Works immediately
- No setup required
- Still uses Aronhime teaching style

**Cons:**
- No specific PWS lecture content
- No exact framework definitions from course
- Can't cite specific lectures
- Less accurate for course-specific questions

---

## 🔬 Understanding the Knowledge Architecture

### Current Data Flow (WITHOUT Knowledge Base):

```
User Question
    ↓
Persona Detection + Question Classification
    ↓
Enhanced System Prompt (Aronhime style)
    ↓
Gemini 2.0 Flash (general knowledge only)
    ↓
Response
```

### Desired Data Flow (WITH Knowledge Base):

```
User Question
    ↓
Persona Detection + Question Classification
    ↓
File Search Retrieval (searches 1,136 PWS chunks)
    ↓
Enhanced System Prompt + Retrieved Context
    ↓
Gemini 2.0 Flash (general knowledge + specific PWS content)
    ↓
Response with Citations
```

---

## 📊 Knowledge Base Structure

When properly set up:

```
pws_chunks.json (1,136 chunks)
    ↓ extracted from
Neo4j Database (DocumentChunk nodes)
    ↓ uploaded to
Google AI File Search Store
    ↓ referenced by
larry_store_info.json (store ID)
    ↓ used by
larry_with_knowledge.py (chatbot)
```

---

## 🛠️ Quick Diagnosis

Check your current status:

```bash
# Check if chunks exist
ls -la pws_chunks.json
# If missing: Need Option 1, 2, or 3

# Check store info
cat larry_store_info.json
# If shows "placeholder": Need to run build_larry_navigator.py

# Check current chatbot
grep "File Search temporarily disabled" larry_chatbot.py
# If found: Use larry_with_knowledge.py instead
```

---

## 🎯 Recommended Path Forward

**For Course Administrators (with Neo4j):**
→ Use Option 1 (full Neo4j extraction)

**For Course Instructors/TAs:**
→ Use Option 2 (request pre-built chunks)

**For Students/Users:**
→ Use Option 4 (works without knowledge base)
→ Or Option 3 (create minimal chunks for your specific needs)

**For Deployment (Streamlit Cloud):**
1. Generate `pws_chunks.json` locally (Options 1-3)
2. Run `build_larry_navigator.py` locally
3. Commit the generated `larry_store_info.json`
4. The File Search store persists in Google AI (linked by store ID)
5. Deploy to Streamlit Cloud - will use the cloud store

---

## 🚀 Testing After Fix

Once you've enabled the knowledge base:

```bash
# Test with a PWS-specific question
python3 larry_with_knowledge.py

# Ask: "What does lecture N02 cover?"
# Larry should cite specific PWS content

# Ask: "Explain the Mom Test from the course"
# Should get PWS-specific explanation

# Ask: "What frameworks are in week 3?"
# Should retrieve from knowledge base
```

**Success indicators:**
- ✅ Larry cites specific lectures (N01-N10)
- ✅ Responses match PWS course content
- ✅ Can navigate by week/lecture number
- ✅ Provides course-specific examples

---

## ⚠️ Important Notes

1. **Google AI Quotas**: File Search has API limits
   - Free tier: Limited queries/month
   - Monitor usage in Google AI Studio

2. **Store Persistence**: Once created, the File Search store persists
   - No need to rebuild unless content changes
   - Store ID in `larry_store_info.json` is the key

3. **Security**: API key is hardcoded in files
   - For production: Use environment variables
   - Already configured in Streamlit app (reads from secrets)

4. **Cost**: File Search may incur costs
   - Check Google AI pricing
   - Consider usage limits for public deployment

---

## 📞 Need Help?

**If you have Neo4j access but extract fails:**
- Check Neo4j credentials in `extract_pws_content.py`
- Verify Neo4j instance is running
- Check DocumentChunk nodes exist: `MATCH (d:DocumentChunk) RETURN count(d)`

**If build_larry_navigator.py fails:**
- Verify `pws_chunks.json` exists and is valid JSON
- Check Google AI API key is valid
- Monitor for API quota limits

**If File Search doesn't work in chatbot:**
- Use `larry_with_knowledge.py` (not `larry_chatbot.py`)
- Check `larry_store_info.json` has a real store_name (not "placeholder")
- Verify internet connection for API calls

---

## 🎓 Summary

**The Fix:**
1. Get `pws_chunks.json` (from Neo4j, admin, or manually)
2. Run `python3 build_larry_navigator.py`
3. Use `python3 larry_with_knowledge.py`

**The Result:**
Larry Navigator with full PWS knowledge base! 🎉

---

**Ready to fix it?** Choose your option above and get Larry's full knowledge activated!
