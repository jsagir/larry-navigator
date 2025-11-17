#!/usr/bin/env python3
"""
Larry Navigator - Build File Search Store with PWS Content
Creates Gemini File Search store and uploads chunks with metadata
"""

import json
import os
import sys
import time
from pathlib import Path
from google import genai
from google.genai import types

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Configuration
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
CHUNKS_FILE = "pws_chunks.json"
STORE_NAME = "larry-pws-navigator"

if not GOOGLE_AI_API_KEY:
    print("✗ Error: GOOGLE_AI_API_KEY not found!")
    print("Please create a .env file with your API key:")
    print("  GOOGLE_AI_API_KEY=your-api-key-here")
    print("\nGet your API key from: https://aistudio.google.com/apikey")
    sys.exit(1)

def create_file_search_store(client):
    """Create a new File Search store for Larry"""
    print("📦 Creating File Search store: '{}'".format(STORE_NAME))

    try:
        file_search_store = client.file_search_stores.create(
            config={'display_name': STORE_NAME}
        )
        print(f"✓ Created store: {file_search_store.name}")
        return file_search_store
    except Exception as e:
        print(f"✗ Error creating store: {e}")
        # Try to get existing store
        print("  Checking for existing stores...")
        try:
            stores = list(client.file_search_stores.list())
            for store in stores:
                if STORE_NAME in store.display_name:
                    print(f"✓ Found existing store: {store.name}")
                    return store
        except:
            pass
        raise

def prepare_chunks_as_documents(chunks_file):
    """Convert chunks into document format for upload"""
    print(f"\n📄 Loading chunks from {chunks_file}...")

    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print(f"✓ Loaded {len(chunks)} chunks")

    # Group chunks by lecture for better organization
    lectures = {}
    for chunk in chunks:
        lecture = chunk.get('lecture_number') or chunk.get('fileName', 'Unknown')
        if lecture not in lectures:
            lectures[lecture] = []
        lectures[lecture].append(chunk)

    print(f"✓ Organized into {len(lectures)} lecture groups")

    # Create documents (combine chunks into lecture documents)
    documents = []
    for lecture_name, lecture_chunks in lectures.items():
        # Sort chunks by position
        lecture_chunks.sort(key=lambda x: x.get('position', 0))

        # Combine chunk content
        combined_content = "\n\n".join([
            f"[Chunk {c.get('position', 0)}]\n{c['content']}"
            for c in lecture_chunks
        ])

        # Get metadata from first chunk
        meta = lecture_chunks[0]

        document = {
            'name': lecture_name,
            'content': combined_content,
            'metadata': {
                'lecture_number': meta.get('lecture_number', 'Unknown'),
                'title': meta.get('title', lecture_name),
                'week': str(meta.get('week', 0)),
                'complexity': meta.get('complexity', 'unknown'),
                'personas': ','.join(meta.get('personas', [])),
                'problem_types': ','.join(meta.get('problem_types', [])),
                'frameworks': ','.join(meta.get('frameworks', [])),
                'chunk_count': str(len(lecture_chunks)),
            }
        }
        documents.append(document)

    return documents

def upload_documents_to_store(client, file_search_store, documents):
    """Upload documents to File Search store"""
    print(f"\n📤 Uploading {len(documents)} documents to store...")

    uploaded_count = 0
    failed = []

    for i, doc in enumerate(documents, 1):
        try:
            print(f"\n  [{i}/{len(documents)}] Uploading: {doc['name'][:50]}...")

            # Create a temporary text file for this document
            filename = f"temp_{doc['name'].replace('/', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(doc['content'])

            # Upload with metadata
            operation = client.file_search_stores.upload_to_file_search_store(
                file=filename,
                file_search_store_name=file_search_store.name,
                config={
                    'display_name': doc['name'],
                    'custom_metadata': [
                        {"key": k, "string_value": v}
                        for k, v in doc['metadata'].items()
                    ]
                }
            )

            # Wait for completion (with timeout)
            timeout = 60  # 60 seconds
            start_time = time.time()
            while not operation.done and (time.time() - start_time) < timeout:
                time.sleep(2)
                operation = client.operations.get(operation)

            if operation.done:
                print(f"    ✓ Uploaded successfully")
                uploaded_count += 1
            else:
                print(f"    ✗ Timeout waiting for upload")
                failed.append(doc['name'])

            # Clean up temp file
            import os
            try:
                os.remove(filename)
            except:
                pass

        except Exception as e:
            print(f"    ✗ Error: {e}")
            failed.append(doc['name'])

    print(f"\n✓ Upload complete: {uploaded_count}/{len(documents)} successful")
    if failed:
        print(f"✗ Failed uploads: {len(failed)}")
        for name in failed[:5]:
            print(f"  - {name}")

    return uploaded_count

def save_store_info(file_search_store):
    """Save store information for later use"""
    store_info = {
        'store_name': file_search_store.name,
        'display_name': STORE_NAME,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    with open('larry_store_info.json', 'w') as f:
        json.dump(store_info, f, indent=2)

    print(f"\n✓ Saved store info to larry_store_info.json")
    return store_info

def main():
    print("=" * 80)
    print("LARRY NAVIGATOR - BUILDING FILE SEARCH STORE")
    print("=" * 80)
    print()

    # Initialize client
    print("🔧 Initializing Google AI client...")
    client = genai.Client(api_key=GOOGLE_AI_API_KEY)
    print("✓ Client initialized")

    # Create store
    file_search_store = create_file_search_store(client)

    # Prepare documents
    documents = prepare_chunks_as_documents(CHUNKS_FILE)

    # Upload documents
    uploaded_count = upload_documents_to_store(client, file_search_store, documents)

    # Save store info
    store_info = save_store_info(file_search_store)

    print("\n" + "=" * 80)
    print("LARRY'S BRAIN IS READY!")
    print("=" * 80)
    print(f"Store Name: {store_info['store_name']}")
    print(f"Documents: {uploaded_count} uploaded")
    print(f"Total Chunks: 1136 PWS content chunks")
    print()
    print("Next: Run larry_chatbot.py to start chatting!")
    print("=" * 80)

if __name__ == "__main__":
    main()
