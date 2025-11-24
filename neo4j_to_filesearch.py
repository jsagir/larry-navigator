#!/usr/bin/env python3
"""
Neo4j to File Search Exporter
Extracts content from Neo4j and uploads to Google File Search for Larry Navigator
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from neo4j import GraphDatabase
from google import genai
from google.genai import types

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

CHUNKS_OUTPUT_FILE = "neo4j_chunks.json"
STORE_INFO_FILE = "larry_store_info.json"


class Neo4jToFileSearch:
    """Extract content from Neo4j and upload to File Search"""

    def __init__(self):
        """Initialize connections to Neo4j and Google AI"""
        if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
            raise ValueError(
                "Missing Neo4j credentials. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD"
            )

        if not GOOGLE_AI_API_KEY:
            raise ValueError("Missing GOOGLE_AI_API_KEY")

        # Initialize Neo4j
        print(f"Connecting to Neo4j at {NEO4J_URI}...")
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

        # Initialize Google AI
        print("Initializing Google AI client...")
        self.genai_client = genai.Client(api_key=GOOGLE_AI_API_KEY)

        # Test connections
        self._test_connections()

    def _test_connections(self):
        """Test Neo4j and Google AI connections"""
        # Test Neo4j
        with self.driver.session() as session:
            result = session.run("RETURN 1 as test")
            assert result.single()["test"] == 1
        print("✓ Neo4j connection successful")

    def close(self):
        """Close connections"""
        if self.driver:
            self.driver.close()

    def extract_document_chunks(self) -> List[Dict[str, Any]]:
        """
        Extract DocumentChunk nodes from Neo4j with all metadata

        Returns chunks suitable for File Search upload
        """
        query = """
        MATCH (chunk:DocumentChunk)
        OPTIONAL MATCH (chunk)-[:DISCUSSES]->(concept:Concept)
        OPTIONAL MATCH (chunk)-[:REFERENCES]->(fw:Framework)
        OPTIONAL MATCH (chunk)-[:PART_OF]->(doc:Document)
        OPTIONAL MATCH (chunk)-[:ADDRESSES]->(pt:ProblemType)

        RETURN
            chunk.chunk_id AS chunk_id,
            chunk.content AS content,
            chunk.source_file AS source_file,
            chunk.document_type AS document_type,
            chunk.chunk_position AS chunk_position,
            chunk.total_chunks AS total_chunks,

            // Metadata
            chunk.problem_types AS problem_types,
            chunk.frameworks AS frameworks,
            chunk.tools AS tools,
            chunk.key_concepts AS key_concepts,
            chunk.personas AS personas,
            chunk.difficulty AS difficulty,

            // Prior art metadata
            chunk.is_prior_art AS is_prior_art,
            chunk.book_title AS book_title,
            chunk.author AS author,
            chunk.publication_year AS publication_year,

            // Relationship metadata
            chunk.references AS references,
            chunk.related_frameworks AS related_frameworks,
            chunk.related_methods AS related_methods,
            chunk.authors_mentioned AS authors_mentioned,
            chunk.topic_cluster AS topic_cluster,

            // Connected nodes
            collect(DISTINCT concept.name) AS connected_concepts,
            collect(DISTINCT fw.name) AS connected_frameworks,
            collect(DISTINCT pt.name) AS connected_problem_types

        ORDER BY chunk.source_file, chunk.chunk_position
        """

        chunks = []
        with self.driver.session() as session:
            results = session.run(query)

            for record in results:
                chunk = {
                    "chunk_id": record["chunk_id"],
                    "content": record["content"],
                    "metadata": {
                        "source_file": record["source_file"],
                        "document_type": record["document_type"],
                        "chunk_position": record["chunk_position"],
                        "total_chunks": record["total_chunks"],

                        # PWS metadata
                        "problem_types": record["problem_types"] or [],
                        "frameworks": record["frameworks"] or [],
                        "tools": record["tools"] or [],
                        "key_concepts": record["key_concepts"] or [],
                        "personas": record["personas"] or [],
                        "difficulty": record["difficulty"] or "intermediate",

                        # Prior art
                        "is_prior_art": record["is_prior_art"] or False,
                        "book_title": record["book_title"],
                        "author": record["author"],
                        "publication_year": record["publication_year"],

                        # Relationships
                        "references": record["references"],
                        "related_frameworks": record["related_frameworks"],
                        "related_methods": record["related_methods"],
                        "authors_mentioned": record["authors_mentioned"],
                        "topic_cluster": record["topic_cluster"],

                        # Connected via relationships
                        "connected_concepts": [c for c in record["connected_concepts"] if c],
                        "connected_frameworks": [f for f in record["connected_frameworks"] if f],
                        "connected_problem_types": [p for p in record["connected_problem_types"] if p],
                    }
                }
                chunks.append(chunk)

        return chunks

    def extract_frameworks(self) -> List[Dict[str, Any]]:
        """Extract Framework nodes as additional context"""
        query = """
        MATCH (fw:Framework)
        OPTIONAL MATCH (fw)-[:ADDRESSES]->(pt:ProblemType)
        OPTIONAL MATCH (p:Persona)-[:USES]->(fw)
        OPTIONAL MATCH (a:Author)-[:CREATED]->(fw)

        RETURN
            fw.name AS name,
            fw.description AS description,
            fw.difficulty AS difficulty,
            fw.time_required AS time_required,
            fw.team_size AS team_size,
            collect(DISTINCT pt.name) AS problem_types,
            collect(DISTINCT p.name) AS personas,
            collect(DISTINCT a.name) AS authors
        """

        chunks = []
        with self.driver.session() as session:
            results = session.run(query)

            for record in results:
                chunk_content = f"""# Framework: {record['name']}

{record['description']}

**Difficulty:** {record['difficulty']}
**Time Required:** {record['time_required']}
**Team Size:** {record['team_size']}

**Addresses Problem Types:** {', '.join(record['problem_types'])}
**Used by Personas:** {', '.join(record['personas'])}
**Created by:** {', '.join(record['authors'])}
"""

                chunk = {
                    "chunk_id": f"framework_{record['name'].lower().replace(' ', '_')}",
                    "content": chunk_content,
                    "metadata": {
                        "source_file": "neo4j_frameworks",
                        "document_type": "framework",
                        "frameworks": [record['name']],
                        "problem_types": record['problem_types'],
                        "personas": record['personas'],
                        "difficulty": record['difficulty'],
                        "is_prior_art": False
                    }
                }
                chunks.append(chunk)

        return chunks

    def extract_case_studies(self) -> List[Dict[str, Any]]:
        """Extract CaseStudy nodes"""
        query = """
        MATCH (cs:CaseStudy)
        OPTIONAL MATCH (cs)-[:DEMONSTRATES]->(fw:Framework)
        OPTIONAL MATCH (cs)-[:INVOLVES]->(c:Company)

        RETURN
            cs.id AS id,
            cs.title AS title,
            cs.description AS description,
            cs.outcome AS outcome,
            cs.industry AS industry,
            cs.success_level AS success_level,
            collect(DISTINCT fw.name) AS frameworks,
            collect(DISTINCT c.name) AS companies
        """

        chunks = []
        with self.driver.session() as session:
            results = session.run(query)

            for record in results:
                chunk_content = f"""# Case Study: {record['title']}

**Industry:** {record['industry']}
**Companies:** {', '.join(record['companies'])}

## Description
{record['description']}

## Outcome
{record['outcome']}

**Success Level:** {record['success_level']}
**Demonstrates Frameworks:** {', '.join(record['frameworks'])}
"""

                chunk = {
                    "chunk_id": f"case_{record['id']}",
                    "content": chunk_content,
                    "metadata": {
                        "source_file": "neo4j_case_studies",
                        "document_type": "case_study",
                        "frameworks": record['frameworks'],
                        "industry": record['industry'],
                        "is_prior_art": False
                    }
                }
                chunks.append(chunk)

        return chunks

    def save_chunks_to_file(self, chunks: List[Dict[str, Any]], filename: str):
        """Save chunks to JSON file"""
        print(f"\nSaving {len(chunks)} chunks to {filename}...")
        with open(filename, 'w') as f:
            json.dump(chunks, f, indent=2)
        print(f"✓ Saved to {filename}")

    def upload_to_file_search(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Upload chunks to Google File Search

        Returns: File Search store name
        """
        print(f"\nUploading {len(chunks)} chunks to File Search...")

        # Create a File Search store
        try:
            # Check if store already exists
            if os.path.exists(STORE_INFO_FILE):
                with open(STORE_INFO_FILE, 'r') as f:
                    store_info = json.load(f)
                    store_name = store_info.get('store_name')
                    print(f"Using existing store: {store_name}")
            else:
                # Create new store
                print("Creating new File Search store...")
                store = self.genai_client.files.create_file_search_store(
                    display_name="Larry Navigator Knowledge Base"
                )
                store_name = store.name
                print(f"✓ Created store: {store_name}")

            # Upload chunks as files
            print(f"\nUploading chunks...")
            uploaded_files = []

            # Group chunks into reasonable-sized batches
            # File Search works better with multiple files than one huge file
            batch_size = 50  # 50 chunks per file

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_num = i // batch_size + 1

                # Create a combined document for this batch
                combined_content = "\n\n---\n\n".join([
                    f"# Chunk ID: {chunk['chunk_id']}\n\n{chunk['content']}"
                    for chunk in batch
                ])

                # Upload as a file
                file_path = f"/tmp/larry_batch_{batch_num}.txt"
                with open(file_path, 'w') as f:
                    f.write(combined_content)

                upload_result = self.genai_client.files.upload(
                    file=file_path,
                    config=types.UploadFileConfig(display_name=f"Larry Knowledge Batch {batch_num}")
                )

                # Add to store
                self.genai_client.files.add_files_to_file_search_store(
                    file_search_store_name=store_name,
                    file_names=[upload_result.name]
                )

                uploaded_files.append(upload_result.name)
                print(f"  ✓ Uploaded batch {batch_num} ({len(batch)} chunks)")

            print(f"\n✓ Uploaded {len(uploaded_files)} files to File Search store")

            # Save store info
            store_info = {
                'store_name': store_name,
                'total_chunks': len(chunks),
                'total_files': len(uploaded_files),
                'created_at': str(Path.cwd())
            }

            with open(STORE_INFO_FILE, 'w') as f:
                json.dump(store_info, f, indent=2)

            print(f"✓ Store info saved to {STORE_INFO_FILE}")

            return store_name

        except Exception as e:
            print(f"✗ Upload failed: {e}")
            raise

    def run_full_export(self):
        """Run complete export process"""
        print("=" * 80)
        print("NEO4J TO FILE SEARCH EXPORTER")
        print("=" * 80)
        print()

        # Extract from Neo4j
        print("Step 1: Extracting content from Neo4j...")
        print("-" * 80)

        all_chunks = []

        print("\n1.1: Extracting DocumentChunk nodes...")
        doc_chunks = self.extract_document_chunks()
        print(f"  ✓ Extracted {len(doc_chunks)} document chunks")
        all_chunks.extend(doc_chunks)

        print("\n1.2: Extracting Framework nodes...")
        fw_chunks = self.extract_frameworks()
        print(f"  ✓ Extracted {len(fw_chunks)} framework chunks")
        all_chunks.extend(fw_chunks)

        print("\n1.3: Extracting CaseStudy nodes...")
        case_chunks = self.extract_case_studies()
        print(f"  ✓ Extracted {len(case_chunks)} case study chunks")
        all_chunks.extend(case_chunks)

        print(f"\n✓ Total chunks extracted: {len(all_chunks)}")

        # Save to file
        print("\n" + "=" * 80)
        print("Step 2: Saving chunks to file...")
        print("-" * 80)
        self.save_chunks_to_file(all_chunks, CHUNKS_OUTPUT_FILE)

        # Upload to File Search
        print("\n" + "=" * 80)
        print("Step 3: Uploading to Google File Search...")
        print("-" * 80)
        store_name = self.upload_to_file_search(all_chunks)

        # Summary
        print("\n" + "=" * 80)
        print("EXPORT COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"  • Total chunks: {len(all_chunks)}")
        print(f"  • Saved to: {CHUNKS_OUTPUT_FILE}")
        print(f"  • File Search store: {store_name}")
        print(f"  • Store info: {STORE_INFO_FILE}")
        print(f"\n✓ Larry Navigator is now ready to use this knowledge base!")
        print(f"\nNext: Run larry_app.py or larry_chatbot.py to test it.")


def main():
    """Main execution"""
    try:
        exporter = Neo4jToFileSearch()
        exporter.run_full_export()
        exporter.close()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
