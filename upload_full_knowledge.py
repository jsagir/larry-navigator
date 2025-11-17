#!/usr/bin/env python3
"""
Upload Full Larry Knowledge Base to File Search
2,988 chunks (~2.66M words) with relationship metadata
"""

import os
import json
import time
from pathlib import Path
from google import genai
from google.genai import types

def load_env():
    """Load environment variables from .env file"""
    env_path = Path.home() / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def main():
    print("=" * 80)
    print("🚀 LARRY FULL KNOWLEDGE BASE UPLOADER")
    print("=" * 80)

    # Load environment
    load_env()
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_AI_API_KEY not found in .env file")
        return

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Load store info
    store_info_path = Path("/home/jsagi/larry_store_info.json")
    with open(store_info_path) as f:
        store_info = json.load(f)

    store_name = store_info['store_name']
    print(f"\n📦 Using File Search store: {store_name}")

    # Load chunks
    chunks_file = Path("/home/jsagi/larry_full_knowledge_chunks.json")
    print(f"\n📂 Loading chunks from {chunks_file.name}...")

    with open(chunks_file) as f:
        chunks = json.load(f)

    print(f"  ✅ Loaded {len(chunks):,} chunks")
    print(f"  📊 Total words: {sum(len(chunk['content'].split()) for chunk in chunks):,}")

    # Upload chunks
    print(f"\n📤 Uploading {len(chunks):,} chunks to File Search...")
    print("=" * 80)

    successful = 0
    failed = 0
    temp_files = []

    for idx, chunk in enumerate(chunks, 1):
        try:
            # Create temporary text file for this chunk
            chunk_file = Path(f"/tmp/larry_chunk_{chunk['chunk_id'][:12]}.txt")
            temp_files.append(chunk_file)

            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk['content'])

            # Prepare metadata (File Search API v2 format)
            metadata_dict = {
                'source_file': chunk.get('source_file', ''),
                'document_type': chunk.get('document_type', ''),
                'chunk_position': str(chunk.get('chunk_position', 0)),
                'total_chunks': str(chunk.get('total_chunks', 0)),
                'problem_types': ','.join(chunk.get('problem_types', [])),
                'frameworks': ','.join(chunk.get('frameworks', []))[:500],  # Truncate if too long
                'difficulty': chunk.get('difficulty', 'intermediate'),
                'is_prior_art': 'true' if chunk.get('is_prior_art', False) else 'false',
                'topic_cluster': chunk.get('topic_cluster', ''),
            }

            # Remove empty values
            metadata_dict = {k: v for k, v in metadata_dict.items() if v and v != 'None'}

            # Convert to File Search metadata format
            custom_metadata = [
                {"key": k, "string_value": v}
                for k, v in metadata_dict.items()
            ]

            # Upload to File Search
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(chunk_file),
                file_search_store_name=store_name,
                config={
                    'display_name': f"{chunk['source_file']} (chunk {chunk['chunk_position']})",
                    'custom_metadata': custom_metadata
                }
            )

            successful += 1

            # Progress indicator
            if idx % 10 == 0 or idx == len(chunks):
                percentage = (idx / len(chunks)) * 100
                print(f"  Progress: {idx}/{len(chunks)} ({percentage:.0f}%) - {successful} successful, {failed} failed")

            # Rate limiting - pause every 50 uploads
            if idx % 50 == 0:
                print(f"  ⏸️  Pausing for rate limit...")
                time.sleep(2)

            # Clean up temp file
            chunk_file.unlink(missing_ok=True)

        except Exception as e:
            failed += 1
            print(f"  ❌ Error uploading chunk {idx}: {str(e)[:100]}")
            # Clean up temp file on error
            if chunk_file.exists():
                chunk_file.unlink(missing_ok=True)

    # Final cleanup
    print("\n🧹 Cleaning up temporary files...")
    for temp_file in temp_files:
        temp_file.unlink(missing_ok=True)

    print("=" * 80)
    print("\n✅ Upload complete!")
    print(f"  Successful: {successful:,}")
    print(f"  Failed: {failed}")

    # Update store info
    store_info['total_chunks'] = successful + int(store_info.get('total_chunks', 0))
    store_info['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')

    with open(store_info_path, 'w') as f:
        json.dump(store_info, f, indent=2)

    print(f"\n💾 Updated {store_info_path.name}")
    print(f"\n🎯 Larry now has access to {store_info['total_chunks']:,} knowledge chunks!")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
