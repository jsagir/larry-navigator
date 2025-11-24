# 🔍 Tavily Web Search Configuration

## Overview

Larry Navigator uses **Tavily AI** for intelligent web search when users ask about current events, recent research, or real-time information. The system automatically routes queries to the appropriate tool.

## Architecture

```
┌─────────────────────────────────────┐
│  User Query                         │
│  "Latest AI trends in 2025"         │
└───────────┬─────────────────────────┘
            │
┌───────────▼─────────────────────────┐
│  Intelligent Router                 │
│  (larry_router.py)                  │
│  - Analyzes query keywords          │
│  - Detects time-sensitive queries   │
│  - Routes to appropriate tool       │
└───────────┬─────────────────────────┘
            │
    ┌───────┴────────┬──────────────┐
    │                │              │
┌───▼─────────┐ ┌───▼───────┐ ┌───▼──────────┐
│ File Search │ │ Web Search│ │ Neo4j        │
│ (Default)   │ │ (Tavily)  │ │ (Optional)   │
│             │ │           │ │              │
│ PWS docs    │ │ Real-time │ │ Knowledge    │
│ Frameworks  │ │ web data  │ │ graph        │
│ Course      │ │ Current   │ │              │
│ materials   │ │ research  │ │              │
└─────────────┘ └───────────┘ └──────────────┘
```

## Web Search Triggers

### Automatic Routing

The router automatically sends queries to Tavily when it detects:

#### 1. Time-Sensitive Keywords
```python
["latest", "recent", "current", "today", "this week", "this month",
 "breaking", "news", "update", "now", "2024", "2025"]
```

**Example:**
- ✅ "What are the latest AI trends?"
- ✅ "Recent developments in quantum computing"
- ✅ "Current market conditions for startups"

#### 2. Specific Web Domains
```python
["stock price", "market cap", "company valuation",
 "weather", "sports score", "election results",
 "trending", "viral", "popular now"]
```

**Example:**
- ✅ "What's the stock price of OpenAI?"
- ✅ "Trending innovation frameworks"
- ✅ "Popular startups in 2025"

#### 3. Explicit Web Search Requests
```python
["search the web", "look up online", "find on the internet",
 "google", "search for"]
```

**Example:**
- ✅ "Search the web for JTBD case studies"
- ✅ "Look up online courses about innovation"
- ✅ "Google latest research on problem-solving"

## Configuration

### Required Dependencies

```txt
# requirements.txt
tavily-python==0.3.3
langchain-core==0.3.34
langchain-community==0.3.14
langchain-anthropic==0.3.7
anthropic>=0.45.0,<1
```

### Environment Variables

#### Required for Web Search
```bash
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Optional (for other features)
```bash
GOOGLE_AI_API_KEY=AIzaSy...  # File Search (required)
NEO4J_URI=neo4j+s://...      # Knowledge graph (optional)
NEO4J_USER=neo4j             # Knowledge graph (optional)
NEO4J_PASSWORD=...           # Knowledge graph (optional)
```

### Getting a Tavily API Key

1. Visit https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes:
   - 1,000 API calls per month
   - Advanced search depth
   - AI-generated summaries

## Code Integration

### 1. Routing Logic (larry_router.py)

```python
def route_query(user_message: str) -> QueryRoute:
    """Routes queries to file_search, neo4j, or web_search"""
    message_lower = user_message.lower()

    # Web Search Triggers
    current_time_keywords = [
        "latest", "recent", "current", "today", "this week"
    ]

    if any(keyword in message_lower for keyword in current_time_keywords):
        return "web_search"  # Route to Tavily

    return "file_search"  # Default to Gemini File Search
```

### 2. Web Search Handler (larry_chat.py)

```python
def _handle_web_search(self, user_message: str) -> Iterator[str]:
    """Handle web search queries."""
    try:
        # Web search tool returns complete response (not streaming)
        result = self.web_search_tool._run(user_message)
        yield result
    except Exception as e:
        yield f"⚠️ Web Search Error: {str(e)}"
```

### 3. Tavily Integration (larry_tavily_search.py)

```python
def search_with_tavily(
    query: str,
    tavily_api_key: str,
    max_results: int = 5,
    search_depth: str = "advanced",
    include_answer: bool = True
) -> Optional[Dict]:
    """Search using Tavily AI search engine"""

    tavily = TavilyClient(api_key=tavily_api_key)

    results = tavily.search(
        query=query,
        search_depth=search_depth,  # "advanced" for higher quality
        max_results=max_results,
        include_answer=include_answer,  # AI-generated summary
        include_raw_content=False,
        include_images=False
    )

    return results
```

### 4. Optional Imports (Graceful Degradation)

```python
# larry_chat.py
try:
    from larry_tools import WebSearchTool
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    class WebSearchTool:
        def _run(self, query: str) -> str:
            return "⚠️ Web search is not configured. Please install langchain dependencies."
```

**Why This Matters:**
- ✅ File Search works even if Tavily is not configured
- ✅ No hard dependency on LangChain for core functionality
- ✅ Graceful error messages if web search unavailable

## Response Format

### Tavily Web Search Response

```markdown
🔎 **Current Research Findings:**

Based on the latest cutting-edge research and industry reports:

**AI Summary:** [Tavily's AI-generated answer summary]

**Sources:**

**1. [Article Title](https://example.com)** (Relevance: High)
   Excerpt from the article showing key information...

**2. [Research Paper](https://example.com/paper)** (Relevance: Medium)
   Another relevant excerpt with current data...

**3. [Blog Post](https://example.com/blog)** (Relevance: High)
   Additional context and insights...

**Synthesis:** These findings represent cutting-edge, hyper-validated research from real-time web search.
```

## Testing Web Search

### Test Query Routing

```python
from larry_router import route_query

# Test web search triggers
print(route_query("What are the latest AI trends?"))  # → "web_search"
print(route_query("Recent startup failures"))         # → "web_search"
print(route_query("Search the web for JTBD"))        # → "web_search"

# Test file search (default)
print(route_query("What is Jobs to be Done?"))       # → "file_search"
print(route_query("Explain innovation frameworks"))  # → "file_search"
```

### Test Tavily Integration

```bash
# Set API key
export TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxx

# Run test
python3 -c "
from larry_tavily_search import integrate_search_with_response

result = integrate_search_with_response(
    user_message='Latest AI trends in 2025',
    persona='general',
    problem_type='general',
    tavily_api_key='tvly-xxxxx'
)

print(result)
"
```

### Test Full Chat Flow

```bash
# Test end-to-end
GOOGLE_AI_API_KEY=AIzaSy... TAVILY_API_KEY=tvly-... python3 -c "
from larry_chat import create_chat_handler

handler = create_chat_handler()

# This should route to web search
for chunk in handler.chat('What are the latest AI trends in 2025?'):
    print(chunk, end='')
"
```

## Troubleshooting

### Issue: "Web search is not configured"

**Cause:** Missing `tavily-python` or LangChain dependencies

**Fix:**
```bash
pip install tavily-python langchain-core langchain-community langchain-anthropic
```

### Issue: "TAVILY_API_KEY environment variable is missing"

**Cause:** API key not set

**Fix:**
```bash
# For local testing
export TAVILY_API_KEY=tvly-xxxxxxxxxx

# For Streamlit Cloud
# Add to Secrets management in dashboard
```

### Issue: Query Not Routing to Web Search

**Cause:** Query doesn't match trigger keywords

**Debug:**
```python
from larry_router import route_query

query = "Your query here"
route = route_query(query)
print(f"Route: {route}")  # Should show "web_search"
```

**Fix:** Either:
1. Add explicit trigger: "Search the web for [your query]"
2. Add time-sensitive keyword: "Latest [your query]"
3. Modify routing keywords in `larry_router.py`

### Issue: Web Search Returns No Results

**Cause:** Query too specific or Tavily API issue

**Debug:**
```python
from larry_tavily_search import search_with_tavily

results = search_with_tavily(
    query="Your query",
    tavily_api_key="tvly-xxx",
    max_results=5
)

print(f"Results: {len(results.get('results', []))}")
```

**Fix:**
- Broaden the query terms
- Check Tavily API quota (1,000 calls/month free tier)
- Verify API key is valid

## Deployment Checklist

### For Streamlit Cloud

1. ✅ Add `tavily-python==0.3.3` to requirements.txt
2. ✅ Add LangChain dependencies to requirements.txt
3. ✅ Add `TAVILY_API_KEY` to Streamlit Secrets
4. ✅ Verify routing triggers match your use cases
5. ✅ Test with time-sensitive queries
6. ✅ Monitor API usage in Tavily dashboard

### Environment Variables in Streamlit Cloud

```toml
# .streamlit/secrets.toml (for local testing)
GOOGLE_AI_API_KEY = "AIzaSy..."
TAVILY_API_KEY = "tvly-..."
NEO4J_URI = "neo4j+s://..."  # Optional
NEO4J_USER = "neo4j"         # Optional
NEO4J_PASSWORD = "..."       # Optional
```

### Verification Commands

```bash
# Check dependencies installed
streamlit run larry_app.py

# Verify in UI:
# 1. Ask "What are the latest AI trends?"
# 2. Should see: "Searching the web..." status
# 3. Response should include web sources with URLs
```

## Performance Characteristics

### Web Search (Tavily)
- **Latency:** 2-5 seconds (depends on search depth)
- **Search Depth:** "advanced" (higher quality, slower) or "basic" (faster)
- **Max Results:** Configurable (default 5)
- **Includes:** AI-generated summary + top sources with relevance scores

### File Search (Gemini)
- **Latency:** 10-15 seconds (includes retrieval + generation)
- **Streaming:** Real-time progressive display
- **Max Tokens:** 8,192
- **Includes:** Source citations with confidence scores

### Comparison

| Feature | Web Search (Tavily) | File Search (Gemini) |
|---------|-------------------|---------------------|
| **Data Freshness** | Real-time | Static (uploaded docs) |
| **Streaming** | ❌ No | ✅ Yes |
| **Latency** | 2-5s | 10-15s |
| **Source Attribution** | ✅ URLs + titles | ✅ Doc titles + confidence |
| **Use Case** | Current events | Course materials, frameworks |

## Best Practices

### When to Use Web Search
✅ Current events and breaking news
✅ Latest research and trends
✅ Real-time market data
✅ Company-specific information
✅ Validation of recent claims

### When to Use File Search
✅ Course materials and frameworks
✅ PWS methodology questions
✅ Innovation frameworks
✅ Case studies in uploaded docs
✅ General knowledge questions

### Query Optimization
```python
# Instead of generic queries
"Tell me about AI"  # → File Search

# Be specific for web search
"Latest AI breakthroughs in 2025"  # → Web Search
```

## Success Metrics

- ✅ Queries correctly routed based on keywords
- ✅ Web search returns within 5 seconds
- ✅ Sources include URLs and relevance scores
- ✅ Graceful fallback if Tavily unavailable
- ✅ File Search continues working independently

## Future Enhancements

### Potential Improvements
1. **Hybrid Search:** Combine File Search + Web Search for comprehensive answers
2. **Smart Caching:** Cache frequent web queries to reduce API calls
3. **Source Quality Filtering:** Prioritize peer-reviewed sources
4. **Custom Search Depth:** Let users choose basic vs advanced
5. **Search History:** Track and display recent web searches

### Cost Optimization
- **Tavily Free Tier:** 1,000 calls/month
- **Pro Tier:** $500/month for 100,000 calls
- **Caching Strategy:** Cache results for 1 hour to reduce duplicate queries

## Summary

✅ **Routing:** Automatic based on query keywords
✅ **Integration:** Tavily AI with advanced search depth
✅ **Fallback:** Graceful degradation if unavailable
✅ **UI:** Clear indication of web search vs file search
✅ **Sources:** URLs + relevance scores displayed
✅ **Performance:** 2-5s latency, real-time web data

Larry Navigator now has intelligent, multi-source knowledge retrieval! 🚀
