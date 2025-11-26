#!/usr/bin/env python3
"""
Test Supabase knowledge base similarity search
"""

import os
import json
from supabase import create_client, Client
from google import genai

print("=" * 80)
print("🧪 TESTING SUPABASE KNOWLEDGE BASE SEARCH")
print("=" * 80)
print()

# Configuration (from environment variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_AI_KEY]):
    print("❌ Missing environment variables!")
    print("Please set: SUPABASE_URL, SUPABASE_KEY, GOOGLE_AI_API_KEY")
    exit(1)

# Connect
print("🔌 Connecting...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
gemini_client = genai.Client(api_key=GOOGLE_AI_KEY)
print("✓ Connected")
print()

# Test queries
test_queries = [
    "What is the PWS framework?",
    "Explain the Cynefin framework",
    "How do I validate a problem?",
    "What is Jobs to be Done?"
]

for query in test_queries:
    print("=" * 80)
    print(f"🔍 Query: {query}")
    print("=" * 80)
    print()

    try:
        # Generate query embedding
        print("  Generating embedding...")
        result = gemini_client.models.embed_content(
            model="models/text-embedding-004",
            contents=query
        )
        query_embedding = result.embeddings[0].values

        # Search using RPC function
        print("  Searching knowledge base...")
        response = supabase.rpc(
            'search_knowledge_base',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5,
                'match_count': 5
            }
        ).execute()

        results = response.data

        print(f"\n  ✅ Found {len(results)} results:")
        print()

        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result['title']}")
            print(f"     Similarity: {result['similarity']:.3f}")
            print(f"     Content preview: {result['content'][:150]}...")
            print(f"     Source: {result['source']}")
            print()

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

print("=" * 80)
print("✅ SEARCH TEST COMPLETE")
print("=" * 80)
