#!/usr/bin/env python3
"""
PWS Innovation Navigator - Neo4j Database Explorer
READ ONLY - Schema exploration and metadata extraction
"""

from neo4j import GraphDatabase
import json

# Neo4j Connection
URI = "neo4j+s://5b8df33f.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "ukfioEbJ2JLqM_8bulME166CJ5zLJdSO5uEucuvYky8"

class Neo4jExplorer:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    def close(self):
        self.driver.close()

    def get_labels(self):
        """Get all node labels in the database"""
        with self.driver.session() as session:
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            return labels

    def get_relationship_types(self):
        """Get all relationship types"""
        with self.driver.session() as session:
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            return rel_types

    def get_node_count_by_label(self):
        """Count nodes by label"""
        labels = self.get_labels()
        counts = {}
        with self.driver.session() as session:
            for label in labels:
                result = session.run(f"MATCH (n:`{label}`) RETURN count(n) as count")
                counts[label] = result.single()["count"]
        return counts

    def get_sample_nodes(self, label, limit=3):
        """Get sample nodes for a given label"""
        with self.driver.session() as session:
            query = f"MATCH (n:`{label}`) RETURN n LIMIT {limit}"
            result = session.run(query)
            nodes = []
            for record in result:
                node = record["n"]
                nodes.append(dict(node))
            return nodes

    def get_schema_visualization(self):
        """Get schema relationships"""
        with self.driver.session() as session:
            query = """
            CALL db.schema.visualization()
            """
            try:
                result = session.run(query)
                return list(result)
            except:
                # Alternative schema query
                query = """
                MATCH (n)-[r]->(m)
                WITH labels(n) as from_labels, type(r) as rel_type, labels(m) as to_labels
                RETURN DISTINCT from_labels, rel_type, to_labels
                LIMIT 50
                """
                result = session.run(query)
                return [dict(record) for record in result]

    def search_for_files(self):
        """Search for file-related nodes"""
        with self.driver.session() as session:
            # Try common file-related properties
            queries = [
                "MATCH (n) WHERE n.filename IS NOT NULL RETURN n LIMIT 5",
                "MATCH (n) WHERE n.file_path IS NOT NULL RETURN n LIMIT 5",
                "MATCH (n) WHERE n.google_drive_id IS NOT NULL RETURN n LIMIT 5",
                "MATCH (n) WHERE n.path IS NOT NULL RETURN n LIMIT 5",
                "MATCH (n) WHERE n.url IS NOT NULL RETURN n LIMIT 5",
            ]

            results = {}
            for query in queries:
                try:
                    result = session.run(query)
                    records = [dict(record["n"]) for record in result]
                    if records:
                        query_name = query.split("WHERE")[1].split("IS NOT NULL")[0].strip()
                        results[query_name] = records
                except Exception as e:
                    pass

            return results

    def search_pws_content(self):
        """Search for PWS-related content (lectures, frameworks, etc.)"""
        with self.driver.session() as session:
            # Try to find lecture/framework/tool nodes
            queries = {
                "Lectures": "MATCH (n) WHERE toLower(labels(n)[0]) CONTAINS 'lecture' OR n.lecture_number IS NOT NULL RETURN n LIMIT 5",
                "Frameworks": "MATCH (n) WHERE toLower(labels(n)[0]) CONTAINS 'framework' OR n.framework_name IS NOT NULL RETURN n LIMIT 5",
                "Tools": "MATCH (n) WHERE toLower(labels(n)[0]) CONTAINS 'tool' RETURN n LIMIT 5",
                "CaseStudies": "MATCH (n) WHERE toLower(labels(n)[0]) CONTAINS 'case' RETURN n LIMIT 5",
                "Documents": "MATCH (n) WHERE toLower(labels(n)[0]) CONTAINS 'doc' RETURN n LIMIT 5",
            }

            results = {}
            for name, query in queries.items():
                try:
                    result = session.run(query)
                    records = [dict(record["n"]) for record in result]
                    if records:
                        results[name] = records
                except:
                    pass

            return results

    def get_all_property_keys(self):
        """Get all property keys used in the database"""
        with self.driver.session() as session:
            query = "CALL db.propertyKeys()"
            result = session.run(query)
            return [record["propertyKey"] for record in result]

def main():
    explorer = Neo4jExplorer()

    print("=" * 80)
    print("PWS INNOVATION NAVIGATOR - NEO4J DATABASE EXPLORATION")
    print("=" * 80)
    print()

    # 1. Get all labels
    print("📊 NODE LABELS:")
    print("-" * 80)
    labels = explorer.get_labels()
    for label in labels:
        print(f"  • {label}")
    print()

    # 2. Node counts
    print("📈 NODE COUNTS BY LABEL:")
    print("-" * 80)
    counts = explorer.get_node_count_by_label()
    for label, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {label:30} {count:>6} nodes")
    print()

    # 3. Relationship types
    print("🔗 RELATIONSHIP TYPES:")
    print("-" * 80)
    rel_types = explorer.get_relationship_types()
    for rel_type in rel_types:
        print(f"  • {rel_type}")
    print()

    # 4. Property keys
    print("🔑 PROPERTY KEYS:")
    print("-" * 80)
    prop_keys = explorer.get_all_property_keys()
    for key in sorted(prop_keys):
        print(f"  • {key}")
    print()

    # 5. Schema visualization
    print("🏗️  SCHEMA RELATIONSHIPS:")
    print("-" * 80)
    schema = explorer.get_schema_visualization()
    for item in schema[:20]:  # First 20 relationships
        print(f"  {item}")
    print()

    # 6. Search for files
    print("📁 FILE-RELATED NODES:")
    print("-" * 80)
    file_results = explorer.search_for_files()
    for query_name, records in file_results.items():
        print(f"\n  Query: {query_name}")
        for record in records:
            print(f"    {json.dumps(record, indent=6, default=str)}")
    print()

    # 7. Search for PWS content
    print("📚 PWS CONTENT NODES:")
    print("-" * 80)
    pws_results = explorer.search_pws_content()
    for content_type, records in pws_results.items():
        print(f"\n  {content_type}:")
        for record in records:
            print(f"    {json.dumps(record, indent=6, default=str)}")
    print()

    # 8. Sample nodes from each label
    print("🔍 SAMPLE NODES (First 2 from each label):")
    print("-" * 80)
    for label in labels[:5]:  # First 5 labels
        print(f"\n  Label: {label}")
        samples = explorer.get_sample_nodes(label, limit=2)
        for sample in samples:
            print(f"    {json.dumps(sample, indent=6, default=str)}")
    print()

    explorer.close()
    print("=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
