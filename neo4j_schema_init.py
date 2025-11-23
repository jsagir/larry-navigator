#!/usr/bin/env python3
"""
Neo4j Schema Initialization for Larry Navigator
Creates the graph schema optimized for PWS methodology and innovation frameworks
"""

import os
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-instance.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


class LarrySchemaInitializer:
    """Initialize and manage Neo4j schema for Larry Navigator"""

    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        """Execute a Cypher query"""
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return list(result)

    def create_constraints(self):
        """Create uniqueness constraints for key node properties"""
        print("Creating constraints...")

        constraints = [
            # Core entities
            "CREATE CONSTRAINT framework_name IF NOT EXISTS FOR (f:Framework) REQUIRE f.name IS UNIQUE",
            "CREATE CONSTRAINT method_name IF NOT EXISTS FOR (m:Method) REQUIRE m.name IS UNIQUE",
            "CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE",
            "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT problem_type_name IF NOT EXISTS FOR (p:ProblemType) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT persona_name IF NOT EXISTS FOR (p:Persona) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",

            # Content entities
            "CREATE CONSTRAINT document_chunk_id IF NOT EXISTS FOR (d:DocumentChunk) REQUIRE d.chunk_id IS UNIQUE",
            "CREATE CONSTRAINT book_title IF NOT EXISTS FOR (b:Book) REQUIRE (b.title, b.author) IS UNIQUE",
            "CREATE CONSTRAINT case_study_id IF NOT EXISTS FOR (cs:CaseStudy) REQUIRE cs.id IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                self.execute_query(constraint)
                print(f"✓ Created: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
            except Exception as e:
                print(f"⚠ Constraint may already exist: {e}")

    def create_indexes(self):
        """Create indexes for faster queries"""
        print("\nCreating indexes...")

        indexes = [
            # Full-text search indexes
            "CREATE FULLTEXT INDEX framework_search IF NOT EXISTS FOR (f:Framework) ON EACH [f.name, f.description]",
            "CREATE FULLTEXT INDEX concept_search IF NOT EXISTS FOR (c:Concept) ON EACH [c.name, c.description]",
            "CREATE FULLTEXT INDEX document_search IF NOT EXISTS FOR (d:DocumentChunk) ON EACH [d.content]",

            # Property indexes for filtering
            "CREATE INDEX framework_difficulty IF NOT EXISTS FOR (f:Framework) ON (f.difficulty)",
            "CREATE INDEX problem_time_horizon IF NOT EXISTS FOR (p:ProblemType) ON (p.time_horizon)",
            "CREATE INDEX document_type IF NOT EXISTS FOR (d:DocumentChunk) ON (d.document_type)",
            "CREATE INDEX chunk_position IF NOT EXISTS FOR (d:DocumentChunk) ON (d.chunk_position)",
        ]

        for index in indexes:
            try:
                self.execute_query(index)
                print(f"✓ Created: {index.split('FOR')[1].split('ON')[0].strip()}")
            except Exception as e:
                print(f"⚠ Index may already exist: {e}")

    def create_core_nodes(self):
        """Create core taxonomy nodes"""
        print("\nCreating core taxonomy nodes...")

        # Problem Types
        problem_types = [
            {
                "name": "Undefined",
                "description": "Future-back problems with 5-20 year horizons",
                "time_horizon": "5-20 years",
                "uncertainty_level": "HIGH",
                "characteristics": ["Macro trends", "Scenario planning", "Paradigm shifts"],
                "tools": ["Scenario Analysis", "Trending to Absurd", "Analogy Leaps"]
            },
            {
                "name": "Ill-Defined",
                "description": "Present-forward problems with 1-5 year horizons",
                "time_horizon": "1-5 years",
                "uncertainty_level": "MEDIUM",
                "characteristics": ["Near-term trends", "Tech scans", "Value migration"],
                "tools": ["Jobs-to-be-Done", "Design Thinking", "Blue Ocean Strategy"]
            },
            {
                "name": "Well-Defined",
                "description": "Execute-now problems with <1 year horizon",
                "time_horizon": "<1 year",
                "uncertainty_level": "LOW",
                "characteristics": ["Clear objectives", "Known constraints", "Execution focus"],
                "tools": ["Five Whys", "MECE Analysis", "Prototyping"]
            },
            {
                "name": "Wicked",
                "description": "Complex systems problems with interconnected stakeholders",
                "time_horizon": "Variable",
                "uncertainty_level": "VERY HIGH",
                "characteristics": ["No clear solution", "Solving creates new problems", "Stakeholder conflicts"],
                "tools": ["Stakeholder Mapping", "Systems Thinking", "Pre-mortem Analysis"]
            }
        ]

        for pt in problem_types:
            self.execute_query("""
                MERGE (p:ProblemType {name: $name})
                SET p.description = $description,
                    p.time_horizon = $time_horizon,
                    p.uncertainty_level = $uncertainty_level,
                    p.characteristics = $characteristics,
                    p.tools = $tools
            """, pt)
            print(f"✓ Created ProblemType: {pt['name']}")

        # Personas
        personas = [
            {"name": "Student", "description": "Course navigation, exam prep, concept learning", "learning_style": "Academic"},
            {"name": "Entrepreneur", "description": "Idea validation, opportunity identification", "learning_style": "Action-oriented"},
            {"name": "Corporate", "description": "Systematic innovation, portfolio management", "learning_style": "Strategic"},
            {"name": "Consultant", "description": "Framework application, client advisory", "learning_style": "Prescriptive"},
            {"name": "Researcher", "description": "Theory exploration, literature connections", "learning_style": "Analytical"},
            {"name": "Nonprofit Leader", "description": "Social innovation, impact measurement", "learning_style": "Mission-driven"}
        ]

        for persona in personas:
            self.execute_query("""
                MERGE (p:Persona {name: $name})
                SET p.description = $description,
                    p.learning_style = $learning_style
            """, persona)
            print(f"✓ Created Persona: {persona['name']}")

        # Innovation Portfolio Horizons
        horizons = [
            {"name": "Now", "description": "Incremental improvements to existing offerings", "resource_allocation": "70%", "time_frame": "0-12 months"},
            {"name": "New", "description": "Adjacent opportunities and market expansion", "resource_allocation": "20%", "time_frame": "1-3 years"},
            {"name": "Next", "description": "Disruptive innovations and business model changes", "resource_allocation": "10%", "time_frame": "3-5 years"}
        ]

        for horizon in horizons:
            self.execute_query("""
                MERGE (h:PortfolioHorizon {name: $name})
                SET h.description = $description,
                    h.resource_allocation = $resource_allocation,
                    h.time_frame = $time_frame
            """, horizon)
            print(f"✓ Created PortfolioHorizon: {horizon['name']}")

    def create_framework_nodes(self):
        """Create framework nodes with metadata"""
        print("\nCreating framework nodes...")

        frameworks = [
            {
                "name": "Design Thinking",
                "description": "Human-centered approach to innovation with empathy, ideation, and prototyping",
                "difficulty": "BEGINNER",
                "problem_types": ["Ill-Defined", "Well-Defined"],
                "personas": ["Corporate", "Entrepreneur", "Nonprofit Leader"],
                "time_required": "2-4 weeks",
                "team_size": "3-8 people"
            },
            {
                "name": "Jobs-to-be-Done",
                "description": "Framework for understanding customer needs through the jobs they hire products to do",
                "difficulty": "INTERMEDIATE",
                "problem_types": ["Ill-Defined", "Well-Defined"],
                "personas": ["Entrepreneur", "Corporate", "Consultant"],
                "time_required": "1-2 weeks",
                "team_size": "2-5 people"
            },
            {
                "name": "Three Box Solution",
                "description": "Manage present (Box 1), selectively forget past (Box 2), create future (Box 3)",
                "difficulty": "ADVANCED",
                "problem_types": ["Ill-Defined", "Undefined"],
                "personas": ["Corporate", "Consultant"],
                "time_required": "3-6 months",
                "team_size": "5-15 people"
            },
            {
                "name": "Scenario Analysis",
                "description": "Explore multiple plausible futures to prepare for uncertainty",
                "difficulty": "ADVANCED",
                "problem_types": ["Undefined", "Ill-Defined"],
                "personas": ["Corporate", "Researcher", "Consultant"],
                "time_required": "4-8 weeks",
                "team_size": "4-10 people"
            },
            {
                "name": "Blue Ocean Strategy",
                "description": "Create uncontested market space by making competition irrelevant",
                "difficulty": "ADVANCED",
                "problem_types": ["Ill-Defined", "Undefined"],
                "personas": ["Corporate", "Entrepreneur", "Consultant"],
                "time_required": "2-4 months",
                "team_size": "3-8 people"
            },
            {
                "name": "Disruptive Innovation",
                "description": "Identify and capitalize on opportunities where low-end or new markets disrupt incumbents",
                "difficulty": "ADVANCED",
                "problem_types": ["Ill-Defined", "Undefined"],
                "personas": ["Corporate", "Entrepreneur", "Researcher"],
                "time_required": "3-6 months",
                "team_size": "5-12 people"
            },
            {
                "name": "Mom Test",
                "description": "Customer interview framework to get honest feedback by focusing on past behavior",
                "difficulty": "BEGINNER",
                "problem_types": ["Well-Defined", "Ill-Defined"],
                "personas": ["Entrepreneur", "Consultant"],
                "time_required": "1-2 weeks",
                "team_size": "1-3 people"
            },
            {
                "name": "Five Whys",
                "description": "Root cause analysis by asking 'why' five times",
                "difficulty": "BEGINNER",
                "problem_types": ["Well-Defined"],
                "personas": ["Student", "Entrepreneur", "Corporate"],
                "time_required": "1-3 days",
                "team_size": "2-5 people"
            },
            {
                "name": "TRIZ",
                "description": "Systematic innovation using 40 inventive principles and contradiction matrix",
                "difficulty": "ADVANCED",
                "problem_types": ["Well-Defined", "Ill-Defined"],
                "personas": ["Researcher", "Corporate", "Consultant"],
                "time_required": "2-3 months",
                "team_size": "3-6 people"
            },
            {
                "name": "Lean Startup",
                "description": "Build-Measure-Learn cycle for rapid validated learning",
                "difficulty": "INTERMEDIATE",
                "problem_types": ["Ill-Defined", "Well-Defined"],
                "personas": ["Entrepreneur", "Corporate"],
                "time_required": "3-6 months",
                "team_size": "2-8 people"
            }
        ]

        for fw in frameworks:
            self.execute_query("""
                MERGE (f:Framework {name: $name})
                SET f.description = $description,
                    f.difficulty = $difficulty,
                    f.time_required = $time_required,
                    f.team_size = $team_size
            """, fw)

            # Link to problem types
            for pt_name in fw['problem_types']:
                self.execute_query("""
                    MATCH (f:Framework {name: $framework_name})
                    MATCH (pt:ProblemType {name: $problem_type})
                    MERGE (f)-[:ADDRESSES]->(pt)
                """, {"framework_name": fw['name'], "problem_type": pt_name})

            # Link to personas
            for persona_name in fw['personas']:
                self.execute_query("""
                    MATCH (f:Framework {name: $framework_name})
                    MATCH (p:Persona {name: $persona})
                    MERGE (p)-[:USES]->(f)
                """, {"framework_name": fw['name'], "persona": persona_name})

            print(f"✓ Created Framework: {fw['name']}")

    def create_author_nodes(self):
        """Create author nodes and their contributions"""
        print("\nCreating author nodes...")

        authors = [
            {"name": "Clayton Christensen", "expertise": "Disruptive Innovation", "books": ["The Innovator's Dilemma", "The Innovator's Solution"]},
            {"name": "Peter Drucker", "expertise": "Management", "books": ["Innovation and Entrepreneurship", "The Effective Executive"]},
            {"name": "Eric Ries", "expertise": "Lean Startup", "books": ["The Lean Startup", "The Startup Way"]},
            {"name": "Steve Blank", "expertise": "Customer Development", "books": ["The Four Steps to the Epiphany", "The Startup Owner's Manual"]},
            {"name": "Rita McGrath", "expertise": "Strategic Inflection Points", "books": ["Seeing Around Corners", "The End of Competitive Advantage"]},
            {"name": "Vijay Govindarajan", "expertise": "Three Box Solution", "books": ["The Three Box Solution", "Reverse Innovation"]},
            {"name": "W. Chan Kim & Renée Mauborgne", "expertise": "Blue Ocean Strategy", "books": ["Blue Ocean Strategy", "Blue Ocean Shift"]},
            {"name": "Tim Brown", "expertise": "Design Thinking", "books": ["Change by Design"]},
            {"name": "Alex Osterwalder", "expertise": "Business Models", "books": ["Business Model Generation", "Value Proposition Design"]}
        ]

        for author in authors:
            self.execute_query("""
                MERGE (a:Author {name: $name})
                SET a.expertise = $expertise,
                    a.books = $books
            """, author)
            print(f"✓ Created Author: {author['name']}")

    def create_relationships(self):
        """Create additional semantic relationships"""
        print("\nCreating semantic relationships...")

        # Framework relationships
        relationships = [
            ("Design Thinking", "COMPLEMENTS", "Jobs-to-be-Done"),
            ("Lean Startup", "BUILDS_ON", "Jobs-to-be-Done"),
            ("Blue Ocean Strategy", "COMPLEMENTS", "Disruptive Innovation"),
            ("Three Box Solution", "REQUIRES", "Scenario Analysis"),
            ("Mom Test", "VALIDATES", "Jobs-to-be-Done"),
            ("Five Whys", "SUPPORTS", "Design Thinking"),
        ]

        for source, rel, target in relationships:
            self.execute_query(f"""
                MATCH (source:Framework {{name: $source}})
                MATCH (target:Framework {{name: $target}})
                MERGE (source)-[:{rel}]->(target)
            """, {"source": source, "target": target})
            print(f"✓ {source} -{rel}-> {target}")

    def initialize_schema(self):
        """Run full schema initialization"""
        print("=" * 60)
        print("LARRY NAVIGATOR - NEO4J SCHEMA INITIALIZATION")
        print("=" * 60)
        print()

        try:
            self.create_constraints()
            self.create_indexes()
            self.create_core_nodes()
            self.create_framework_nodes()
            self.create_author_nodes()
            self.create_relationships()

            print("\n" + "=" * 60)
            print("✓ SCHEMA INITIALIZATION COMPLETE!")
            print("=" * 60)

            # Print summary
            summary = self.execute_query("""
                CALL apoc.meta.stats() YIELD labels, relTypesCount
                RETURN labels, relTypesCount
            """)

            if summary:
                print("\nDatabase Summary:")
                print(f"  Nodes by Label: {summary[0]['labels']}")
                print(f"  Relationship Types: {summary[0]['relTypesCount']}")

        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            raise

    def verify_schema(self):
        """Verify schema was created correctly"""
        print("\n" + "=" * 60)
        print("VERIFYING SCHEMA")
        print("=" * 60)

        checks = [
            ("ProblemType nodes", "MATCH (p:ProblemType) RETURN count(p) as count"),
            ("Framework nodes", "MATCH (f:Framework) RETURN count(f) as count"),
            ("Persona nodes", "MATCH (p:Persona) RETURN count(p) as count"),
            ("Author nodes", "MATCH (a:Author) RETURN count(a) as count"),
            ("ADDRESSES relationships", "MATCH ()-[r:ADDRESSES]->() RETURN count(r) as count"),
            ("USES relationships", "MATCH ()-[r:USES]->() RETURN count(r) as count"),
        ]

        for name, query in checks:
            result = self.execute_query(query)
            count = result[0]['count'] if result else 0
            status = "✓" if count > 0 else "✗"
            print(f"{status} {name}: {count}")


def main():
    """Main execution"""
    print("\nConnecting to Neo4j...")
    print(f"URI: {NEO4J_URI}")
    print(f"Database: {NEO4J_DATABASE}")

    initializer = LarrySchemaInitializer(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

    try:
        initializer.initialize_schema()
        initializer.verify_schema()
    finally:
        initializer.close()
        print("\n✓ Connection closed")


if __name__ == "__main__":
    main()
