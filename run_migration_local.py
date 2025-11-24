#!/usr/bin/env python3
"""
Interactive Neo4j to File Search Migration
Prompts for API keys at runtime - NO HARDCODING
"""

import os
import sys
import json
import time
from pathlib import Path
from getpass import getpass

print("=" * 80)
print("🚀 NEO4J TO FILE SEARCH MIGRATION (Interactive)")
print("=" * 80)
print()
print("This script will upload 1,424 chunks from Neo4j to Google File Search")
print("You'll be prompted for API keys - they will NOT be saved to disk")
print()

# Prompt for credentials
print("📋 Enter your credentials:")
print()

neo4j_uri = input("Neo4j URI (press Enter for default): ").strip()
if not neo4j_uri:
    neo4j_uri = "neo4j+s://5b8df33f.databases.neo4j.io"
    print(f"  → Using: {neo4j_uri}")

neo4j_user = input("Neo4j User (press Enter for 'neo4j'): ").strip()
if not neo4j_user:
    neo4j_user = "neo4j"
    print(f"  → Using: {neo4j_user}")

neo4j_password = getpass("Neo4j Password (hidden): ")
if not neo4j_password:
    print("❌ Neo4j password is required!")
    sys.exit(1)

google_api_key = getpass("Google AI API Key (hidden): ")
if not google_api_key:
    print("❌ Google AI API Key is required!")
    sys.exit(1)

print()
print("✅ Credentials collected!")
print()

# Set environment variables for this session only
os.environ["NEO4J_URI"] = neo4j_uri
os.environ["NEO4J_USER"] = neo4j_user
os.environ["NEO4J_PASSWORD"] = neo4j_password
os.environ["GOOGLE_AI_API_KEY"] = google_api_key

# Check if we have the chunks file already
chunks_file = Path("neo4j_chunks.json")

if chunks_file.exists():
    print("📁 Found existing neo4j_chunks.json")
    use_existing = input("Use existing file? (y/n): ").strip().lower()

    if use_existing == 'y':
        print("  → Using cached chunks file")
        with open(chunks_file) as f:
            all_chunks = json.load(f)
        print(f"  → Loaded {len(all_chunks)} chunks")
        skip_extraction = True
    else:
        skip_extraction = False
else:
    skip_extraction = False

# Import the exporter (after setting env vars)
try:
    from neo4j_to_filesearch import Neo4jToFileSearch
except ImportError as e:
    print(f"❌ Error importing neo4j_to_filesearch: {e}")
    print()
    print("Installing required packages...")
    os.system("pip install neo4j google-genai")
    from neo4j_to_filesearch import Neo4jToFileSearch

# Run the migration
try:
    print()
    print("=" * 80)
    print("STARTING MIGRATION")
    print("=" * 80)
    print()

    exporter = Neo4jToFileSearch()

    if skip_extraction:
        # Skip extraction, just upload
        print("Skipping extraction, uploading existing chunks...")
        print()
        print("=" * 80)
        print("Uploading to Google File Search...")
        print("-" * 80)

        store_name = exporter.upload_to_file_search(all_chunks)

        print()
        print("=" * 80)
        print("MIGRATION COMPLETE!")
        print("=" * 80)
        print()
        print(f"📊 Summary:")
        print(f"  • Total chunks uploaded: {len(all_chunks)}")
        print(f"  • File Search store: {store_name}")
        print()
        print("✅ Larry Navigator can now access this knowledge!")

    else:
        # Full extraction and upload
        exporter.run_full_export()

    exporter.close()

except KeyboardInterrupt:
    print()
    print("⚠️ Migration interrupted by user")
    sys.exit(1)
except Exception as e:
    print()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("🎉 ALL DONE!")
print("=" * 80)
