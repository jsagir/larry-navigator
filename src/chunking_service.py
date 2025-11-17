#!/usr/bin/env python3
"""
Production Chunking Service
Following Gemini File Search best practices:
- ~1000 words per chunk
- Proper overlap for context continuity
- Preserves document structure
- Rich metadata for retrieval
"""

import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import tiktoken

@dataclass
class PWS_Chunk:
    """Production-ready chunk with complete metadata"""
    id: str
    content: str
    word_count: int
    token_count: int

    # Source information
    source_file_name: str
    source_position: int

    # Chunk metadata
    chunk_index: int
    has_overlap: bool

    # Document classification
    doc_type: str  # lecture, textbook, framework, tool, syllabus, reference, example
    chunk_type: str  # slide, section, paragraph, concept, week, case_study

    # Rich metadata for retrieval
    metadata: Dict[str, Any]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ChunkingService:
    """
    Production chunking service implementing File Search best practices

    Key Features:
    - ~1000 words per chunk (optimal for retrieval)
    - 200-word overlap for context continuity
    - Document-type-aware strategies
    - Preserves semantic boundaries
    - Rich metadata for graph-like relationships
    """

    # Best practices from Gemini File Search guide
    TARGET_WORDS = 1000
    OVERLAP_WORDS = 200
    WORDS_TO_TOKENS_RATIO = 1.3

    def __init__(self):
        """Initialize chunking service with tiktoken encoder"""
        self.encoder = None
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        except Exception as e1:
            # Fallback to basic encoding
            try:
                self.encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e2:
                # If both fail, use word-count estimation
                print(f"⚠️  tiktoken encoder unavailable - using word-count estimation")
                self.encoder = None

    def chunk_document(
        self,
        content: str,
        file_name: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Main chunking method - routes to appropriate strategy

        Args:
            content: Full document text
            file_name: Source filename
            metadata: Base metadata to enrich

        Returns:
            List of optimally chunked PWS_Chunk objects
        """
        print(f"  📝 Chunking: {file_name}")

        # Detect document type
        doc_type = self._detect_doc_type(file_name)

        # Route to appropriate chunking strategy
        if doc_type == 'lecture':
            chunks = self._chunk_lecture(content, file_name, metadata)
        elif doc_type == 'textbook':
            chunks = self._chunk_textbook(content, file_name, metadata)
        elif doc_type == 'syllabus':
            chunks = self._chunk_syllabus(content, file_name, metadata)
        else:
            chunks = self._chunk_generic(content, file_name, metadata)

        avg_words = sum(c.word_count for c in chunks) / len(chunks) if chunks else 0
        print(f"     ✓ Created {len(chunks)} chunks (avg {int(avg_words)} words/chunk)")

        return chunks

    def _chunk_lecture(
        self,
        content: str,
        file_name: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Lecture chunking strategy
        - Preserves slide boundaries
        - ~1000 words per chunk
        - Maintains logical flow
        """
        chunks = []

        # Split by slide markers (double newlines or slide numbers)
        slides = [s.strip() for s in re.split(r'\n\n+|\r\n\r\n+', content) if s.strip()]

        current_chunk = ''
        current_words = 0
        chunk_index = 0

        for i, slide in enumerate(slides):
            slide_words = self._count_words(slide)

            # Check if adding this slide exceeds target
            if current_words + slide_words > self.TARGET_WORDS and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk(
                    content=current_chunk,
                    file_name=file_name,
                    chunk_index=chunk_index,
                    has_overlap=chunk_index > 0,
                    doc_type='lecture',
                    chunk_type='slide',
                    metadata=metadata
                ))
                chunk_index += 1

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.OVERLAP_WORDS)
                current_chunk = f"{overlap_text}\n\n{slide}" if overlap_text else slide
                current_words = self._count_words(current_chunk)
            else:
                # Add to current chunk
                current_chunk = f"{current_chunk}\n\n{slide}" if current_chunk else slide
                current_words += slide_words

        # Save final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                content=current_chunk,
                file_name=file_name,
                chunk_index=chunk_index,
                has_overlap=chunk_index > 0,
                doc_type='lecture',
                chunk_type='slide',
                metadata=metadata
            ))

        return chunks

    def _chunk_textbook(
        self,
        content: str,
        file_name: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Textbook chunking strategy
        - Preserves sections/chapters
        - ~1000 words per chunk
        - Maintains hierarchical structure
        """
        chunks = []

        # Extract sections
        sections = self._extract_sections(content)

        for i, section in enumerate(sections):
            section_title = section['title']
            section_content = section['content']
            section_words = self._count_words(section_content)

            # Section fits in one chunk (allow 20% overflow)
            if section_words <= self.TARGET_WORDS * 1.2:
                chunks.append(self._create_chunk(
                    content=section_content,
                    file_name=file_name,
                    chunk_index=i,
                    has_overlap=False,
                    doc_type='textbook',
                    chunk_type='section',
                    metadata={**metadata, 'section_title': section_title}
                ))
            else:
                # Split large section with overlap
                sub_chunks = self._split_large_text(
                    text=section_content,
                    file_name=file_name,
                    start_index=i * 100,
                    doc_type='textbook',
                    chunk_type='section',
                    metadata={**metadata, 'section_title': section_title}
                )
                chunks.extend(sub_chunks)

        return chunks

    def _chunk_syllabus(
        self,
        content: str,
        file_name: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Syllabus chunking strategy
        - One chunk per week
        - Preserves weekly structure
        """
        chunks = []

        # Split by week markers
        week_pattern = re.compile(r'(Week\s+\d+|WEEK\s+\d+|Weeks?\s+\d+-\d+)', re.IGNORECASE)
        parts = week_pattern.split(content)

        # Combine headers with content
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                week_header = parts[i]
                week_content = parts[i + 1].strip()

                if week_content:
                    # Extract week number
                    week_num_match = re.search(r'\d+', week_header)
                    week_number = int(week_num_match.group()) if week_num_match else 0

                    full_content = f"{week_header}\n\n{week_content}"

                    chunks.append(self._create_chunk(
                        content=full_content,
                        file_name=file_name,
                        chunk_index=(i - 1) // 2,
                        has_overlap=False,
                        doc_type='syllabus',
                        chunk_type='week',
                        metadata={
                            **metadata,
                            'week': week_number,
                            'week_title': week_header
                        }
                    ))

        return chunks

    def _chunk_generic(
        self,
        content: str,
        file_name: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Generic chunking strategy
        - Sliding window with overlap
        - Preserves paragraph boundaries
        """
        doc_type = self._detect_doc_type(file_name)
        return self._split_large_text(
            text=content,
            file_name=file_name,
            start_index=0,
            doc_type=doc_type,
            chunk_type='paragraph',
            metadata=metadata
        )

    def _split_large_text(
        self,
        text: str,
        file_name: str,
        start_index: int,
        doc_type: str,
        chunk_type: str,
        metadata: Dict[str, Any]
    ) -> List[PWS_Chunk]:
        """
        Split large text with sliding window and overlap

        Strategy:
        - Split by paragraphs (semantic boundaries)
        - Build chunks up to ~1000 words
        - Add 200-word overlap for context
        """
        chunks = []
        paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]

        current_chunk = ''
        current_words = 0
        chunk_index = start_index

        for paragraph in paragraphs:
            paragraph_words = self._count_words(paragraph)

            # Check if adding paragraph exceeds target
            if current_words + paragraph_words > self.TARGET_WORDS and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk(
                    content=current_chunk,
                    file_name=file_name,
                    chunk_index=chunk_index,
                    has_overlap=chunk_index > start_index,
                    doc_type=doc_type,
                    chunk_type=chunk_type,
                    metadata=metadata
                ))
                chunk_index += 1

                # Create new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.OVERLAP_WORDS)
                current_chunk = f"{overlap_text}\n\n{paragraph}" if overlap_text else paragraph
                current_words = self._count_words(current_chunk)
            else:
                # Add to current chunk
                current_chunk = f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph
                current_words += paragraph_words

        # Save final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                content=current_chunk,
                file_name=file_name,
                chunk_index=chunk_index,
                has_overlap=chunk_index > start_index,
                doc_type=doc_type,
                chunk_type=chunk_type,
                metadata=metadata
            ))

        return chunks

    def _create_chunk(
        self,
        content: str,
        file_name: str,
        chunk_index: int,
        has_overlap: bool,
        doc_type: str,
        chunk_type: str,
        metadata: Dict[str, Any]
    ) -> PWS_Chunk:
        """Create chunk object with all metadata"""
        word_count = self._count_words(content)
        token_count = self._count_tokens(content)

        # Generate unique ID
        chunk_id = f"{file_name}_chunk_{chunk_index}_{uuid.uuid4().hex[:8]}"

        return PWS_Chunk(
            id=chunk_id,
            content=content,
            word_count=word_count,
            token_count=token_count,
            source_file_name=file_name,
            source_position=chunk_index,
            chunk_index=chunk_index,
            has_overlap=has_overlap,
            doc_type=doc_type,
            chunk_type=chunk_type,
            metadata={
                'title': metadata.get('title', file_name),
                'file_name': file_name,
                'doc_type': doc_type,
                **metadata
            }
        )

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from structured content"""
        sections = []

        # Match section patterns
        section_pattern = re.compile(
            r'^(Chapter\s+\d+|Section\s+\d+\.?\d*|^\d+\.[\s\w]+)',
            re.MULTILINE | re.IGNORECASE
        )

        matches = list(section_pattern.finditer(content))

        if not matches:
            return [{'title': 'Full Document', 'content': content}]

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            sections.append({
                'title': match.group(0).strip(),
                'content': section_content
            })

        return sections

    def _get_overlap_text(self, text: str, target_words: int) -> str:
        """Get overlap text from end of chunk"""
        # Split into sentences
        sentences = [s.strip() + '.' for s in re.split(r'[.!?]+', text) if s.strip()]

        overlap = ''
        words = 0

        # Work backwards to build overlap
        for sentence in reversed(sentences):
            sentence_words = self._count_words(sentence)

            if words + sentence_words > target_words:
                break

            overlap = sentence + ' ' + overlap
            words += sentence_words

        return overlap.strip()

    def _detect_doc_type(self, file_name: str) -> str:
        """Detect document type from filename"""
        if re.match(r'^N\d+_', file_name):
            return 'lecture'
        if 'PWS_INNOVATION_BOOK' in file_name or 'Extended Research' in file_name:
            return 'textbook'
        if 'Syllabus' in file_name:
            return 'syllabus'
        if re.search(r'Beautiful Question|mINTO', file_name):
            return 'reference'
        if re.search(r'NATO|case', file_name, re.IGNORECASE):
            return 'example'
        if re.search(r'framework|theory', file_name, re.IGNORECASE):
            return 'framework'
        if re.search(r'tool|method', file_name, re.IGNORECASE):
            return 'tool'
        return 'reference'

    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.strip().split())

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        if self.encoder:
            try:
                return len(self.encoder.encode(text))
            except Exception:
                pass
        # Fallback: estimate tokens from word count
        return int(self._count_words(text) * self.WORDS_TO_TOKENS_RATIO)

    def __del__(self):
        """Cleanup encoder"""
        if hasattr(self, 'encoder'):
            try:
                self.encoder.free()
            except:
                pass
