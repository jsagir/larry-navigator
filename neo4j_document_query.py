#!/usr/bin/env python3
"""
Query Neo4j for Document and Chunk structure for PWS Navigator
"""

from neo4j import GraphDatabase
import json

URI = "neo4j+s://5b8df33f.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "ukfioEbJ2JLqM_8bulME166CJ5zLJdSO5uEucuvYky8"

class DocumentExplorer:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    def close(self):
        self.driver.close()

    def query_documents(self):
        """Get all Document nodes with their properties"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document)
            RETURN d
            LIMIT 10
            """
            result = session.run(query)
            return [dict(record["d"]) for record in result]

    def query_document_chunks(self):
        """Get DocumentChunk nodes and their relationships"""
        with self.driver.session() as session:
            query = """
            MATCH (dc:DocumentChunk)
            RETURN dc
            LIMIT 5
            """
            result = session.run(query)
            return [dict(record["dc"]) for record in result]

    def query_document_relationships(self):
        """Understand Document → Chunk relationships"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document)-[r]->(dc:DocumentChunk)
            RETURN d.name as doc_name, type(r) as relationship, count(dc) as chunk_count
            LIMIT 10
            """
            result = session.run(query)
            return [dict(record) for record in result]

    def query_frameworks(self):
        """Get Framework nodes"""
        with self.driver.session() as session:
            query = """
            MATCH (f:Framework)
            RETURN f
            LIMIT 5
            """
            result = session.run(query)
            return [dict(record["f"]) for record in result]

    def query_tools(self):
        """Get InnovationTool nodes"""
        with self.driver.session() as session:
            query = """
            MATCH (t:InnovationTool)
            RETURN t
            LIMIT 5
            """
            result = session.run(query)
            return [dict(record["t"]) for record in result]

    def query_week_modules(self):
        """Get WeekModule structure"""
        with self.driver.session() as session:
            query = """
            MATCH (w:WeekModule)
            RETURN w
            ORDER BY w.week
            LIMIT 10
            """
            result = session.run(query)
            return [dict(record["w"]) for record in result]

    def query_case_studies(self):
        """Get CaseStudy nodes"""
        with self.driver.session() as session:
            query = """
            MATCH (cs:CaseStudy)
            RETURN cs
            LIMIT 5
            """
            result = session.run(query)
            return [dict(record["cs"]) for record in result]

    def query_problem_types(self):
        """Get ProblemType nodes"""
        with self.driver.session() as session:
            query = """
            MATCH (pt:ProblemType)
            RETURN pt
            """
            result = session.run(query)
            return [dict(record["pt"]) for record in result]

    def query_professor(self):
        """Find Lawrence Aronhime or Professor nodes"""
        with self.driver.session() as session:
            query = """
            MATCH (p:Professor)
            RETURN p
            LIMIT 5
            """
            result = session.run(query)
            professors = [dict(record["p"]) for record in result]

            # Also try Person nodes
            query2 = """
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS 'aronhime' OR toLower(p.name) CONTAINS 'lawrence'
            RETURN p
            LIMIT 5
            """
            result2 = session.run(query2)
            persons = [dict(record["p"]) for record in result2]

            return {"professors": professors, "persons": persons}

    def query_document_framework_connections(self):
        """How are Documents connected to Frameworks?"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document)-[r]-(f:Framework)
            RETURN d.name as document, type(r) as relationship, f.name as framework
            LIMIT 10
            """
            result = session.run(query)
            return [dict(record) for record in result]

    def query_chunk_properties(self):
        """What properties do DocumentChunks have?"""
        with self.driver.session() as session:
            query = """
            MATCH (dc:DocumentChunk)
            WITH dc LIMIT 1
            RETURN keys(dc) as properties
            """
            result = session.run(query)
            return result.single()["properties"] if result.peek() else []

    def query_document_properties(self):
        """What properties do Documents have?"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document)
            WITH d LIMIT 1
            RETURN keys(d) as properties
            """
            result = session.run(query)
            return result.single()["properties"] if result.peek() else []

def main():
    explorer = DocumentExplorer()

    print("=" * 80)
    print("PWS NAVIGATOR - DOCUMENT & CONTENT ANALYSIS")
    print("=" * 80)
    print()

    # Document properties
    print("📄 DOCUMENT NODE PROPERTIES:")
    print("-" * 80)
    doc_props = explorer.query_document_properties()
    for prop in doc_props:
        print(f"  • {prop}")
    print()

    # Documents
    print("📚 SAMPLE DOCUMENTS (10):")
    print("-" * 80)
    docs = explorer.query_documents()
    for doc in docs:
        print(json.dumps(doc, indent=2, default=str))
        print()
    print()

    # Chunk properties
    print("🧩 DOCUMENT CHUNK PROPERTIES:")
    print("-" * 80)
    chunk_props = explorer.query_chunk_properties()
    for prop in chunk_props:
        print(f"  • {prop}")
    print()

    # Document → Chunk relationships
    print("🔗 DOCUMENT → CHUNK RELATIONSHIPS:")
    print("-" * 80)
    doc_rels = explorer.query_document_relationships()
    for rel in doc_rels:
        print(f"  {rel}")
    print()

    # Frameworks
    print("🎯 SAMPLE FRAMEWORKS (5):")
    print("-" * 80)
    frameworks = explorer.query_frameworks()
    for fw in frameworks:
        print(json.dumps(fw, indent=2, default=str))
        print()
    print()

    # Tools
    print("🛠️  SAMPLE INNOVATION TOOLS (5):")
    print("-" * 80)
    tools = explorer.query_tools()
    for tool in tools:
        print(json.dumps(tool, indent=2, default=str))
        print()
    print()

    # Week Modules
    print("📅 WEEK MODULES:")
    print("-" * 80)
    weeks = explorer.query_week_modules()
    for week in weeks:
        print(json.dumps(week, indent=2, default=str))
        print()
    print()

    # Problem Types
    print("❓ PROBLEM TYPES:")
    print("-" * 80)
    problem_types = explorer.query_problem_types()
    for pt in problem_types:
        print(json.dumps(pt, indent=2, default=str))
        print()
    print()

    # Case Studies
    print("📖 SAMPLE CASE STUDIES (5):")
    print("-" * 80)
    case_studies = explorer.query_case_studies()
    for cs in case_studies:
        print(json.dumps(cs, indent=2, default=str))
        print()
    print()

    # Professor / Aronhime
    print("👨‍🏫 PROFESSOR / LAWRENCE ARONHIME:")
    print("-" * 80)
    profs = explorer.query_professor()
    print("Professors:")
    for p in profs["professors"]:
        print(json.dumps(p, indent=2, default=str))
    print("\nPersons (Aronhime/Lawrence):")
    for p in profs["persons"]:
        print(json.dumps(p, indent=2, default=str))
    print()

    # Document ↔ Framework connections
    print("🔗 DOCUMENT ↔ FRAMEWORK CONNECTIONS:")
    print("-" * 80)
    doc_fw_conns = explorer.query_document_framework_connections()
    for conn in doc_fw_conns:
        print(f"  {conn}")
    print()

    explorer.close()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
