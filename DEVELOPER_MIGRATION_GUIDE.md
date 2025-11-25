# Developer Migration Guide: Google File Search → Supabase Vector DB

**For: Larry Navigator Development Team**
**Date: November 25, 2025**
**Status: Migration Complete - Ready for Integration**

---

## Table of Contents
1. [What Changed](#what-changed)
2. [Why We Migrated](#why-we-migrated)
3. [Architecture Comparison](#architecture-comparison)
4. [Code Changes Required](#code-changes-required)
5. [Step-by-Step Integration](#step-by-step-integration)
6. [Testing](#testing)
7. [Deployment](#deployment)

---

## What Changed

### OLD SYSTEM (Google File Search API)
- **Storage**: Google's proprietary vector store
- **API**: Google Generative AI File Search API
- **Embeddings**: Generated and managed by Google
- **Access**: Tied to specific API key/project
- **Problem**: When API key changed, lost access to existing store

### NEW SYSTEM (Supabase + pgvector)
- **Storage**: PostgreSQL with pgvector extension (your own database)
- **API**: Direct Supabase client + RPC functions
- **Embeddings**: You generate using Gemini, store in your DB
- **Access**: Full control, no API key lock-in
- **Benefit**: Complete ownership and portability

---

## Why We Migrated

### The Problem We Faced
```
❌ OLD: API key was exposed and had to be rotated
❌ RESULT: New API key couldn't access existing File Search store
❌ IMPACT: Lost access to 1,424 knowledge chunks
```

### The Solution
```
✅ NEW: Migrate to self-hosted Supabase PostgreSQL database
✅ RESULT: Full control over data, no API key dependencies
✅ IMPACT: All 1,424 chunks migrated successfully with 100% success rate
```

---

## Architecture Comparison

### BEFORE: Google File Search Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Larry Navigator App                      │
│                     (larry_app.py)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Uses Google Generative AI SDK
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Generative AI API                        │
│  • create_file()                                            │
│  • upload_file()                                            │
│  • File Search (opaque vector search)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Stored in Google's infrastructure
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          Google File Search Vector Store                     │
│  • Store ID: larry-navigator-neo4j-knowl-30cntohiwvs4      │
│  • 1,424 chunks                                             │
│  • Locked to original API key                              │
│  • ❌ INACCESSIBLE with new API key                         │
└─────────────────────────────────────────────────────────────┘
```

### AFTER: Supabase Vector DB Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Larry Navigator App                      │
│                     (larry_app.py)                          │
│  + import larry_supabase_rag                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Uses Supabase client
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Supabase Client                             │
│  • Direct PostgreSQL access                                 │
│  • RPC function calls: search_knowledge_base()             │
│  • Full SQL capabilities                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Your database (full control)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase PostgreSQL Database                    │
│  • Table: knowledge_base                                    │
│  • 1,424 rows with 768-dim embeddings                      │
│  • pgvector extension for similarity search                │
│  • IVFFlat index for fast queries                          │
│  • ✅ YOU OWN THIS DATA                                     │
└─────────────────────────────────────────────────────────────┘
                      ▲
                      │ Generate embeddings
┌─────────────────────┴───────────────────────────────────────┐
│              Google Gemini API (Embeddings Only)             │
│  • text-embedding-004 model                                 │
│  • Generates 768-dimensional vectors                        │
│  • Only used for embedding generation, NOT storage         │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Changes Required

### 1. OLD CODE: Google File Search (What to Remove/Replace)

```python
# ❌ OLD: larry_app.py using Google File Search

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import File

# OLD: Configure Google API
genai.configure(api_key=GOOGLE_AI_API_KEY)

# OLD: Reference to File Search store
FILE_SEARCH_STORE = "larry-navigator-neo4j-knowl-30cntohiwvs4"

def retrieve_context(query: str):
    """OLD way using File Search"""
    # This was Google's opaque API - you didn't control the search
    # The exact implementation was abstracted away

    # Pseudo-code of what happened:
    response = genai.generate_content(
        model="gemini-1.5-flash",
        contents=query,
        tools=[{
            "file_search": {
                "corpus_id": FILE_SEARCH_STORE
            }
        }]
    )

    # Google handled embedding generation, search, ranking internally
    # You got back relevant chunks but no control over parameters
    return response.text
```

**Problems with this approach:**
- ❌ No control over similarity thresholds
- ❌ Can't inspect embeddings
- ❌ Store tied to API key that created it
- ❌ Can't debug or optimize search
- ❌ Limited to Google's infrastructure

---

### 2. NEW CODE: Supabase Vector DB (What to Add)

```python
# ✅ NEW: larry_app.py using Supabase

from larry_supabase_rag import SupabaseKnowledgeBase

# NEW: Initialize Supabase knowledge base (reads from env vars)
kb = SupabaseKnowledgeBase()

def retrieve_context(query: str, top_k: int = 5):
    """NEW way using Supabase vector search"""

    # Direct control over search parameters
    results = kb.retrieve_context(
        query=query,
        top_k=top_k,              # Number of results
        threshold=0.5              # Minimum similarity (0.0-1.0)
    )

    # Returns list of dicts with full control:
    # [
    #   {
    #     'content': 'chunk content...',
    #     'title': 'Framework: JTBD',
    #     'source': 'module_2.md',
    #     'similarity': 0.747  # Actual similarity score!
    #   },
    #   ...
    # ]

    # Format for LLM prompt
    context_str = kb.format_context_for_llm(results)

    return context_str, results  # Return both formatted and raw data
```

**Benefits of this approach:**
- ✅ Full control over similarity thresholds
- ✅ Can inspect and log similarity scores
- ✅ Database is yours (export anytime)
- ✅ Can debug with direct SQL queries
- ✅ Portable to any PostgreSQL hosting

---

## Step-by-Step Integration

### STEP 1: Update requirements.txt

```diff
# requirements.txt

streamlit>=1.28.0
- google-generativeai>=0.3.0
+ google-generativeai>=0.3.0  # Still needed for embeddings
+ supabase>=2.0.0              # NEW: Add Supabase client
pandas
numpy
```

Install new dependency:
```bash
pip install supabase
```

---

### STEP 2: Update Environment Variables

**For local development (.env file):**
```bash
# OLD variables (keep for embeddings)
GOOGLE_AI_API_KEY="AIzaSyBsuaqlmsGGrFhdkkUhA936qrIaNWGkWfs"

# NEW variables (add these)
SUPABASE_URL="https://ulmymxxmvsehjiyymqoi.supabase.co"
SUPABASE_KEY="sb_publishable_uDXBTiy9AxSmqh-zsCthrw_w7ZOHRt9"
```

**For Streamlit Cloud (secrets.toml):**
```toml
# .streamlit/secrets.toml

# OLD (keep)
GOOGLE_AI_API_KEY = "AIzaSyBsuaqlmsGGrFhdkkUhA936qrIaNWGkWfs"

# NEW (add)
SUPABASE_URL = "https://ulmymxxmvsehjiyymqoi.supabase.co"
SUPABASE_KEY = "sb_publishable_uDXBTiy9AxSmqh-zsCthrw_w7ZOHRt9"
```

---

### STEP 3: Replace Knowledge Base Retrieval Code

#### BEFORE (Google File Search):

```python
# ❌ OLD: Somewhere in larry_app.py

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))

def chat_with_larry(user_message: str):
    # OLD: Use File Search via Gemini API
    response = genai.generate_content(
        model="gemini-1.5-flash",
        contents=user_message,
        tools=[{
            "file_search": {
                "corpus_id": "larry-navigator-neo4j-knowl-30cntohiwvs4"
            }
        }]
    )

    return response.text
```

#### AFTER (Supabase Vector DB):

```python
# ✅ NEW: In larry_app.py

from larry_supabase_rag import SupabaseKnowledgeBase
import os

# Initialize once (at module level or in session_state)
@st.cache_resource
def get_knowledge_base():
    return SupabaseKnowledgeBase()

kb = get_knowledge_base()

def chat_with_larry(user_message: str):
    # NEW: Retrieve context from Supabase
    context_chunks = kb.retrieve_context(
        query=user_message,
        top_k=5,           # Get top 5 most relevant chunks
        threshold=0.5      # Minimum similarity: 0.5 (balanced)
    )

    # Format context for LLM
    context_text = kb.format_context_for_llm(
        context_chunks,
        include_similarity=False  # Don't show similarity to user
    )

    # Build prompt with context
    prompt = f"""You are Larry, an expert in problem solving and innovation.

Context from PWS course materials:
{context_text}

User question: {user_message}

Provide a helpful, educational response based on the context above.
If the context doesn't contain relevant information, say so politely and
offer general guidance based on problem-solving principles."""

    # Call your LLM (Gemini, OpenAI, etc.)
    response = your_llm_call(prompt)  # Replace with actual LLM call

    return response, context_chunks  # Return both response and sources
```

---

### STEP 4: Update Chat Handler with Citation Support

```python
# ✅ NEW: Enhanced chat with source citations

def chat_with_larry_enhanced(user_message: str):
    # Retrieve context
    context_chunks = kb.retrieve_context(user_message, top_k=5, threshold=0.5)

    if not context_chunks:
        return "I don't have specific course material on that topic. Let me help with general guidance..."

    # Format context
    context_text = kb.format_context_for_llm(context_chunks)

    # Create prompt
    prompt = f"""Context from PWS course materials:
{context_text}

User question: {user_message}

Provide a helpful response. Reference the context sources when relevant."""

    # Get LLM response
    response = your_llm_call(prompt)

    # Display in Streamlit with sources
    st.write(response)

    # Show sources in expander
    with st.expander("📚 Sources"):
        for i, chunk in enumerate(context_chunks, 1):
            st.markdown(f"""
            **{i}. {chunk['title']}** (Relevance: {chunk['similarity']:.2%})
            > {chunk['content'][:200]}...
            """)

    return response
```

---

### STEP 5: Add Search Quality Monitoring (Optional but Recommended)

```python
# ✅ NEW: Log search performance for tuning

import logging

def retrieve_with_logging(query: str, threshold: float = 0.5):
    """Retrieve context and log performance metrics"""

    results = kb.retrieve_context(query, top_k=5, threshold=threshold)

    # Log for analytics
    logging.info({
        "query": query,
        "num_results": len(results),
        "top_similarity": results[0]['similarity'] if results else 0.0,
        "threshold": threshold
    })

    # Alert if no results (might need to lower threshold)
    if not results:
        logging.warning(f"No results for query: {query} (threshold={threshold})")

    return results
```

---

## Complete Example: Full Chat Integration

### Complete Before/After in larry_app.py

#### BEFORE (Google File Search):

```python
# ❌ OLD APPROACH

import streamlit as st
import google.generativeai as genai
import os

# Configure
genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
FILE_SEARCH_STORE = "larry-navigator-neo4j-knowl-30cntohiwvs4"

st.title("Larry Navigator")

# Chat input
if user_query := st.chat_input("Ask about problem solving..."):
    st.chat_message("user").write(user_query)

    # OLD: Use File Search (opaque, no control)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = genai.generate_content(
                model="gemini-1.5-flash",
                contents=user_query,
                tools=[{"file_search": {"corpus_id": FILE_SEARCH_STORE}}]
            )
            st.write(response.text)
```

#### AFTER (Supabase Vector DB):

```python
# ✅ NEW APPROACH

import streamlit as st
from larry_supabase_rag import SupabaseKnowledgeBase
from google import genai
import os

# Configure
@st.cache_resource
def init_services():
    kb = SupabaseKnowledgeBase()
    gemini = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))
    return kb, gemini

kb, gemini = init_services()

st.title("Larry Navigator")

# Chat input
if user_query := st.chat_input("Ask about problem solving..."):
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            # NEW: Retrieve context with full control
            context_chunks = kb.retrieve_context(
                query=user_query,
                top_k=5,
                threshold=0.5
            )

            # Format context for LLM
            context_text = kb.format_context_for_llm(context_chunks)

            # Build prompt
            prompt = f"""Context from PWS course materials:
{context_text}

User question: {user_query}

Provide a helpful, educational response."""

            # Generate response using Gemini
            response = gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            # Display response
            st.write(response.text)

            # Show sources
            if context_chunks:
                with st.expander(f"📚 {len(context_chunks)} Sources Used"):
                    for i, chunk in enumerate(context_chunks, 1):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{chunk['title']}**")
                            st.caption(chunk['content'][:150] + "...")
                        with col2:
                            st.metric("Relevance", f"{chunk['similarity']:.1%}")
```

---

## Testing

### 1. Test Module Directly

```bash
# Test the Supabase RAG module
cd /home/jsagi/larry-navigator
python3 larry_supabase_rag.py
```

Expected output:
```
Testing Supabase Knowledge Base...

✓ Connected to knowledge base
✓ Total chunks: 1424

Testing query: What is Jobs to be Done?
Found 3 results:
  - Untitled (similarity: 0.747)
  - Untitled (similarity: 0.530)
  - Untitled (similarity: 0.503)

✓ Module working correctly!
```

### 2. Test Search Functionality

```bash
# Run comprehensive search tests
python3 test_supabase_search.py
```

Expected: 4 test queries with results showing similarity scores

### 3. Test in Streamlit App

```bash
# Run your Streamlit app locally
streamlit run larry_app.py
```

Test with these queries:
- "What is the PWS framework?"
- "Explain the Cynefin framework"
- "What is Jobs to be Done?"

Verify:
- ✅ Responses are relevant
- ✅ Sources are displayed
- ✅ Similarity scores are reasonable (>0.5 for good matches)

---

## Deployment to Streamlit Cloud

### 1. Update Secrets

In Streamlit Cloud dashboard → Settings → Secrets:

```toml
GOOGLE_AI_API_KEY = "AIzaSyBsuaqlmsGGrFhdkkUhA936qrIaNWGkWfs"
SUPABASE_URL = "https://ulmymxxmvsehjiyymqoi.supabase.co"
SUPABASE_KEY = "sb_publishable_uDXBTiy9AxSmqh-zsCthrw_w7ZOHRt9"
```

### 2. Update requirements.txt

```
streamlit>=1.28.0
google-generativeai>=0.3.0
supabase>=2.0.0
pandas
numpy
```

### 3. Add larry_supabase_rag.py to Repository

```bash
git add larry_supabase_rag.py
git commit -m "feat: Add Supabase vector DB integration"
git push
```

### 4. Deploy

Streamlit Cloud will automatically:
1. Install new dependencies
2. Read secrets
3. Initialize Supabase connection
4. Start serving with new vector DB backend

---

## Performance Tuning

### Adjust Similarity Threshold Based on Results

```python
# Strict matching (high precision, fewer results)
results = kb.retrieve_context(query, threshold=0.7)

# Balanced (default - good for most cases)
results = kb.retrieve_context(query, threshold=0.5)

# Broad matching (high recall, more results)
results = kb.retrieve_context(query, threshold=0.3)
```

### Adjust Number of Results

```python
# Quick context (faster, less token usage)
results = kb.retrieve_context(query, top_k=3)

# Standard context
results = kb.retrieve_context(query, top_k=5)

# Comprehensive context (more tokens, more cost)
results = kb.retrieve_context(query, top_k=10)
```

### Monitor Search Quality

Add to your app:

```python
# Log search metrics
if st.session_state.get('debug_mode'):
    st.sidebar.metric("Chunks Retrieved", len(context_chunks))
    if context_chunks:
        st.sidebar.metric("Top Similarity", f"{context_chunks[0]['similarity']:.2%}")
```

---

## Rollback Plan (If Needed)

If you need to rollback to Google File Search:

1. **Keep old code in comments** during migration:
   ```python
   # OLD: Google File Search (backup)
   # response = genai.generate_content(...)

   # NEW: Supabase Vector DB
   results = kb.retrieve_context(...)
   ```

2. **Feature flag for gradual rollout**:
   ```python
   USE_SUPABASE = os.getenv("USE_SUPABASE", "true") == "true"

   if USE_SUPABASE:
       results = kb.retrieve_context(query)
   else:
       # Old File Search code
       pass
   ```

3. **Data is safe**: Your Supabase database remains intact, just switch the code back

---

## Troubleshooting

### "Module 'larry_supabase_rag' not found"
**Solution**: Add to repository and ensure it's in same directory as larry_app.py

### "No results found for query"
**Solution**: Lower threshold from 0.5 to 0.3:
```python
results = kb.retrieve_context(query, threshold=0.3)
```

### "Supabase connection failed"
**Solution**: Check environment variables are set correctly:
```python
import os
print(os.getenv("SUPABASE_URL"))  # Should print URL
print(os.getenv("SUPABASE_KEY"))  # Should print key
```

### "Slow query performance"
**Solution**: Database already has IVFFlat index. For large scale (>10K rows), adjust:
```sql
-- In Supabase SQL Editor
DROP INDEX knowledge_base_embedding_idx;
CREATE INDEX knowledge_base_embedding_idx
ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);  -- Increase lists for larger datasets
```

---

## Summary Checklist

### Migration Checklist

- [x] Supabase database created and migrated (1,424 chunks)
- [x] Search tested and verified (0.747 similarity for test queries)
- [ ] Update requirements.txt with `supabase>=2.0.0`
- [ ] Add environment variables (SUPABASE_URL, SUPABASE_KEY)
- [ ] Add larry_supabase_rag.py to project
- [ ] Update larry_app.py chat handler to use new retrieval
- [ ] Test locally with sample queries
- [ ] Update Streamlit Cloud secrets
- [ ] Deploy to production
- [ ] Monitor search quality and adjust thresholds

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `larry_supabase_rag.py` | Vector DB integration module | ✅ Ready |
| `create_supabase_table.sql` | Database schema | ✅ Executed |
| `setup_supabase_kb.py` | Migration script | ✅ Complete |
| `test_supabase_search.py` | Search tests | ✅ Passing |
| `larry_kb_config.json` | Configuration | ✅ Generated |
| `SUPABASE_SETUP_STEPS.md` | Setup guide | ✅ Available |
| `SUPABASE_MIGRATION_SUCCESS.md` | Full docs | ✅ Available |

---

## Quick Reference: Key Changes

| Aspect | OLD (File Search) | NEW (Supabase) |
|--------|------------------|----------------|
| **Import** | `import google.generativeai` | `from larry_supabase_rag import SupabaseKnowledgeBase` |
| **Init** | `genai.configure(api_key=key)` | `kb = SupabaseKnowledgeBase()` |
| **Retrieve** | `genai.generate_content(..., tools=[file_search])` | `kb.retrieve_context(query, top_k=5, threshold=0.5)` |
| **Control** | None (opaque API) | Full (threshold, top_k, similarity scores) |
| **Ownership** | Google's store | Your PostgreSQL database |
| **Portability** | Locked to Google | Portable (standard PostgreSQL) |
| **Debugging** | No direct access | Direct SQL queries |
| **Cost** | Pay per query | Free tier: 500MB + 2GB bandwidth |

---

## Support & Resources

- **Module**: `larry_supabase_rag.py` (docstrings included)
- **Tests**: `test_supabase_search.py`
- **Database**: https://ulmymxxmvsehjiyymqoi.supabase.co
- **Docs**: `SUPABASE_MIGRATION_SUCCESS.md`

**Migration Status**: ✅ Complete and Production Ready

---

**Questions?** Check the comprehensive documentation in `SUPABASE_MIGRATION_SUCCESS.md` or inspect the `larry_supabase_rag.py` module code for implementation details.
