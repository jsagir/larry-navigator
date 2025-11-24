#!/usr/bin/env python3
import os
import json
import time
from neo4j import GraphDatabase
from google import genai
from google.genai import types

print("=" * 80)
print("🚀 CREATE NEW FILE SEARCH STORE + UPLOAD")
print("=" * 80)
print()

# Load chunks
print("📁 Loading neo4j_chunks.json...")
with open("neo4j_chunks.json", "r") as f:
    chunks = json.load(f)
print(f"✓ Loaded {len(chunks):,} chunks")
print()

# Initialize Google AI client
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key:
    print("❌ GOOGLE_AI_API_KEY not set!")
    exit(1)

print("🔌 Initializing Google AI client...")
client = genai.Client(api_key=api_key)
print("✓ Connected")
print()

# Create NEW File Search store
print("=" * 80)
print("📦 CREATING NEW FILE SEARCH STORE")
print("=" * 80)
print()

try:
    print("Creating store...")
    store = client.file_search_stores.create(
        config={'display_name': "Larry Navigator Neo4j Knowledge"}
    )
    store_name = store.name
    print(f"✓ Created: {store_name}")
    print()
except Exception as e:
    print(f"❌ Error creating store: {e}")
    exit(1)

# Upload chunks
print("=" * 80)
print("📤 UPLOADING CHUNKS TO NEW STORE")
print("=" * 80)
print()

successful = 0
failed = 0

for idx, chunk in enumerate(chunks, 1):
    try:
        # Create temp file
        chunk_id = chunk.get("chunk_id") or f"chunk_{idx}"
        chunk_file = f"/tmp/neo4j_{chunk_id[:12].replace('/', '_')}.txt"

        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(chunk["content"])

        # Prepare metadata
        metadata = chunk.get("metadata", {})
        metadata_dict = {
            "source_file": metadata.get("source_file", ""),
            "document_type": metadata.get("document_type", ""),
            "difficulty": metadata.get("difficulty", "intermediate"),
        }

        # Remove empty values
        metadata_dict = {k: v for k, v in metadata_dict.items() if v and v != "None"}

        # Convert to File Search metadata format
        custom_metadata = [
            {"key": k, "string_value": v}
            for k, v in metadata_dict.items()
        ]

        # Upload
        operation = client.file_search_stores.upload_to_file_search_store(
            file=chunk_file,
            file_search_store_name=store_name,
            config={
                "display_name": f"{metadata.get('source_file', 'neo4j')} (chunk {idx})",
                "custom_metadata": custom_metadata
            }
        )

        successful += 1

        # Progress
        if idx % 50 == 0 or idx == len(chunks):
            percentage = (idx / len(chunks)) * 100
            print(f"  Progress: {idx}/{len(chunks)} ({percentage:.0f}%) - ✅ {successful} uploaded, ❌ {failed} failed")

        # Rate limiting
        if idx % 50 == 0:
            print(f"  ⏸️  Pausing for rate limit...")
            time.sleep(2)

        # Cleanup
        if os.path.exists(chunk_file):
            os.remove(chunk_file)

    except Exception as e:
        failed += 1
        if idx % 50 == 0:
            print(f"  ❌ Error on chunk {idx}: {str(e)[:80]}")
        if os.path.exists(chunk_file):
            os.remove(chunk_file)

# Final summary
print()
print("=" * 80)
print("✅ MIGRATION COMPLETE!")
print("=" * 80)
print()
print(f"📊 Summary:")
print(f"  • Total chunks: {len(chunks):,}")
print(f"  • Successfully uploaded: {successful:,}")
print(f"  • Failed: {failed:,}")
print(f"  • File Search store: {store_name}")
print()

# Save store info
store_info = {
    "store_name": store_name,
    "total_chunks": successful,
    "total_files": successful,
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open("larry_store_info.json", "w") as f:
    json.dump(store_info, f, indent=2)

print(f"✓ Store info saved to larry_store_info.json")
print()
print("🎉 Larry Navigator can now access this knowledge!")
