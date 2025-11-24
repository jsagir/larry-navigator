#!/usr/bin/env python3
"""
Quick Neo4j Database Inspector
Shows what content is available in your Neo4j database
"""

import os

# Try to import neo4j
try:
    from neo4j import GraphDatabase
except ImportError:
    print("Installing neo4j driver...")
    os.system("pip install neo4j")
    from neo4j import GraphDatabase

# Your credentials
NEO4J_URI = "neo4j+s://5b8df33f.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ukfioEbJ2JLqM_8bulME166CJ5zLJdSO5uEucuvYky8"

print("=" * 80)
print("NEO4J DATABASE INSPECTOR")
print("=" * 80)
print(f"\nConnecting to: {NEO4J_URI}")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    # Get node counts by label
    print("\n📊 NODE COUNTS BY LABEL:")
    print("-" * 80)
    result = session.run("CALL db.labels() YIELD label RETURN label")
    labels = [record["label"] for record in result]

    for label in sorted(labels):
        count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
        count = count_result.single()["count"]
        print(f"  {label:30} {count:>10,} nodes")

    # Get relationship counts
    print("\n🔗 RELATIONSHIP COUNTS:")
    print("-" * 80)
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    rel_types = [record["relationshipType"] for record in result]

    for rel_type in sorted(rel_types):
        count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
        count = count_result.single()["count"]
        print(f"  {rel_type:30} {count:>10,} relationships")

    # Sample DocumentChunk if exists
    if "DocumentChunk" in labels:
        print("\n📄 SAMPLE DOCUMENT CHUNK:")
        print("-" * 80)
        result = session.run("""
            MATCH (chunk:DocumentChunk)
            RETURN chunk
            LIMIT 1
        """)
        sample = result.single()
        if sample:
            chunk = dict(sample["chunk"])
            print(f"  Properties available:")
            for key, value in chunk.items():
                value_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"    • {key}: {value_preview}")

    # Sample Framework if exists
    if "Framework" in labels:
        print("\n🎯 SAMPLE FRAMEWORK:")
        print("-" * 80)
        result = session.run("""
            MATCH (fw:Framework)
            RETURN fw.name as name, fw.description as description
            LIMIT 3
        """)
        for record in result:
            print(f"  • {record['name']}")
            if record['description']:
                desc = record['description'][:100] + "..." if len(record['description']) > 100 else record['description']
                print(f"    {desc}")

    # Total database stats
    print("\n📈 DATABASE STATISTICS:")
    print("-" * 80)
    total_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
    total_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
    print(f"  Total Nodes:         {total_nodes:>10,}")
    print(f"  Total Relationships: {total_rels:>10,}")
    print(f"  Node Labels:         {len(labels):>10,}")
    print(f"  Relationship Types:  {len(rel_types):>10,}")

driver.close()

print("\n" + "=" * 80)
print("✓ INSPECTION COMPLETE")
print("=" * 80)
print("\nBased on this structure, we can now extract and upload to File Search.")
