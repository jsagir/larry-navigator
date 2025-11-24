#!/usr/bin/env python3
import os
import json
from neo4j_to_filesearch import Neo4jToFileSearch

print("=" * 80)
print("🚀 NEO4J TO FILE SEARCH MIGRATION")
print("=" * 80)
print()

# Load existing chunks
print("📁 Loading neo4j_chunks.json...")
with open("neo4j_chunks.json", "r") as f:
    chunks = json.load(f)
print(f"✓ Loaded {len(chunks):,} chunks")
print()

# Initialize exporter
print("🔌 Connecting to services...")
exporter = Neo4jToFileSearch()
print()

# Upload to File Search
print("=" * 80)
print("📤 UPLOADING TO GOOGLE FILE SEARCH")
print("=" * 80)
print()

try:
    store_name = exporter.upload_to_file_search(chunks)
    print()
    print("=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"📊 Summary:")
    print(f"  • Chunks uploaded: {len(chunks):,}")
    print(f"  • File Search store: {store_name}")
    print()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

exporter.close()
