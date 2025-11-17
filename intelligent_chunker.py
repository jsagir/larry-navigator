#!/usr/bin/env python3
"""
Intelligent Document Chunker for Larry Navigator
Implements Google File Search best practices:
- ~1000 word chunks
- 200 word overlap
- Rich metadata extraction
- Document type detection
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# Document type detection patterns
PROBLEM_TYPES = {
    'un-defined': ['un-defined', 'undefined', 'discovery', 'exploration', 'search space'],
    'ill-defined': ['ill-defined', 'wicked elements', 'ambiguous', 'fuzzy'],
    'well-defined': ['well-defined', 'clear requirements', 'optimization', 'execution'],
    'wicked': ['wicked problem', 'complex system', 'stakeholder conflict', 'no clear solution']
}

FRAMEWORKS = [
    'Three Box Solution', 'Scenario Analysis', 'TRIZ', 'Jobs-to-be-Done', 'Mom Test',
    'Trending to Absurd', 'Beautiful Questions', 'Red Teaming', 'Nested Hierarchies',
    'Extensive Search', 'Intensive Search', 'Lateral Thinking', 'Creative Destruction',
    'Disruptive Innovation', 'Minto Pyramid', 'Portfolio Management'
]

TOOLS = [
    'Beautiful Questions', 'Jobs-to-be-Done', 'Mom Test', 'Trending to Absurd',
    'Red Teaming', 'Scenario Analysis', 'TRIZ', 'Lateral Thinking'
]

@dataclass
class Chunk:
    """Represents a properly chunked document segment"""
    chunk_id: str
    content: str
    source_file: str
    document_type: str
    chunk_position: int
    total_chunks: int

    # PWS-specific metadata
    lecture_number: str = None
    week: int = 0
    topic: str = None
    problem_types: List[str] = None
    frameworks: List[str] = None
    tools: List[str] = None
    key_concepts: List[str] = None

    # Persona targeting
    personas: List[str] = None
    difficulty: str = 'intermediate'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        # Convert lists to ensure JSON compatibility
        for key in ['problem_types', 'frameworks', 'tools', 'key_concepts', 'personas']:
            if d[key] is None:
                d[key] = []
        return d

class IntelligentChunker:
    """Smart document chunker following Google File Search best practices"""

    def __init__(self, target_words=1000, overlap_words=200):
        self.target_words = target_words
        self.overlap_words = overlap_words
        self.min_words = 500
        self.max_words = 1500

    def read_document(self, file_path: Path) -> str:
        """Read document content based on file type"""
        suffix = file_path.suffix.lower()

        if suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif suffix == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                print(f"⚠️ python-docx not installed, skipping {file_path}")
                return ""
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                return ""
        elif suffix == '.pdf':
            print(f"⚠️ PDF parsing not implemented yet for {file_path}")
            return ""
        else:
            print(f"⚠️ Unsupported file type: {suffix}")
            return ""

    def detect_document_type(self, file_path: Path) -> str:
        """Detect document type from filename and location"""
        path_str = str(file_path).lower()

        if 'lecture' in path_str or '.pptx' in path_str or any(f'n{i:02d}' in path_str for i in range(1, 11)):
            return 'lecture'
        elif 'framework' in path_str or 'minto' in path_str:
            return 'framework'
        elif 'notes' in path_str or 'innovation_book' in path_str:
            return 'textbook'
        elif any(prob in path_str for prob in ['un defined', 'ill-defined', 'well-defined', 'wicked']):
            return 'problem_type_doc'
        else:
            return 'general'

    def extract_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract PWS-specific metadata from content"""
        metadata = {
            'problem_types': [],
            'frameworks': [],
            'tools': [],
            'key_concepts': [],
            'personas': ['student'],  # Default
            'difficulty': 'intermediate',
            'lecture_number': None,
            'week': 0,
            'topic': file_path.stem
        }

        content_lower = content.lower()

        # Detect problem types
        for prob_type, keywords in PROBLEM_TYPES.items():
            if any(kw in content_lower for kw in keywords):
                metadata['problem_types'].append(prob_type)

        # Detect frameworks
        for framework in FRAMEWORKS:
            if framework.lower() in content_lower:
                metadata['frameworks'].append(framework)

        # Detect tools
        for tool in TOOLS:
            if tool.lower() in content_lower:
                metadata['tools'].append(tool)

        # Extract lecture number from filename
        filename = file_path.name.upper()
        lecture_match = re.search(r'N(\d+)', filename)
        if lecture_match:
            metadata['lecture_number'] = f"N{lecture_match.group(1)}"
            metadata['week'] = int(lecture_match.group(1))

        # Detect personas
        if any(word in content_lower for word in ['startup', 'entrepreneur', 'venture', 'founder']):
            if 'entrepreneur' not in metadata['personas']:
                metadata['personas'].append('entrepreneur')
        if any(word in content_lower for word in ['corporate', 'company', 'organization', 'enterprise']):
            if 'corporate' not in metadata['personas']:
                metadata['personas'].append('corporate')
        if any(word in content_lower for word in ['consult', 'advise', 'facilitat']):
            if 'consultant' not in metadata['personas']:
                metadata['personas'].append('consultant')

        return metadata

    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into ~1000 word chunks with 200 word overlap"""
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            # Extract chunk of target_words
            chunk_words = words[i:i + self.target_words]

            # Create chunk text
            chunk_text = ' '.join(chunk_words)

            # Only add if chunk is substantial (> min_words)
            if len(chunk_words) >= self.min_words or i + self.target_words >= len(words):
                chunks.append(chunk_text)

            # Move forward by (target_words - overlap_words)
            i += (self.target_words - self.overlap_words)

            # Stop if we're past the end
            if i >= len(words):
                break

        return chunks if chunks else [text]  # Return full text if too small

    def generate_chunk_id(self, content: str) -> str:
        """Generate unique chunk ID using SHA-256"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def chunk_document(self, file_path: Path) -> List[Chunk]:
        """Process a document into properly sized chunks with metadata"""
        print(f"📄 Processing: {file_path.name}")

        # Read content
        content = self.read_document(file_path)
        if not content or len(content.strip()) < 100:
            print(f"  ⚠️ Skipping (empty or too small)")
            return []

        # Detect document type
        doc_type = self.detect_document_type(file_path)

        # Extract base metadata
        base_metadata = self.extract_metadata(content, file_path)

        # Split into chunks
        chunk_texts = self.split_into_chunks(content)
        total_chunks = len(chunk_texts)

        print(f"  ✅ Created {total_chunks} chunks (~{self.target_words} words each)")

        # Create Chunk objects
        chunks = []
        for idx, chunk_text in enumerate(chunk_texts, 1):
            chunk = Chunk(
                chunk_id=self.generate_chunk_id(chunk_text),
                content=chunk_text,
                source_file=file_path.name,
                document_type=doc_type,
                chunk_position=idx,
                total_chunks=total_chunks,
                **base_metadata
            )
            chunks.append(chunk)

        return chunks

    def process_directory(self, directory: Path) -> List[Chunk]:
        """Process all documents in a directory"""
        all_chunks = []

        # Supported file types
        patterns = ['**/*.txt', '**/*.docx', '**/*.pdf']

        files = []
        for pattern in patterns:
            files.extend(directory.glob(pattern))

        print(f"\n🔍 Found {len(files)} documents to process")
        print("=" * 60)

        for file_path in sorted(files):
            chunks = self.chunk_document(file_path)
            all_chunks.extend(chunks)

        print("=" * 60)
        print(f"✅ Total chunks created: {len(all_chunks)}")

        return all_chunks

    def save_chunks(self, chunks: List[Chunk], output_file: Path):
        """Save chunks to JSON file"""
        chunk_dicts = [chunk.to_dict() for chunk in chunks]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved {len(chunks)} chunks to {output_file}")

        # Print statistics
        total_words = sum(len(chunk.content.split()) for chunk in chunks)
        avg_words = total_words / len(chunks) if chunks else 0

        print(f"\n📊 CHUNKING STATISTICS:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Average chunk size: {avg_words:.0f} words")
        print(f"  Total content: {total_words:,} words")

        # Document type breakdown
        doc_types = {}
        for chunk in chunks:
            doc_types[chunk.document_type] = doc_types.get(chunk.document_type, 0) + 1

        print(f"\n📚 BY DOCUMENT TYPE:")
        for doc_type, count in sorted(doc_types.items()):
            print(f"  {doc_type}: {count} chunks")

def main():
    """Main execution"""
    print("🎯 Larry Navigator - Intelligent Document Chunker")
    print("=" * 60)

    # Configuration
    docs_dir = Path("/home/jsagi/docs")
    output_file = Path("/home/jsagi/larry_chunks_v2.json")

    # Create chunker
    chunker = IntelligentChunker(
        target_words=1000,
        overlap_words=200
    )

    # Process all documents
    chunks = chunker.process_directory(docs_dir)

    # Save results
    chunker.save_chunks(chunks, output_file)

    print("\n✅ Chunking complete!")
    print(f"📁 Output: {output_file}")

if __name__ == "__main__":
    main()
