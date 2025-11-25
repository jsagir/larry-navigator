# 🚨 QUICK FIX: App Error on Streamlit Cloud

## The Error

```
pydantic_core._pydantic_core.ValidationError
File "/mount/src/larry-navigator/larry_app.py", line 174, in stream_larry_response
    file_search=types.FileSearch(
        file_search_store=file_search_store
    )
```

**Problem:** The app is trying to use the old Google File Search store which is inaccessible.

**Solution:** Replace File Search with Supabase (which is already migrated and working!)

---

## OPTION 1: Quick Temporary Fix (5 minutes)

### Disable File Search temporarily to stop the error:

**Edit `larry_app.py` around line 167-179:**

```python
# OLD CODE (causing error):
    # Configure File Search
    config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=2048,
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store=file_search_store  # ❌ This fails!
                )
            )
        ]
    )
```

**Replace with:**

```python
# TEMPORARY FIX (no File Search):
    config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=2048,
        tools=[]  # ✅ Disabled File Search (app will work, but without knowledge base)
    )
```

This will get your app running again, but **without the knowledge base**.

---

## OPTION 2: Full Supabase Integration (20 minutes)

### Step 1: Add Supabase to requirements.txt

```text
# In requirements.txt, add:
supabase>=2.0.0
```

### Step 2: Add larry_supabase_rag.py to your repo

Upload the `larry_supabase_rag.py` file to your GitHub repo (same directory as larry_app.py).

### Step 3: Add Secrets in Streamlit Cloud

Go to Streamlit Cloud → Your App → Settings → Secrets

Add these to your secrets.toml:

```toml
SUPABASE_URL = "https://ulmymxxmvsehjiyymqoi.supabase.co"
SUPABASE_KEY = "sb_publishable_uDXBTiy9AxSmqh-zsCthrw_w7ZOHRt9"
GOOGLE_AI_API_KEY = "AIzaSyBsuaqlmsGGrFhdkkUhA936qrIaNWGkWfs"
```

### Step 4: Modify larry_app.py

**A) Add import at the top (around line 10):**

```python
from larry_supabase_rag import SupabaseKnowledgeBase
```

**B) Add initialization function (around line 65):**

```python
@st.cache_resource
def get_knowledge_base():
    """Initialize Supabase knowledge base"""
    return SupabaseKnowledgeBase()
```

**C) Replace `stream_larry_response` function:**

Find the function starting around line 129. Replace the ENTIRE function with this:

```python
def stream_larry_response(
    client: genai.Client,
    messages: List[Dict[str, str]],
    kb: SupabaseKnowledgeBase  # NEW parameter
) -> Iterator[str]:
    """
    Stream response from Larry using Supabase knowledge base
    """
    # Get last user message for context retrieval
    user_query = messages[-1]["content"] if messages else ""

    # Retrieve context from Supabase
    context_chunks = kb.retrieve_context(
        query=user_query,
        top_k=5,
        threshold=0.5
    )

    # Format context for LLM
    context_text = ""
    if context_chunks:
        context_text = "\n\n## Context from PWS Course Materials:\n\n"
        context_text += kb.format_context_for_llm(context_chunks, include_similarity=False)

    # Build conversation with context
    contents = []
    for msg in messages:
        contents.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}]
        })

    # Add system context if available
    if context_text and messages[-1]["role"] == "user":
        contents[-1]["parts"][0]["text"] = f"{context_text}\n\n{contents[-1]['parts'][0]['text']}"

    # Configure generation (NO File Search)
    config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=2048,
        system_instruction=LARRY_SYSTEM_PROMPT
    )

    # Stream response
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash-exp",
        contents=contents,
        config=config
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text
```

**D) Update the main() function:**

Find around line 324-330, replace:

```python
# OLD:
    # Load config
    file_search_config = load_file_search_config()
    file_search_store = file_search_config.get("store_name")

    # Get client
    client = get_gemini_client()
```

With:

```python
# NEW:
    # Get client and knowledge base
    client = get_gemini_client()
    kb = get_knowledge_base()  # Initialize Supabase KB
```

**E) Update the streaming call around line 373:**

Find:

```python
# OLD:
    for chunk in stream_larry_response(
        client,
        st.session_state.messages,
        file_search_store
    ):
```

Replace with:

```python
# NEW:
    for chunk in stream_larry_response(
        client,
        st.session_state.messages,
        kb  # Pass Supabase KB instead of file_search_store
    ):
```

### Step 5: Remove/Comment the old function

Comment out or remove the `load_file_search_config()` function (lines 52-62) since it's no longer needed.

### Step 6: Deploy

```bash
git add larry_app.py larry_supabase_rag.py requirements.txt
git commit -m "fix: Replace File Search with Supabase vector DB"
git push
```

Streamlit Cloud will automatically redeploy.

---

## Verification

After deploying, test with these queries:

1. "What is the PWS framework?"
2. "Explain the Cynefin framework"
3. "What is Jobs to be Done?"

You should get responses with relevant context from the knowledge base!

---

## Need Help?

If you get stuck, refer to:
- `DEVELOPER_MIGRATION_GUIDE.md` - Complete integration guide
- `larry_supabase_rag.py` - See the module code
- `SUPABASE_MIGRATION_SUCCESS.md` - Full documentation

The knowledge base is already live with all 1,424 chunks and working perfectly!
