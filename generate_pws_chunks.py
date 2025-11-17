#!/usr/bin/env python3
"""
Generate pws_chunks.json with Production Chunking

This script:
1. Extracts documents from Neo4j (or uses sample data)
2. Applies optimal chunking strategy (~1000 words)
3. Enriches with comprehensive metadata
4. Generates pws_chunks.json for File Search

Usage:
    python3 generate_pws_chunks.py [--neo4j] [--sample]

Options:
    --neo4j     Extract from Neo4j database
    --sample    Generate sample chunks (no Neo4j required)
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from chunking_service import ChunkingService, PWS_Chunk
from metadata_enricher import MetadataEnricher


class PWS_ChunkGenerator:
    """Generates production-ready PWS knowledge chunks"""

    def __init__(self):
        self.chunking_service = ChunkingService()
        self.metadata_enricher = MetadataEnricher()
        self.chunks: List[PWS_Chunk] = []

    def generate_from_neo4j(self):
        """Extract from Neo4j and generate chunks"""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("❌ neo4j-driver not installed")
            print("   Install: pip install neo4j-driver")
            return False

        # Neo4j connection (update with your credentials)
        URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        USERNAME = os.getenv('NEO4J_USER', 'neo4j')
        PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

        print(f"🔌 Connecting to Neo4j: {URI}")

        try:
            driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

            with driver.session() as session:
                # Get all documents
                result = session.run("""
                    MATCH (c:Chunk)
                    WHERE c.fileName IS NOT NULL
                    RETURN DISTINCT c.fileName as fileName,
                           collect(c) as chunks
                    ORDER BY fileName
                """)

                documents = []
                for record in result:
                    file_name = record['fileName']
                    neo4j_chunks = record['chunks']

                    # Combine chunks into full content
                    sorted_chunks = sorted(neo4j_chunks, key=lambda c: c.get('position', 0))
                    full_content = '\n\n'.join([
                        c.get('content', '') for c in sorted_chunks
                    ])

                    documents.append({
                        'fileName': file_name,
                        'content': full_content,
                        'chunkCount': len(neo4j_chunks)
                    })

                print(f"✅ Extracted {len(documents)} documents from Neo4j")

                # Process documents
                self._process_documents(documents)

            driver.close()
            return True

        except Exception as e:
            print(f"❌ Neo4j error: {e}")
            print("   Tip: Update credentials in script or use --sample mode")
            return False

    def generate_sample_chunks(self):
        """Generate sample chunks without Neo4j"""
        print("📝 Generating sample PWS chunks...")

        # Sample lecture content
        sample_documents = self._get_sample_documents()

        self._process_documents(sample_documents)

        print(f"✅ Generated {len(self.chunks)} sample chunks")

    def _process_documents(self, documents: List[Dict[str, Any]]):
        """Process documents and generate chunks"""
        print(f"\n📚 Processing {len(documents)} documents...\n")

        for doc in documents:
            file_name = doc['fileName']
            content = doc['content']

            print(f"📄 {file_name}")

            # Enrich metadata
            if file_name.startswith('N'):
                metadata = self.metadata_enricher.enrich_lecture(file_name, content)
            elif 'PWS' in file_name or 'Extended' in file_name:
                metadata = self.metadata_enricher.enrich_textbook(file_name)
            else:
                metadata = {'title': file_name, 'file_name': file_name}

            # Chunk with optimal strategy
            document_chunks = self.chunking_service.chunk_document(
                content=content,
                file_name=file_name,
                metadata=metadata
            )

            self.chunks.extend(document_chunks)

        print(f"\n✅ Total chunks generated: {len(self.chunks)}")

    def save_chunks(self, output_path: str = 'pws_chunks.json'):
        """Save chunks to JSON file"""
        print(f"\n💾 Saving chunks to {output_path}...")

        # Convert chunks to dictionaries
        chunks_data = [chunk.to_dict() for chunk in self.chunks]

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)

        # Print statistics
        total_words = sum(c.word_count for c in self.chunks)
        total_tokens = sum(c.token_count for c in self.chunks)
        avg_words = total_words / len(self.chunks) if self.chunks else 0
        avg_tokens = total_tokens / len(self.chunks) if self.chunks else 0

        print(f"\n📊 Chunk Statistics:")
        print(f"   ├─ Total chunks: {len(self.chunks):,}")
        print(f"   ├─ Total words: {total_words:,}")
        print(f"   ├─ Total tokens: {total_tokens:,}")
        print(f"   ├─ Avg words/chunk: {int(avg_words)}")
        print(f"   └─ Avg tokens/chunk: {int(avg_tokens)}")

        # Document type breakdown
        doc_types = {}
        for chunk in self.chunks:
            dt = chunk.doc_type
            doc_types[dt] = doc_types.get(dt, 0) + 1

        print(f"\n📁 Document Types:")
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   ├─ {doc_type}: {count}")

        print(f"\n✅ Saved to: {output_path}")

    def _get_sample_documents(self) -> List[Dict[str, Any]]:
        """Get sample PWS documents for testing"""
        return [
            {
                'fileName': 'N01_Introduction',
                'content': """
Framework for Innovation

Creative Destruction and Innovation

Creative destruction is a concept introduced by economist Joseph Schumpeter to describe the process of industrial mutation that incessantly revolutionizes the economic structure from within, incessantly destroying the old one, incessantly creating a new one. This process is the essential fact about capitalism.

Innovation vs. Invention

It's crucial to distinguish between innovation and invention. Invention is the creation of a new idea or concept. Innovation is the transformation of that invention into a commercial reality - bringing it to market and creating value.

Innovation Types

There are several types of innovation:
1. Incremental Innovation - Small, continuous improvements
2. Radical Innovation - Breakthrough changes that transform markets
3. Disruptive Innovation - New market entrants that eventually overtake incumbents
4. Architectural Innovation - Reconfiguring existing technologies in new ways

Entrepreneurship and Opportunity Recognition

Entrepreneurs are individuals who recognize opportunities and marshal resources to pursue them. Opportunity recognition involves:
- Identifying unmet needs
- Recognizing market gaps
- Understanding emerging trends
- Connecting disparate ideas

The Innovation Imperative

In today's rapidly changing world, innovation is not optional - it's essential for survival. Companies that fail to innovate become obsolete, replaced by more agile competitors who better serve customer needs.
""",
                'chunkCount': 1
            },
            {
                'fileName': 'N02_UnDefined_Problems',
                'content': """
Un-defined Problems

What are Un-defined Problems?

Un-defined problems are characterized by high uncertainty about both the problem itself and potential solutions. The future is unclear, and we don't even know what questions to ask yet.

These problems require exploration and sense-making before any solution can be proposed. They often involve emerging technologies, societal changes, or unprecedented situations.

Scenario Analysis

Scenario analysis is a structured method for thinking about the future. Instead of trying to predict one future, we develop multiple plausible scenarios and prepare for each.

Steps in Scenario Analysis:
1. Identify focal question or decision
2. Identify critical uncertainties
3. Develop scenario logics
4. Flesh out scenarios with details
5. Identify implications and options
6. Select leading indicators to monitor

Trending to Absurd

This technique involves taking current trends and extrapolating them to extreme conclusions. By pushing trends to their logical (or illogical) extremes, we can:
- Identify potential disruptions
- Challenge assumptions
- Reveal weak signals
- Generate novel ideas

Example: If online shopping continues to grow, what happens when 100% of retail is online? What second-order effects emerge?

Nested Hierarchies

Un-defined problems often exist within nested systems. Understanding the hierarchy helps us:
- Zoom in and out between levels
- Identify leverage points
- Recognize interdependencies
- Avoid solving the wrong problem

Red Teaming

Red teaming involves challenging plans and assumptions by taking an adversarial perspective. This helps identify:
- Blind spots in thinking
- Unstated assumptions
- Vulnerabilities in strategies
- Alternative interpretations of evidence

Beautiful Questions

Warren Berger's concept of "beautiful questions" emphasizes the power of inquiry in un-defined problem spaces. Instead of rushing to solutions, we should:
- Ask "Why?" to understand root causes
- Ask "What if?" to explore possibilities
- Ask "How?" to develop actionable paths

Tools for Un-defined Problems

Key tools include:
- Scenario planning
- Trend analysis
- Weak signal detection
- Futures studies methodologies
- Strategic foresight techniques

Case Study: COVID-19 Pandemic

The COVID-19 pandemic was an un-defined problem for most organizations. Nobody knew:
- How long it would last
- What the health impacts would be
- How societies would respond
- What the economic consequences would be

Organizations that used scenario planning were better prepared to adapt quickly as events unfolded.
""",
                'chunkCount': 1
            },
            {
                'fileName': 'N03_IllDefined_Problems',
                'content': """
Ill-defined Problems

Characteristics of Ill-defined Problems

Ill-defined problems have some structure, but significant ambiguity remains. We know there's an opportunity or challenge, but the boundaries are fuzzy and multiple solution paths exist.

These problems require both search (finding the right problem to solve) and solution development.

Extensive vs. Intensive Searching

Two complementary approaches:

Extensive Searching:
- Cast a wide net
- Explore many possibilities
- Look across domains
- Identify patterns and trends
- Generate many options

Intensive Searching:
- Deep dive into specific areas
- Understand nuances
- Develop expertise
- Test assumptions
- Refine specific solutions

Jobs-to-be-Done Framework

Clayton Christensen's Jobs-to-be-Done (JTBD) framework helps identify ill-defined opportunities by focusing on what customers are "hiring" products to do.

Key principles:
- People don't want products, they want progress
- Jobs are stable over time
- Solutions change, but jobs remain
- Competition comes from anything hired for the same job

Famous example: McDonald's milkshake study revealed customers were "hiring" milkshakes for a boring morning commute, not for nutrition or taste.

Diffusion of Innovation

Everett Rogers' diffusion theory explains how innovations spread through populations:

1. Innovators (2.5%) - First to adopt
2. Early Adopters (13.5%) - Opinion leaders
3. Early Majority (34%) - Deliberate adopters
4. Late Majority (34%) - Skeptical adopters
5. Laggards (16%) - Last to adopt

Understanding diffusion helps identify:
- Target customer segments
- Adoption barriers
- Messaging strategies
- Scaling challenges

Finding Opportunities in Ill-defined Spaces

Strategies include:
- Observing customer struggles
- Identifying "workarounds"
- Looking for compensating behaviors
- Studying non-consumption
- Exploring adjacent markets

Trend Analysis

Analyzing trends helps identify ill-defined opportunities:
- Demographic shifts
- Technological changes
- Regulatory changes
- Economic trends
- Social movements

The key is connecting trends to create unique insights.

Case Study: Airbnb

Airbnb solved an ill-defined problem. They didn't invent the concept of renting rooms, but they recognized:
- Conference attendees needed affordable lodging
- Homeowners had spare rooms
- Trust was the barrier
- Technology could solve the trust problem

By deeply understanding the "job" (affordable, authentic accommodations) and the enabling trends (smartphone adoption, social media), they created a multi-billion dollar market.
""",
                'chunkCount': 1
            },
            {
                'fileName': 'N07_WellDefined_Problems',
                'content': """
Well-defined Problems

Characteristics

Well-defined problems have:
- Clear problem statements
- Known solution approaches
- Measurable success criteria
- Defined constraints
- Established best practices

These are execution challenges, not discovery challenges.

Lean Startup Methodology

Eric Ries' Lean Startup approach is ideal for well-defined problems:

Build-Measure-Learn Loop:
1. Build a minimum viable product (MVP)
2. Measure how customers respond
3. Learn from data
4. Iterate or pivot

Key principles:
- Validated learning over opinions
- Small batches for fast feedback
- Actionable metrics over vanity metrics
- Continuous deployment

Minimum Viable Product (MVP)

An MVP is the smallest version of a product that allows you to test a specific hypothesis with real customers.

MVP is NOT:
- A low-quality product
- A prototype
- A beta version

MVP IS:
- A learning tool
- Hypothesis-driven
- Customer-focused
- Iterative

The Mom Test

Rob Fitzpatrick's Mom Test helps validate well-defined problems by asking better customer questions:

Bad questions:
- "Would you use this product?"
- "How much would you pay?"
- "What features do you want?"

Good questions:
- "How do you currently solve this problem?"
- "What have you tried before?"
- "Walk me through the last time this was an issue"

The rule: Don't ask anyone whether your business is a good idea, because they're likely to lie.

Validation Techniques

For well-defined problems:
- Customer interviews
- Landing page tests
- Concierge MVPs
- Wizard of Oz tests
- Smoke tests
- Pre-orders

Pirate Metrics (AARRR)

Dave McClure's framework for measuring startup success:

- Acquisition: How do users find you?
- Activation: Do they have a great first experience?
- Retention: Do they come back?
- Revenue: Can you monetize?
- Referral: Do they tell others?

Case Study: Dropbox

Dropbox faced a well-defined problem: file synchronization. They used:
- Explainer video as MVP (measured signups)
- Beta program (measured usage)
- Referral program (measured viral growth)
- Freemium model (measured conversion)

By systematically validating each hypothesis, they built a multi-billion dollar company.

Execution Excellence

With well-defined problems, success comes from:
- Fast iteration
- Data-driven decisions
- Customer focus
- Operational efficiency
- Continuous improvement
""",
                'chunkCount': 1
            },
            {
                'fileName': 'PWS_INNOVATION_BOOK',
                'content': """
Problems Worth Solving: A Systematic Approach to Innovation

Introduction

This book presents a comprehensive framework for identifying, analyzing, and solving problems worth solving. The methodology distinguishes between different problem types and provides specific tools for each.

The Problem Typology

Problems can be classified along two dimensions:
1. Problem definition clarity
2. Solution space clarity

This creates a matrix of problem types:
- Un-defined: Unknown problem, unknown solution
- Ill-defined: Emerging problem, multiple solutions
- Well-defined: Clear problem, known solution approach
- Wicked: Unsolvable problems with no clear endpoint

Each type requires different approaches, tools, and mindsets.

The Innovation Process

Innovation is not random or magical. It follows a systematic process:

1. Problem Discovery
   - Identify opportunities
   - Classify problem type
   - Understand context

2. Problem Definition
   - Frame correctly
   - Identify constraints
   - Clarify success criteria

3. Solution Development
   - Generate options
   - Test hypotheses
   - Iterate rapidly

4. Implementation
   - Execute efficiently
   - Measure results
   - Scale systematically

Core Frameworks

The book integrates multiple frameworks:
- Creative Destruction (Schumpeter)
- Disruptive Innovation (Christensen)
- Diffusion Theory (Rogers)
- Lean Startup (Ries)
- Jobs-to-be-Done (Christensen)
- Design Thinking (IDEO)
- Three Box Solution (Govindarajan)

Each framework applies to specific problem types and contexts.

Organizational Innovation

Building innovative organizations requires:
- Portfolio approach to projects
- Ambidextrous structures
- Experimental culture
- Customer focus
- Continuous learning

The Three Box Solution helps organizations balance:
- Box 1: Managing the present
- Box 2: Selectively forgetting the past
- Box 3: Creating the future

Measuring Innovation

Innovation metrics vary by problem type:

Un-defined:
- Number of scenarios developed
- Weak signals identified
- Strategic options created

Ill-defined:
- Market opportunities discovered
- Customer needs validated
- Trends analyzed

Well-defined:
- MVPs tested
- Validated learnings
- Customer acquisition cost
- Lifetime value

Practical Tools

The PWS toolkit includes:
- Scenario analysis templates
- Customer interview guides
- Validation frameworks
- Trend analysis tools
- Portfolio mapping
- Business model canvas
- Value proposition design

Case Studies

The book includes detailed case studies:
- Kodak vs. Fujifilm (managing disruption)
- Netflix evolution (continuous innovation)
- Airbnb creation (identifying opportunities)
- Tesla's approach (systems thinking)
- Amazon's culture (customer obsession)

Conclusion

Problems worth solving are everywhere. The key is developing the mindset and skillset to:
- Recognize opportunities
- Frame problems correctly
- Apply appropriate tools
- Execute systematically
- Learn continuously

Innovation is not about having great ideas - it's about solving real problems that create value.
""",
                'chunkCount': 1
            }
        ]


def main():
    """Main execution"""
    print("=" * 80)
    print("PWS CHUNK GENERATOR - Production Chunking System")
    print("=" * 80)
    print()

    # Parse arguments
    use_neo4j = '--neo4j' in sys.argv
    use_sample = '--sample' in sys.argv

    if not use_neo4j and not use_sample:
        print("Usage: python3 generate_pws_chunks.py [--neo4j] [--sample]")
        print()
        print("Options:")
        print("  --neo4j    Extract from Neo4j database")
        print("  --sample   Generate sample chunks (no Neo4j required)")
        print()
        print("Defaulting to --sample mode...")
        print()
        use_sample = True

    # Generate chunks
    generator = PWS_ChunkGenerator()

    if use_neo4j:
        success = generator.generate_from_neo4j()
        if not success:
            print("\n⚠️  Falling back to sample mode...")
            generator.generate_sample_chunks()
    else:
        generator.generate_sample_chunks()

    # Save to file
    output_path = 'pws_chunks.json'
    generator.save_chunks(output_path)

    print("\n" + "=" * 80)
    print("✅ PWS CHUNKS GENERATED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review pws_chunks.json")
    print("  2. Run: python3 build_larry_navigator.py")
    print("  3. Start chatbot: python3 larry_with_knowledge.py")
    print()


if __name__ == '__main__':
    main()
