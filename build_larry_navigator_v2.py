#!/usr/bin/env python3
"""
Larry Navigator - Build File Search Store (Updated for Production Chunks)
Creates Gemini File Search store and uploads production chunks with rich metadata
"""

import json
import time
import os
from google import genai
from google.genai import types

# Configuration
GOOGLE_AI_API_KEY = "AIzaSyC6miH5hbQeBHYVORXLJra0CCS1NMRp_TE"
CHUNKS_FILE = "pws_chunks.json"
STORE_NAME = "larry-pws-navigator-v2"

def create_file_search_store(client):
    """Create a new File Search store for Larry"""
    print(f"📦 Creating File Search store: '{STORE_NAME}'")

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

def load_production_chunks(chunks_file):
    """Load production chunks from pws_chunks.json"""
    print(f"\n📄 Loading production chunks from {chunks_file}...")

    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print(f"✓ Loaded {len(chunks)} production chunks")

    # Group by source file for organized upload
    files = {}
    for chunk in chunks:
        source = chunk.get('source_file_name', 'Unknown')
        if source not in files:
            files[source] = []
        files[source].append(chunk)

    print(f"✓ Organized into {len(files)} source files")

    return chunks, files

def prepare_documents_for_upload(chunks, files):
    """Prepare chunks as documents for File Search"""
    print(f"\n📝 Preparing {len(files)} documents for upload...")

    documents = []

    for source_file, file_chunks in files.items():
        # Sort by chunk index
        file_chunks.sort(key=lambda x: x.get('chunk_index', 0))

        # Combine all chunks for this file
        combined_content = "\n\n---\n\n".join([
            f"[Chunk {c.get('chunk_index')}]\n{c['content']}"
            for c in file_chunks
        ])

        # Extract metadata from first chunk
        first_chunk = file_chunks[0]
        metadata = first_chunk.get('metadata', {})

        # Build metadata for File Search
        search_metadata = {
            'source_file': source_file,
            'doc_type': first_chunk.get('doc_type', 'unknown'),
            'chunk_count': str(len(file_chunks)),
            'total_words': str(sum(c.get('word_count', 0) for c in file_chunks)),
            'total_tokens': str(sum(c.get('token_count', 0) for c in file_chunks)),
        }

        # Add lecture metadata if available
        if 'lecture_id' in metadata:
            search_metadata['lecture_id'] = metadata['lecture_id']
            search_metadata['lecture_number'] = metadata.get('lecture_number', '')
            search_metadata['week'] = str(metadata.get('week', ''))
            search_metadata['difficulty'] = metadata.get('difficulty', '')

        # Add problem types
        problem_types = metadata.get('problem_types', [])
        if problem_types:
            search_metadata['problem_types'] = ','.join(problem_types)

        # Add frameworks
        frameworks = metadata.get('frameworks_mentioned', [])
        if frameworks:
            search_metadata['frameworks'] = ','.join(frameworks[:5])  # Limit to 5

        # Add tools
        tools = metadata.get('tools_introduced', [])
        if tools:
            search_metadata['tools'] = ','.join(tools[:5])

        # Add title
        search_metadata['title'] = metadata.get('title', source_file)

        document = {
            'name': source_file,
            'content': combined_content,
            'metadata': search_metadata
        }

        documents.append(document)

    print(f"✓ Prepared {len(documents)} documents")
    return documents

def upload_documents_to_store(client, file_search_store, documents):
    """Upload documents to File Search store"""
    print(f"\n📤 Uploading {len(documents)} documents to store...")
    print("   (This may take a few minutes...)\n")

    uploaded_count = 0
    failed = []

    for i, doc in enumerate(documents, 1):
        try:
            doc_name = doc['name']
            print(f"  [{i}/{len(documents)}] {doc_name[:50]}...", end=' ', flush=True)

            # Create temporary text file
            temp_filename = f"temp_{doc_name.replace('/', '_').replace(' ', '_')}.txt"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(doc['content'])

            # Upload to File Search store
            operation = client.file_search_stores.upload_to_file_search_store(
                file=temp_filename,
                file_search_store_name=file_search_store.name,
                config={
                    'display_name': doc_name,
                    'custom_metadata': [
                        {"key": k, "string_value": v}
                        for k, v in doc['metadata'].items()
                    ]
                }
            )

            # Wait for completion
            timeout = 60
            start_time = time.time()
            while not operation.done and (time.time() - start_time) < timeout:
                time.sleep(2)
                operation = client.operations.get(operation)

            if operation.done:
                print("✓")
                uploaded_count += 1
            else:
                print("✗ Timeout")
                failed.append(doc_name)

            # Clean up temp file
            try:
                os.remove(temp_filename)
            except:
                pass

        except Exception as e:
            print(f"✗ Error: {e}")
            failed.append(doc['name'])

    print(f"\n✓ Upload complete: {uploaded_count}/{len(documents)} successful")

    if failed:
        print(f"\n⚠️  Failed uploads ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")

    return uploaded_count

def save_store_info(file_search_store, uploaded_count, total_chunks):
    """Save store information for chatbot"""
    store_info = {
        'store_name': file_search_store.name,
        'display_name': STORE_NAME,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'file_count': uploaded_count,
        'total_chunks': total_chunks,
        'status': 'active'
    }

    output_file = 'larry_store_info.json'
    with open(output_file, 'w') as f:
        json.dump(store_info, f, indent=2)

    print(f"\n✓ Saved store info to {output_file}")
    return store_info

def main():
    print("=" * 80)
    print("LARRY NAVIGATOR - BUILDING FILE SEARCH STORE (V2)")
    print("=" * 80)
    print()

    # Check if chunks file exists
    if not os.path.exists(CHUNKS_FILE):
        print(f"❌ Error: {CHUNKS_FILE} not found!")
        print("   Run: python3 generate_pws_chunks.py --sample")
        return

    # Initialize client
    print("🔧 Initializing Google AI client...")
    try:
        client = genai.Client(api_key=GOOGLE_AI_API_KEY)
        print("✓ Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("   Check your API key in the script")
        return

    try:
        # Load chunks
        chunks, files = load_production_chunks(CHUNKS_FILE)

        # Create File Search store
        file_search_store = create_file_search_store(client)

        # Prepare documents
        documents = prepare_documents_for_upload(chunks, files)

        # Upload documents
        uploaded_count = upload_documents_to_store(client, file_search_store, documents)

        # Save store info
        store_info = save_store_info(file_search_store, uploaded_count, len(chunks))

        # Success summary
        print("\n" + "=" * 80)
        print("✅ LARRY'S KNOWLEDGE BASE IS READY!")
        print("=" * 80)
        print(f"Store Name: {store_info['store_name']}")
        print(f"Documents Uploaded: {uploaded_count}")
        print(f"Total Chunks: {len(chunks)}")
        print(f"Status: {store_info['status']}")
        print()
        print("📊 Statistics:")
        total_words = sum(c.get('word_count', 0) for c in chunks)
        total_tokens = sum(c.get('token_count', 0) for c in chunks)
        print(f"  - Total words: {total_words:,}")
        print(f"  - Total tokens: {total_tokens:,}")
        print(f"  - Avg words/chunk: {total_words // len(chunks)}")
        print()
        print("🚀 Next Steps:")
        print("  1. Run: python3 larry_with_knowledge.py")
        print("  2. Ask Larry about PWS topics!")
        print("  3. Test with questions from EDGE_CASE_TESTS.md")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  - Check internet connection")
        print("  - Verify API key is valid")
        print("  - Check pws_chunks.json format")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
