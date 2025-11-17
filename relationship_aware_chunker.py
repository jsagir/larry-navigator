#!/usr/bin/env python3
"""
Relationship-Aware Chunker for PWS Library
Extracts content AND relationships between documents, topics, frameworks, and methods
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict

# Extended PWS knowledge taxonomy
FRAMEWORKS = [
    'Three Box Solution', 'Scenario Analysis', 'TRIZ', 'Jobs-to-be-Done', 'Mom Test',
    'Trending to Absurd', 'Beautiful Questions', 'Red Teaming', 'Nested Hierarchies',
    'Extensive Search', 'Intensive Search', 'Lateral Thinking', 'Creative Destruction',
    'Disruptive Innovation', 'Minto Pyramid', 'Portfolio Management', 'Blue Ocean Strategy',
    'Design Thinking', 'Lean Startup', 'Agile Innovation', 'Open Innovation'
]

METHODS = [
    'Brainstorming', 'Mind Mapping', 'SCAMPER', 'Six Thinking Hats', 'Fishbone Diagram',
    'Five Whys', 'Customer Journey Mapping', 'Value Proposition Canvas', 'Business Model Canvas',
    'Empathy Mapping', 'Persona Development', 'A/B Testing', 'Rapid Prototyping'
]

PROBLEM_TYPES = ['un-defined', 'ill-defined', 'well-defined', 'wicked']

AUTHORS = [
    'Clayton Christensen', 'Peter Drucker', 'Eric Ries', 'Steve Blank', 'Geoffrey Moore',
    'Rita McGrath', 'Vijay Govindarajan', 'Kim & Mauborgne', 'Tim Brown', 'Alex Osterwalder'
]

@dataclass
class RelationshipMetadata:
    """Tracks relationships between chunks and topics"""
    references: List[str] = field(default_factory=list)  # Other docs referenced
    cited_by: List[str] = field(default_factory=list)  # Docs that cite this
    related_frameworks: List[str] = field(default_factory=list)
    related_methods: List[str] = field(default_factory=list)
    related_problem_types: List[str] = field(default_factory=list)
    authors_mentioned: List[str] = field(default_factory=list)
    topic_cluster: str = None  # Main topic cluster
    subtopics: List[str] = field(default_factory=list)

@dataclass
class EnhancedChunk:
    """Chunk with relationship metadata"""
    chunk_id: str
    content: str
    source_file: str
    document_type: str
    chunk_position: int
    total_chunks: int

    # Basic PWS metadata
    problem_types: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    personas: List[str] = field(default_factory=list)
    difficulty: str = 'intermediate'

    # Relationship metadata
    relationships: RelationshipMetadata = field(default_factory=RelationshipMetadata)

    # Prior art specific
    is_prior_art: bool = False
    book_title: str = None
    author: str = None
    publication_year: int = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON"""
        d = asdict(self)
        # Flatten relationships for File Search metadata
        if d['relationships']:
            d['references'] = ','.join(d['relationships'].get('references', []))
            d['related_frameworks'] = ','.join(d['relationships'].get('related_frameworks', []))
            d['related_methods'] = ','.join(d['relationships'].get('related_methods', []))
            d['authors_mentioned'] = ','.join(d['relationships'].get('authors_mentioned', []))
            d['topic_cluster'] = d['relationships'].get('topic_cluster', '')
        return d

class RelationshipAwareChunker:
    """Advanced chunker that extracts content and relationships"""

    def __init__(self, target_words=1000, overlap_words=200):
        self.target_words = target_words
        self.overlap_words = overlap_words
        self.document_graph = defaultdict(set)  # Doc -> Related docs
        self.topic_graph = defaultdict(set)  # Topic -> Related topics
        self.all_chunks = []

    def detect_document_type(self, file_path: Path) -> str:
        """Enhanced document type detection"""
        path_str = str(file_path).lower()
        name = file_path.name.lower()

        # Prior art detection
        if any(keyword in path_str for keyword in ['book', 'prior-art', 'reference', 'library']):
            return 'prior_art'

        # Academic paper
        if any(ext in path_str for ext in ['.pdf']) and 'paper' in path_str:
            return 'academic_paper'

        # Framework documentation
        if any(fw.lower().replace(' ', '-') in path_str for fw in FRAMEWORKS):
            return 'framework_doc'

        # Method guide
        if any(method.lower() in path_str for method in METHODS):
            return 'method_guide'

        # Existing types
        if 'lecture' in path_str or '.pptx' in path_str:
            return 'lecture'
        elif 'notes' in path_str:
            return 'textbook'

        return 'general'

    def extract_relationships(self, content: str, file_path: Path) -> RelationshipMetadata:
        """Extract relationships from content"""
        rel = RelationshipMetadata()
        content_lower = content.lower()

        # Detect framework references
        for framework in FRAMEWORKS:
            if framework.lower() in content_lower:
                rel.related_frameworks.append(framework)

        # Detect method references
        for method in METHODS:
            if method.lower() in content_lower:
                rel.related_methods.append(method)

        # Detect problem type references
        for prob_type in PROBLEM_TYPES:
            if prob_type in content_lower:
                rel.related_problem_types.append(prob_type)

        # Detect author mentions
        for author in AUTHORS:
            if author.lower() in content_lower:
                rel.authors_mentioned.append(author)

        # Detect citations (look for patterns like "see X", "according to Y", "ref: Z")
        citation_patterns = [
            r'see (?:also )?([A-Z][a-zA-Z\s]+(?:19|20)\d{2})',
            r'according to ([A-Z][a-zA-Z\s]+)',
            r'(?:ref|reference):\s*([A-Z][a-zA-Z\s]+)',
            r'\(([A-Z][a-zA-Z\s]+,?\s*(?:19|20)\d{2})\)'
        ]

        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            rel.references.extend(matches[:5])  # Limit to 5 per pattern

        # Detect topic cluster based on content
        if any(word in content_lower for word in ['discovery', 'exploration', 'search']):
            rel.topic_cluster = 'Discovery & Exploration'
        elif any(word in content_lower for word in ['validation', 'testing', 'experiment']):
            rel.topic_cluster = 'Validation & Testing'
        elif any(word in content_lower for word in ['execution', 'implementation', 'scale']):
            rel.topic_cluster = 'Execution & Scaling'
        elif any(word in content_lower for word in ['disruption', 'innovation', 'breakthrough']):
            rel.topic_cluster = 'Innovation & Disruption'
        else:
            rel.topic_cluster = 'General'

        return rel

    def extract_book_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from prior art books"""
        metadata = {}

        # Try to extract title from filename or first lines
        name = file_path.stem
        metadata['book_title'] = name.replace('_', ' ').replace('-', ' ').title()

        # Try to find author in content
        author_patterns = [
            r'by ([A-Z][a-zA-Z\s]+)',
            r'Author:\s*([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+\((?:19|20)\d{2}\)'
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content[:1000])  # Check first 1000 chars
            if match:
                metadata['author'] = match.group(1).strip()
                break

        # Try to find publication year
        year_match = re.search(r'\b(19|20)\d{2}\b', content[:2000])
        if year_match:
            metadata['publication_year'] = int(year_match.group(0))

        return metadata

    def read_document(self, file_path: Path) -> str:
        """Read document with enhanced PDF support"""
        suffix = file_path.suffix.lower()

        if suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

        elif suffix == '.md':
            # Markdown files - read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

        elif suffix == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                return ""

        elif suffix == '.pdf':
            # TODO: Add PyPDF2 or pdfplumber support
            print(f"⚠️ PDF parsing not yet implemented for {file_path}")
            return ""

        return ""

    def split_into_chunks(self, text: str) -> List[str]:
        """Split with overlap"""
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.target_words]

            if len(chunk_words) >= 500 or i + self.target_words >= len(words):
                chunks.append(' '.join(chunk_words))

            i += (self.target_words - self.overlap_words)

            if i >= len(words):
                break

        return chunks if chunks else [text]

    def chunk_document(self, file_path: Path) -> List[EnhancedChunk]:
        """Process document with relationship extraction"""
        print(f"📄 Processing: {file_path.name}")

        content = self.read_document(file_path)
        if not content or len(content.strip()) < 100:
            print(f"  ⚠️ Skipping (empty or too small)")
            return []

        doc_type = self.detect_document_type(file_path)
        is_prior_art = doc_type == 'prior_art'

        # Extract relationships
        relationships = self.extract_relationships(content, file_path)

        # Extract book metadata if prior art
        book_meta = {}
        if is_prior_art:
            book_meta = self.extract_book_metadata(content, file_path)

        # Split into chunks
        chunk_texts = self.split_into_chunks(content)
        total_chunks = len(chunk_texts)

        print(f"  ✅ Created {total_chunks} chunks")
        print(f"     Type: {doc_type}")
        if relationships.related_frameworks:
            print(f"     Frameworks: {', '.join(relationships.related_frameworks[:3])}")
        if relationships.authors_mentioned:
            print(f"     Authors: {', '.join(relationships.authors_mentioned[:3])}")

        # Create chunks
        chunks = []
        for idx, chunk_text in enumerate(chunk_texts, 1):
            chunk = EnhancedChunk(
                chunk_id=hashlib.sha256(chunk_text.encode()).hexdigest(),
                content=chunk_text,
                source_file=file_path.name,
                document_type=doc_type,
                chunk_position=idx,
                total_chunks=total_chunks,
                problem_types=relationships.related_problem_types,
                frameworks=relationships.related_frameworks,
                personas=['student', 'entrepreneur', 'consultant'],
                relationships=relationships,
                is_prior_art=is_prior_art,
                **book_meta
            )
            chunks.append(chunk)

        return chunks

    def process_directory(self, directory: Path) -> List[EnhancedChunk]:
        """Process all documents and build relationship graph"""
        all_chunks = []

        patterns = ['**/*.txt', '**/*.md', '**/*.docx', '**/*.pdf']
        files = []
        for pattern in patterns:
            files.extend(directory.glob(pattern))

        # Filter out metadata files
        files = [f for f in files if 'Zone.Identifier' not in str(f)]

        print(f"\n🔍 Found {len(files)} documents to process")
        print("=" * 60)

        for file_path in sorted(files):
            chunks = self.chunk_document(file_path)
            all_chunks.extend(chunks)

        print("=" * 60)
        print(f"✅ Total chunks created: {len(all_chunks)}")

        # Build relationship statistics
        self.analyze_relationships(all_chunks)

        return all_chunks

    def analyze_relationships(self, chunks: List[EnhancedChunk]):
        """Analyze and print relationship statistics"""
        print(f"\n📊 RELATIONSHIP ANALYSIS:")

        # Topic clusters
        clusters = defaultdict(int)
        for chunk in chunks:
            if chunk.relationships.topic_cluster:
                clusters[chunk.relationships.topic_cluster] += 1

        print(f"\n🏷️  Topic Clusters:")
        for cluster, count in sorted(clusters.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cluster}: {count} chunks")

        # Most referenced frameworks
        framework_counts = defaultdict(int)
        for chunk in chunks:
            for fw in chunk.frameworks:
                framework_counts[fw] += 1

        print(f"\n🔧 Most Referenced Frameworks:")
        for fw, count in sorted(framework_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {fw}: {count} mentions")

        # Author mentions
        author_counts = defaultdict(int)
        for chunk in chunks:
            for author in chunk.relationships.authors_mentioned:
                author_counts[author] += 1

        print(f"\n📚 Most Mentioned Authors:")
        for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {author}: {count} mentions")

    def save_chunks(self, chunks: List[EnhancedChunk], output_file: Path):
        """Save chunks with relationships"""
        chunk_dicts = [chunk.to_dict() for chunk in chunks]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved {len(chunks)} chunks to {output_file}")

        # Statistics
        total_words = sum(len(chunk.content.split()) for chunk in chunks)
        avg_words = total_words / len(chunks) if chunks else 0
        prior_art_count = sum(1 for chunk in chunks if chunk.is_prior_art)

        print(f"\n📊 FINAL STATISTICS:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Average chunk size: {avg_words:.0f} words")
        print(f"  Total content: {total_words:,} words")
        print(f"  Prior art chunks: {prior_art_count}")
        print(f"  Course material chunks: {len(chunks) - prior_art_count}")

def main():
    """Main execution"""
    print("🎯 PWS Library - Relationship-Aware Chunker")
    print("=" * 60)

    # Configuration
    library_dir = Path("/home/jsagi/pws-library")
    output_file = Path("/home/jsagi/pws_library_chunks.json")

    if not library_dir.exists():
        print(f"❌ Error: {library_dir} not found!")
        print("\nPlease copy the PWS library to this location:")
        print(f"  {library_dir}")
        return

    # Create chunker
    chunker = RelationshipAwareChunker(
        target_words=1000,
        overlap_words=200
    )

    # Process all documents
    chunks = chunker.process_directory(library_dir)

    # Save results
    chunker.save_chunks(chunks, output_file)

    print("\n✅ Relationship-aware chunking complete!")
    print(f"📁 Output: {output_file}")

if __name__ == "__main__":
    main()
