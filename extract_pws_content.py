#!/usr/bin/env python3
"""
Extract PWS content from Neo4j for Larry Navigator
Extracts chunks, lectures, frameworks, tools, and metadata
"""

from neo4j import GraphDatabase
import json
import re

URI = "neo4j+s://5b8df33f.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "ukfioEbJ2JLqM_8bulME166CJ5zLJdSO5uEucuvYky8"

class PWSContentExtractor:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    def close(self):
        self.driver.close()

    def extract_lecture_number(self, filename):
        """Extract lecture number from filename like 'N01_Introduction.pptx.txt'"""
        match = re.search(r'N(\d+)', filename)
        return match.group(0) if match else None

    def infer_problem_types(self, filename):
        """Infer problem types from filename"""
        filename_lower = filename.lower()
        problem_types = []

        if 'undefined' in filename_lower or 'n02' in filename_lower:
            problem_types.append('un-defined')
        if 'illdefined' in filename_lower or 'n03' in filename_lower:
            problem_types.append('ill-defined')
        if 'welldefined' in filename_lower or 'well-defined' in filename_lower or 'n07' in filename_lower:
            problem_types.append('well-defined')
        if 'wicked' in filename_lower or 'n04' in filename_lower:
            problem_types.append('wicked')

        return problem_types

    def infer_metadata_from_lecture(self, filename):
        """Infer rich metadata from lecture filename"""
        lecture_metadata = {
            "N01": {
                "title": "Introduction to Innovation",
                "week": 1,
                "complexity": "foundational",
                "personas": ["student", "entrepreneur"],
                "key_concepts": ["Innovation vs Invention", "PWS Framework", "Problems Worth Solving"],
                "frameworks": ["PWS Methodology"],
            },
            "N02": {
                "title": "Un-Defined Problems",
                "week": 2,
                "complexity": "foundational",
                "personas": ["student", "entrepreneur", "corporate"],
                "key_concepts": ["Un-defined problems", "Long-term uncertainty", "Exploration"],
                "frameworks": ["Problem Typology", "Trending to Absurd", "Scenario Analysis"],
                "problem_types": ["un-defined"],
            },
            "N03": {
                "title": "Ill-Defined Problems",
                "week": 3,
                "complexity": "intermediate",
                "personas": ["student", "entrepreneur"],
                "key_concepts": ["Ill-defined problems", "Problem framing", "Discovery"],
                "problem_types": ["ill-defined"],
            },
            "N04": {
                "title": "Wicked Problems",
                "week": 4,
                "complexity": "intermediate",
                "personas": ["student", "corporate", "consultant"],
                "key_concepts": ["Wicked problems", "No clear solution", "Stakeholder conflicts"],
                "frameworks": ["Wicked Problem Framework"],
                "problem_types": ["wicked"],
            },
            "N05": {
                "title": "Domains and Cross-Domain Innovation",
                "week": 5,
                "complexity": "intermediate",
                "personas": ["entrepreneur", "corporate", "consultant"],
                "key_concepts": ["Domain expertise", "Cross-pollination", "Hidden connections"],
                "frameworks": ["Domain Mapping", "Cross-Domain Innovation"],
            },
            "N06": {
                "title": "Innovation Portfolio",
                "week": 6,
                "complexity": "advanced",
                "personas": ["corporate", "consultant"],
                "key_concepts": ["Portfolio management", "Three Box Solution", "Risk allocation"],
                "frameworks": ["Three Box Solution", "Portfolio Management"],
            },
            "N07": {
                "title": "Well-Defined Problems",
                "week": 7,
                "complexity": "intermediate",
                "personas": ["student", "entrepreneur"],
                "key_concepts": ["Well-defined problems", "Clear constraints", "Optimization"],
                "frameworks": ["TRIZ", "Lateral Thinking"],
                "problem_types": ["well-defined"],
            },
            "N08": {
                "title": "Prior Art and Validation",
                "week": 8,
                "complexity": "advanced",
                "personas": ["entrepreneur", "researcher"],
                "key_concepts": ["Prior art search", "Validation", "Mom Test"],
            },
            "N10": {
                "title": "January Term Projects",
                "week": 10,
                "complexity": "advanced",
                "personas": ["student"],
                "key_concepts": ["Applied projects", "Real-world application"],
            },
        }

        lecture_num = self.extract_lecture_number(filename)
        return lecture_metadata.get(lecture_num, {
            "title": filename,
            "week": 0,
            "complexity": "unknown",
            "personas": ["student"],
            "key_concepts": [],
        })

    def extract_chunks_with_metadata(self):
        """Extract all DocumentChunks with rich metadata"""
        with self.driver.session() as session:
            query = """
            MATCH (dc:DocumentChunk)
            WHERE dc.has_embedding = true
            RETURN dc.id as chunk_id,
                   dc.content as content,
                   dc.fileName as fileName,
                   dc.position as position,
                   dc.chunk_type as chunk_type,
                   dc.source_file as source_file
            ORDER BY dc.fileName, dc.position
            """
            result = session.run(query)

            chunks = []
            for record in result:
                filename = record["fileName"] or record["source_file"] or "Unknown"
                lecture_num = self.extract_lecture_number(filename)
                problem_types = self.infer_problem_types(filename)
                metadata = self.infer_metadata_from_lecture(filename)

                chunk = {
                    "chunk_id": record["chunk_id"],
                    "content": record["content"],
                    "fileName": filename,
                    "position": record["position"],
                    "lecture_number": lecture_num,
                    "title": metadata.get("title", filename),
                    "week": metadata.get("week", 0),
                    "complexity": metadata.get("complexity", "unknown"),
                    "personas": metadata.get("personas", ["student"]),
                    "problem_types": problem_types or metadata.get("problem_types", []),
                    "key_concepts": metadata.get("key_concepts", []),
                    "frameworks": metadata.get("frameworks", []),
                }
                chunks.append(chunk)

            return chunks

    def get_all_frameworks(self):
        """Get all framework names"""
        with self.driver.session() as session:
            query = """
            MATCH (f:Framework)
            RETURN f.name as name
            """
            result = session.run(query)
            return [record["name"] for record in result]

    def get_all_tools(self):
        """Get all innovation tools"""
        with self.driver.session() as session:
            query = """
            MATCH (t:InnovationTool)
            RETURN t.name as name
            """
            result = session.run(query)
            return [record["name"] for record in result]

    def get_problem_types(self):
        """Get all problem types"""
        with self.driver.session() as session:
            query = """
            MATCH (pt:ProblemType)
            RETURN pt.name as name
            """
            result = session.run(query)
            return [record["name"] for record in result]

    def save_chunks_to_json(self, output_file="pws_chunks.json"):
        """Save extracted chunks to JSON file"""
        chunks = self.extract_chunks_with_metadata()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        return len(chunks)

    def get_statistics(self):
        """Get extraction statistics"""
        chunks = self.extract_chunks_with_metadata()

        stats = {
            "total_chunks": len(chunks),
            "lectures": {},
            "problem_types": set(),
            "personas": set(),
            "frameworks": set(),
        }

        for chunk in chunks:
            lecture = chunk.get("lecture_number", "Unknown")
            stats["lectures"][lecture] = stats["lectures"].get(lecture, 0) + 1

            for pt in chunk.get("problem_types", []):
                stats["problem_types"].add(pt)

            for persona in chunk.get("personas", []):
                stats["personas"].add(persona)

            for fw in chunk.get("frameworks", []):
                stats["frameworks"].add(fw)

        stats["problem_types"] = list(stats["problem_types"])
        stats["personas"] = list(stats["personas"])
        stats["frameworks"] = list(stats["frameworks"])

        return stats

def main():
    extractor = PWSContentExtractor()

    print("=" * 80)
    print("LARRY NAVIGATOR - PWS CONTENT EXTRACTION")
    print("=" * 80)
    print()

    print("📊 Extracting chunks from Neo4j...")
    count = extractor.save_chunks_to_json("pws_chunks.json")
    print(f"✓ Extracted {count} chunks to pws_chunks.json")
    print()

    print("📈 EXTRACTION STATISTICS:")
    print("-" * 80)
    stats = extractor.get_statistics()
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"\nLectures:")
    for lecture, count in sorted(stats['lectures'].items()):
        print(f"  {lecture}: {count} chunks")
    print(f"\nProblem Types: {', '.join(stats['problem_types'])}")
    print(f"Personas: {', '.join(stats['personas'])}")
    print(f"Frameworks: {len(stats['frameworks'])} unique")
    print()

    print("🎯 Getting additional metadata...")
    frameworks = extractor.get_all_frameworks()
    tools = extractor.get_all_tools()
    problem_types = extractor.get_problem_types()

    print(f"  Frameworks: {len(frameworks)} total")
    print(f"  Tools: {len(tools)} total")
    print(f"  Problem Types: {len(problem_types)} total")
    print()

    # Save metadata catalog
    catalog = {
        "frameworks": frameworks,
        "tools": tools,
        "problem_types": problem_types,
        "statistics": stats,
    }

    with open("pws_catalog.json", 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print("✓ Saved metadata catalog to pws_catalog.json")
    print()

    extractor.close()

    print("=" * 80)
    print("EXTRACTION COMPLETE - Ready for Larry Navigator!")
    print("=" * 80)

if __name__ == "__main__":
    main()
