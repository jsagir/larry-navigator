# 🚀 Advanced File Search Implementation Guide

## ❌ Current State vs ✅ Target State

### Current Implementation (BASIC):
```python
# Using simple google.genai SDK
client.file_search_stores.upload_to_file_search_store(...)
```

**Issues:**
- ❌ No chunking strategy
- ❌ No hybrid (keyword + semantic) search
- ❌ No citations/source tracking
- ❌ Not using Vertex AI Search
- ❌ No Dense Passage Retrieval (DPR)
- ❌ File Search disabled in chatbot anyway
- ❌ Missing source data (pws_chunks.json)

### Target Implementation (ADVANCED):
```python
# Using Vertex AI + DPR indexing + Hybrid retrieval
```

**Features:**
- ✅ Semantic + keyword hybrid search
- ✅ Proper chunking (~1000 words)
- ✅ Citations with source tracking
- ✅ Re-ranking and deduplication
- ✅ IAM security
- ✅ Cost optimization
- ✅ Audit logging

---

## 📋 Step-by-Step Implementation

### Phase 1: Setup Google Cloud Infrastructure

#### 1.1 Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable discoveryengine.googleapis.com
```

#### 1.2 Create Service Account
```bash
PROJECT_ID="your-project-id"
SA_NAME="larry-retrieval-sa"

gcloud iam service-accounts create $SA_NAME \
    --display-name="Larry Retrieval Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

#### 1.3 Set Up Google Cloud Storage
```bash
BUCKET_NAME="larry-pws-knowledge"
LOCATION="us-central1"

gsutil mb -l $LOCATION gs://$BUCKET_NAME/
```

---

### Phase 2: Prepare and Chunk Documents

#### 2.1 Optimal Chunking Strategy

```python
def chunk_document(content, chunk_size=1000):
    """
    Chunk documents for optimal retrieval

    Best practices:
    - ~1000 words per chunk
    - Preserve semantic boundaries (paragraphs)
    - Add overlap for context continuity
    - Include metadata with each chunk
    """
    words = content.split()
    chunks = []

    for i in range(0, len(words), chunk_size - 100):  # 100-word overlap
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append({
            'content': chunk,
            'position': i // (chunk_size - 100),
            'chunk_size': len(chunk.split())
        })

    return chunks
```

#### 2.2 Enhanced Metadata Structure

```python
{
    "chunk_id": "N02_chunk_005",
    "content": "Un-defined problems are characterized by...",
    "metadata": {
        "lecture_number": "N02",
        "lecture_title": "Un-Defined Problems",
        "week": 2,
        "position": 5,
        "total_chunks": 45,
        "complexity": "intermediate",
        "personas": ["student", "entrepreneur"],
        "problem_types": ["un-defined"],
        "frameworks": ["Problem Typology", "Extensive Searching"],
        "keywords": ["uncertainty", "exploration", "undefined"],
        "word_count": 987,
        "created_at": "2024-01-15",
        "source_file": "N02_Undefined_Problems.pdf",
        "page_range": "12-14"
    }
}
```

---

### Phase 3: Upload and Index with Vertex AI

#### 3.1 Upload to Cloud Storage

```python
from google.cloud import storage

def upload_chunks_to_gcs(chunks, bucket_name):
    """Upload chunked documents to GCS"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for chunk in chunks:
        chunk_id = chunk['chunk_id']
        blob = bucket.blob(f"chunks/{chunk_id}.json")
        blob.upload_from_string(
            json.dumps(chunk),
            content_type='application/json'
        )

    print(f"✅ Uploaded {len(chunks)} chunks to gs://{bucket_name}/chunks/")
```

#### 3.2 Create Vertex AI Search Datastore

```python
from google.cloud import discoveryengine_v1beta as discoveryengine

def create_search_datastore(project_id, location):
    """
    Create Vertex AI Search datastore for PWS knowledge
    """
    client = discoveryengine.DataStoreServiceClient()

    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

    datastore = discoveryengine.DataStore(
        display_name="larry-pws-knowledge",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    operation = client.create_data_store(
        parent=parent,
        data_store=datastore,
        data_store_id="larry-pws-datastore"
    )

    response = operation.result()
    print(f"✅ Created datastore: {response.name}")
    return response
```

#### 3.3 Import Documents with DPR Indexing

```python
def import_documents_with_dpr(datastore_name, gcs_uri):
    """
    Import documents with Dense Passage Retrieval indexing
    """
    client = discoveryengine.DocumentServiceClient()

    import_config = discoveryengine.ImportDocumentsRequest.GcsSource(
        input_uris=[f"{gcs_uri}/*.json"],
        data_schema="content"  # Use content field for indexing
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=datastore_name,
        gcs_source=import_config,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    operation = client.import_documents(request=request)
    response = operation.result(timeout=300)  # 5 min timeout

    print(f"✅ Imported documents with DPR indexing")
    return response
```

---

### Phase 4: Implement Hybrid Retrieval

#### 4.1 Hybrid Search Function

```python
def hybrid_search(query, datastore_name, top_k=8):
    """
    Perform hybrid semantic + keyword search

    Args:
        query: User question
        datastore_name: Vertex AI datastore
        top_k: Number of results to return

    Returns:
        List of retrieved chunks with scores
    """
    client = discoveryengine.SearchServiceClient()

    # Semantic search component
    semantic_config = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=top_k
        )
    )

    # Construct hybrid search request
    request = discoveryengine.SearchRequest(
        serving_config=f"{datastore_name}/servingConfigs/default_config",
        query=query,
        page_size=top_k,
        content_search_spec=semantic_config,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        )
    )

    response = client.search(request)

    results = []
    for result in response.results:
        doc = result.document
        results.append({
            'content': doc.derived_struct_data['snippets'][0]['snippet'],
            'source': doc.derived_struct_data.get('link', 'Unknown'),
            'metadata': doc.derived_struct_data,
            'relevance_score': result.relevance_score,
            'chunk_id': doc.id
        })

    return results
```

#### 4.2 Re-Ranking Retrieved Results

```python
def rerank_results(query, results, min_score=0.6):
    """
    Re-rank and filter results by relevance

    - Remove duplicates
    - Filter by minimum relevance score
    - Diversify results (avoid similar chunks)
    """
    # Filter by minimum score
    filtered = [r for r in results if r['relevance_score'] >= min_score]

    # Deduplicate
    seen_content = set()
    deduped = []
    for result in filtered:
        content_hash = hash(result['content'][:100])  # First 100 chars
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            deduped.append(result)

    # Sort by relevance
    deduped.sort(key=lambda x: x['relevance_score'], reverse=True)

    return deduped
```

---

### Phase 5: Integration with Gemini

#### 5.1 Retrieval-Augmented Generation (RAG)

```python
def generate_with_retrieval(query, gemini_client):
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Format as context
    3. Generate response with citations
    """
    # Step 1: Retrieve
    retrieval_results = hybrid_search(
        query=query,
        datastore_name="projects/.../dataStor...
es/larry-pws-datastore",
        top_k=8
    )

    # Step 2: Re-rank
    top_results = rerank_results(query, retrieval_results, min_score=0.6)

    # Step 3: Format context
    context = "=== RETRIEVED PWS COURSE CONTENT ===\n\n"
    citations = []

    for i, result in enumerate(top_results, 1):
        metadata = result['metadata']
        lecture = metadata.get('lecture_number', 'Unknown')
        title = metadata.get('lecture_title', 'Unknown')

        context += f"[Source {i}] Lecture {lecture}: {title}\n"
        context += f"{result['content']}\n\n"

        citations.append({
            'index': i,
            'lecture': lecture,
            'title': title,
            'relevance': result['relevance_score']
        })

    context += "=== END RETRIEVED CONTENT ===\n\n"
    context += "INSTRUCTION: Use ONLY the above content. Cite sources as [Source #]. "
    context += "If insufficient information, state this explicitly.\n"

    # Step 4: Generate with Gemini
    system_prompt = f"""{LARRY_SYSTEM_PROMPT}

{context}

Respond using the Aronhime method, citing every claim from the sources above.
"""

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7
        )
    )

    return {
        'response': response.text,
        'citations': citations,
        'retrieval_count': len(top_results)
    }
```

---

### Phase 6: Security & Optimization

#### 6.1 IAM Security

```bash
# Restrict datastore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:larry-retrieval-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/discoveryengine.viewer" \
    --condition=None

# Enable audit logging
gcloud logging write larry-retrieval "Query executed" \
    --severity=INFO \
    --resource=projects/$PROJECT_ID
```

#### 6.2 Cost Optimization

```python
# Implement caching for frequent queries
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query_hash):
    """Cache top 100 frequent queries"""
    return hybrid_search(query_hash)

# Batch queries during off-peak
def batch_preload_common_queries():
    """Pre-load cache with common PWS questions"""
    common_queries = [
        "What is Creative Destruction?",
        "Explain Three Box Solution",
        "Difference between ill-defined and un-defined"
    ]
    for q in common_queries:
        cached_search(hash(q))
```

---

## 📊 Expected Performance

### Metrics to Track:

1. **Retrieval Quality**
   - Precision@K (top K results relevant)
   - Recall (% of relevant docs retrieved)
   - MRR (Mean Reciprocal Rank)

2. **Latency**
   - Search time: < 500ms target
   - End-to-end response: < 3s

3. **Cost**
   - Vertex AI Search: ~$0.50-2.00 per 1000 queries
   - Gemini API: ~$0.002-0.01 per 1000 tokens

---

## 🎯 Implementation Roadmap

### Week 1: Infrastructure
- [ ] Set up Google Cloud project
- [ ] Enable APIs and create service account
- [ ] Create GCS bucket

### Week 2: Data Preparation
- [ ] Extract PWS content from Neo4j
- [ ] Implement chunking strategy
- [ ] Enrich metadata
- [ ] Upload to GCS

### Week 3: Indexing
- [ ] Create Vertex AI datastore
- [ ] Import documents with DPR
- [ ] Test basic search

### Week 4: Integration
- [ ] Implement hybrid search
- [ ] Add re-ranking
- [ ] Integrate with Gemini
- [ ] Add citation system

### Week 5: Testing & Optimization
- [ ] Run edge case tests
- [ ] Optimize chunking
- [ ] Tune relevance thresholds
- [ ] Implement caching

### Week 6: Deployment
- [ ] Deploy to production
- [ ] Set up monitoring
- [ ] Create documentation
- [ ] Train users

---

## ⚠️ Current Blockers

1. **Missing Data**: Need `pws_chunks.json` from Neo4j
2. **GCP Setup**: Requires Google Cloud project with billing
3. **API Access**: Need Vertex AI API enabled
4. **Cost**: Vertex AI Search is paid (vs current free Gemini only)

---

## 🔄 Migration Path

### From Current → Advanced:

**Option A: Quick (Keep simple SDK)**
1. Generate pws_chunks.json
2. Use current build_larry_navigator.py
3. Re-enable File Search in chatbot
4. Add basic citations

**Option B: Full (Vertex AI)**
1. Complete GCP setup (this guide)
2. Migrate to Vertex AI Search
3. Implement hybrid retrieval
4. Full citation system
5. Advanced monitoring

**Recommendation**: Start with Option A, migrate to Option B for production.

---

## 📚 References

- [Vertex AI Search Documentation](https://cloud.google.com/generative-ai-app-builder/docs)
- [Dense Passage Retrieval Paper](https://arxiv.org/abs/2004.04906)
- [RAG Best Practices](https://www.anthropic.com/research/rag)
- [Gemini File Search API](https://ai.google.dev/gemini-api/docs/file-search)

---

**Ready to implement?** Start with the infrastructure setup and work through each phase systematically! 🚀
