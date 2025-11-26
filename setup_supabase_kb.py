#!/usr/bin/env python3
"""
Set up Larry Navigator Knowledge Base on Supabase with pgvector
"""

import os
import json
import time
from supabase import create_client, Client
from google import genai

print("=" * 80)
print("🚀 LARRY NAVIGATOR - SUPABASE KNOWLEDGE BASE SETUP")
print("=" * 80)
print()

# Configuration (from environment variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_API_KEY")

if not SUPABASE_KEY:
    print("❌ SUPABASE_SERVICE_KEY not set!")
    print()
    print("Please set your Supabase service_role key:")
    print("export SUPABASE_SERVICE_KEY='your-service-role-key'")
    print()
    print("Get it from: Project Settings → API → service_role")
    exit(1)

print(f"🔗 Supabase URL: {SUPABASE_URL}")
print(f"🔑 Supabase Key: {SUPABASE_KEY[:20]}...")
print(f"🔑 Google AI Key: {GOOGLE_AI_KEY[:20]}...")
print()

# Load chunks
print("📁 Loading neo4j_chunks.json...")
with open('neo4j_chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)
print(f"✓ Loaded {len(chunks)} chunks")
print()

# Initialize clients
print("🔌 Connecting to services...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    gemini_client = genai.Client(api_key=GOOGLE_AI_KEY)
    print("✓ Connected to Supabase")
    print("✓ Connected to Google AI")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

print()

# Test table exists
print("🔍 Checking if knowledge_base table exists...")
try:
    test = supabase.table('knowledge_base').select("count", count='exact').limit(1).execute()
    print(f"✓ Table exists (current rows: {test.count})")
except Exception as e:
    print(f"❌ Table doesn't exist or error: {e}")
    print()
    print("Please create the table first. Run this SQL in Supabase:")
    print("""
CREATE TABLE knowledge_base (
  id BIGSERIAL PRIMARY KEY,
  chunk_id TEXT UNIQUE NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  source TEXT,
  embedding VECTOR(768),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON knowledge_base FOR SELECT TO public USING (true);
""")
    exit(1)

print()
print("=" * 80)
print(f"🧠 GENERATING EMBEDDINGS & UPLOADING {len(chunks)} CHUNKS")
print("=" * 80)
print()

uploaded = 0
failed = 0
errors = []
batch_size = 10

for i, chunk in enumerate(chunks, 1):
    try:
        # Prepare text for embedding
        text_to_embed = f"{chunk.get('title', '')}\n\n{chunk.get('content', '')}"

        # Generate embedding using Gemini
        result = gemini_client.models.embed_content(
            model="models/text-embedding-004",
            contents=text_to_embed
        )

        embedding = result.embeddings[0].values

        # Insert into Supabase
        data = {
            "chunk_id": chunk.get('id', f'chunk_{i}'),
            "title": chunk.get('title', '')[:500],  # Truncate if too long
            "content": chunk.get('content', ''),
            "source": chunk.get('source', ''),
            "embedding": embedding
        }

        supabase.table('knowledge_base').insert(data).execute()
        uploaded += 1

        # Progress update
        if i % batch_size == 0 or i == len(chunks):
            print(f"  Progress: {i}/{len(chunks)} ({int(i/len(chunks)*100)}%) - ✅ {uploaded} uploaded, ❌ {failed} failed")

        # Rate limiting
        if i % batch_size == 0 and i < len(chunks):
            time.sleep(1)

    except Exception as e:
        failed += 1
        error_msg = str(e)[:200]
        if failed <= 5:
            print(f"  ⚠️ Failed chunk {i}: {error_msg}")
        errors.append({"chunk": i, "error": error_msg})

print()
print("=" * 80)
print("✅ SUPABASE KNOWLEDGE BASE SETUP COMPLETE!")
print("=" * 80)
print()

print("📊 Summary:")
print(f"  • Total chunks: {len(chunks)}")
print(f"  • Successfully uploaded: {uploaded}")
print(f"  • Failed: {failed}")
print(f"  • Success rate: {int(uploaded/len(chunks)*100)}%")
print()

# Save configuration
config = {
    "type": "supabase",
    "url": SUPABASE_URL,
    "table": "knowledge_base",
    "total_chunks": uploaded,
    "embedding_model": "text-embedding-004",
    "embedding_dimensions": 768,
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open('larry_kb_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✓ Configuration saved to larry_kb_config.json")
print()

if errors:
    print(f"⚠️ {len(errors)} errors occurred. Saving to errors.json...")
    with open('migration_errors.json', 'w') as f:
        json.dump(errors, f, indent=2)
    print("✓ Errors saved to migration_errors.json")
    print()

print("🎯 Your knowledge base is ready!")
print()
print("Next: Test similarity search with test_supabase_search.py")
print()
