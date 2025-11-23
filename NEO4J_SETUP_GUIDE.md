# Larry Navigator - Neo4j Knowledge Graph Setup Guide

## Overview

Larry Navigator uses Neo4j to create a **knowledge graph** that captures relationships between:
- **Frameworks** (Design Thinking, Jobs-to-be-Done, etc.)
- **Problem Types** (Undefined, Ill-Defined, Well-Defined, Wicked)
- **Personas** (Student, Entrepreneur, Corporate, Consultant, etc.)
- **Authors** (Clayton Christensen, Peter Drucker, etc.)
- **Concepts**, **Methods**, and **Case Studies**

This provides **network-effect RAG** - discovering insights through relationships, not just keyword matching.

---

## Schema Design

### Node Types

```cypher
(:Framework)           # Innovation frameworks (Design Thinking, JTBD, etc.)
(:ProblemType)         # Undefined, Ill-Defined, Well-Defined, Wicked
(:Persona)             # Student, Entrepreneur, Corporate, etc.
(:Author)              # Thought leaders and book authors
(:Book)                # Reference books
(:Concept)             # Key concepts and ideas
(:Method)              # Specific methods and techniques
(:Topic)               # Topics and subject areas
(:CaseStudy)           # Real-world examples
(:DocumentChunk)       # Chunked content from PWS materials
(:PortfolioHorizon)    # Now, New, Next innovation horizons
```

### Relationships

```cypher
(:Framework)-[:ADDRESSES]->(:ProblemType)
(:Persona)-[:USES]->(:Framework)
(:Author)-[:CREATED]->(:Framework)
(:Author)-[:WROTE]->(:Book)
(:Framework)-[:COMPLEMENTS]->(:Framework)
(:Framework)-[:BUILDS_ON]->(:Framework)
(:Framework)-[:REQUIRES]->(:Framework)
(:CaseStudy)-[:DEMONSTRATES]->(:Framework)
(:DocumentChunk)-[:DISCUSSES]->(:Concept)
(:Book)-[:INTRODUCES]->(:Framework)
```

---

## Quick Start

### 1. Set Environment Variables

Create or update `.env` file:

```bash
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password
NEO4J_DATABASE=neo4j
```

### 2. Initialize Schema

Run the schema initialization script:

```bash
python3 neo4j_schema_init.py
```

This will:
- ✓ Create uniqueness constraints
- ✓ Create search indexes
- ✓ Create core taxonomy nodes (Problem Types, Personas, Horizons)
- ✓ Create framework nodes with metadata
- ✓ Create author nodes
- ✓ Link everything together with relationships

**Expected output:**
```
============================================================
LARRY NAVIGATOR - NEO4J SCHEMA INITIALIZATION
============================================================

Creating constraints...
✓ Created: (f:Framework) REQUIRE f.name IS UNIQUE
✓ Created: (m:Method) REQUIRE m.name IS UNIQUE
...

Creating indexes...
✓ Created: framework_search
✓ Created: concept_search
...

Creating core taxonomy nodes...
✓ Created ProblemType: Undefined
✓ Created ProblemType: Ill-Defined
✓ Created ProblemType: Well-Defined
✓ Created ProblemType: Wicked
...

Creating framework nodes...
✓ Created Framework: Design Thinking
✓ Created Framework: Jobs-to-be-Done
...

✓ SCHEMA INITIALIZATION COMPLETE!
```

### 3. Verify Schema

The script automatically verifies the schema:

```
VERIFYING SCHEMA
============================================================
✓ ProblemType nodes: 4
✓ Framework nodes: 10
✓ Persona nodes: 6
✓ Author nodes: 9
✓ ADDRESSES relationships: 20+
✓ USES relationships: 30+
```

---

## Pre-Built Cypher Queries

Larry uses **20+ pre-built Cypher queries** instead of LLM-generated queries for:
- **Speed** - No LLM round-trip for query generation
- **Reliability** - Tested, optimized queries
- **Consistency** - Predictable results

### Query Categories

1. **Framework Discovery** (4 queries)
   - Find frameworks by problem type
   - Find frameworks by persona
   - Find beginner frameworks
   - Find related frameworks

2. **Problem Type Classification** (2 queries)
   - Classify by time horizon
   - Get problem type details

3. **Concept & Knowledge Discovery** (2 queries)
   - Search concepts by keyword
   - Find document chunks

4. **Author & Book Queries** (2 queries)
   - Find authors by expertise
   - Get book information

5. **Portfolio & Innovation Horizon** (2 queries)
   - Get portfolio horizon frameworks
   - Portfolio recommendations

6. **Learning Paths & Recommendations** (2 queries)
   - Learning path for persona
   - Prerequisite frameworks

7. **Case Studies & Examples** (1 query)
   - Find case studies

8. **Advanced Queries** (3 queries)
   - Discover framework clusters
   - Find by multiple criteria
   - Semantic framework search

9. **Diagnostic Queries** (1 query)
   - Diagnose problem and recommend

10. **Content Enrichment** (1 query)
    - Enrich response with context

---

## Usage Examples

### Python Integration

```python
from larry_neo4j_rag_v2 import LarryNeo4jRAG

# Initialize
rag = LarryNeo4jRAG()

# Get context for a user question
context = rag.get_rag_context(
    user_message="Which framework should I use for undefined problems?",
    persona="Entrepreneur",
    problem_type="Undefined"
)

print(context)
# Output:
# **Relevant Frameworks from Knowledge Graph:**
#
# 1. **Scenario Analysis** (ADVANCED)
#    - Explore multiple plausible futures to prepare for uncertainty
#    - Addresses: Undefined, Ill-Defined
#
# 2. **Blue Ocean Strategy** (ADVANCED)
#    - Create uncontested market space by making competition irrelevant
#    - Addresses: Ill-Defined, Undefined
# ...

rag.close()
```

### Quick Function

```python
from larry_neo4j_rag_v2 import get_neo4j_rag_context_fast

# One-liner with auto-cleanup
context = get_neo4j_rag_context_fast(
    "How do I validate my startup idea?",
    persona="Entrepreneur",
    problem_type="Ill-Defined"
)
```

### Direct Cypher Query

```python
from larry_neo4j_rag_v2 import LarryNeo4jRAG
from larry_cypher_queries import CYPHER_QUERIES

rag = LarryNeo4jRAG()

# Execute a specific query
results = rag.execute_query(
    CYPHER_QUERIES["find_frameworks_by_persona"],
    {"persona": "Student"}
)

print(results)
# [
#   {'framework': 'Design Thinking', 'difficulty': 'BEGINNER', ...},
#   {'framework': 'Five Whys', 'difficulty': 'BEGINNER', ...},
#   ...
# ]

rag.close()
```

---

## Query Selection Logic

The system **automatically selects** the best query based on question keywords:

| Question Pattern | Selected Query | Example |
|-----------------|----------------|---------|
| "which framework", "what framework" | `find_frameworks_by_problem_type` or `find_frameworks_by_persona` | "Which framework for undefined problems?" |
| "what type of problem", "classify" | `get_problem_type_details` | "What type of problem is this?" |
| "related to", "similar to" | `find_related_frameworks` | "What's similar to Design Thinking?" |
| "learning path", "where to start" | `learning_path_for_persona` | "What's a good learning path?" |
| "portfolio", "now new next" | `portfolio_recommendations` | "How do I manage my portfolio?" |
| "example", "case study" | `find_case_studies` | "Show me real examples" |
| *default* | `semantic_framework_search` | Any general question |

---

## Sample Cypher Queries

### Find Frameworks for a Problem Type

```cypher
MATCH (f:Framework)-[:ADDRESSES]->(pt:ProblemType {name: 'Undefined'})
OPTIONAL MATCH (a:Author)-[:CREATED]->(f)
RETURN
    f.name AS framework,
    f.description AS description,
    f.difficulty AS difficulty,
    f.time_required AS time_required,
    collect(DISTINCT a.name) AS authors
ORDER BY
    CASE f.difficulty
        WHEN 'BEGINNER' THEN 1
        WHEN 'INTERMEDIATE' THEN 2
        WHEN 'ADVANCED' THEN 3
    END
LIMIT 5
```

### Get Learning Path for Persona

```cypher
MATCH (p:Persona {name: 'Entrepreneur'})-[:USES]->(f:Framework)
MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
WITH f, pt, p,
    CASE f.difficulty
        WHEN 'BEGINNER' THEN 1
        WHEN 'INTERMEDIATE' THEN 2
        WHEN 'ADVANCED' THEN 3
    END AS difficulty_order
RETURN
    f.name AS framework,
    f.difficulty AS level,
    f.description AS description,
    pt.name AS problem_type,
    f.time_required AS time_commitment
ORDER BY difficulty_order, f.time_required
LIMIT 5
```

### Discover Framework Clusters

```cypher
MATCH (f:Framework {name: 'Design Thinking'})
CALL apoc.path.subgraphNodes(f, {
    relationshipFilter: "COMPLEMENTS|BUILDS_ON|REQUIRES",
    maxLevel: 2
})
YIELD node
MATCH (node)-[:ADDRESSES]->(pt:ProblemType)
RETURN
    node.name AS framework,
    node.description AS description,
    collect(DISTINCT pt.name) AS addresses
LIMIT 8
```

---

## Configuration for Streamlit Cloud

Add to Streamlit Cloud **Secrets**:

```toml
[default]
NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your-secure-password"
NEO4J_DATABASE = "neo4j"
```

---

## Re-enabling Neo4j in Larry Tools

Once the schema is initialized, re-enable Neo4j in `larry_tools.py`:

### Current (Disabled):

```python
def fetch_neo4j_context():
    """Query Neo4j graph database - DISABLED due to timeout issues."""
    return None
```

### Updated (Enabled with new fast system):

```python
def fetch_neo4j_context():
    """Query Neo4j graph database using pre-built queries."""
    from larry_neo4j_rag_v2 import get_neo4j_rag_context_fast

    try:
        context = get_neo4j_rag_context_fast(
            user_message=query,
            persona=persona,
            problem_type=problem_type
        )
        if context:
            return f"NETWORK-EFFECT GRAPH CONTEXT:\n{context}"
        return None
    except Exception as e:
        return f"NETWORK-EFFECT GRAPH ERROR: {str(e)}"
```

---

## Troubleshooting

### Connection Issues

```python
# Test connection
from larry_neo4j_rag_v2 import LarryNeo4jRAG

rag = LarryNeo4jRAG()
if rag.driver:
    print("✓ Connected")
else:
    print("✗ Connection failed - check credentials")
```

### Query Timeout

All queries have a **5-second timeout** by default. Adjust if needed:

```python
results = rag.execute_query(query, params, timeout=10)  # 10 seconds
```

### View Available Queries

```python
from larry_cypher_queries import CYPHER_QUERIES

print(f"Available queries: {len(CYPHER_QUERIES)}")
for query_name in CYPHER_QUERIES.keys():
    print(f"  - {query_name}")
```

---

## Performance Notes

- **Connection Pooling**: Automatically managed by Neo4j driver
- **Query Timeout**: 5 seconds default (prevents hanging)
- **Connection Timeout**: 5 seconds for acquiring connections
- **Max Connection Lifetime**: 30 seconds
- **Auto-cleanup**: Context manager pattern ensures connections close

---

## Next Steps

1. **Initialize Schema** - Run `neo4j_schema_init.py`
2. **Verify Installation** - Check node and relationship counts
3. **Test Queries** - Run `larry_neo4j_rag_v2.py` test suite
4. **Add Content** - Import document chunks from PWS materials
5. **Re-enable in Larry** - Update `larry_tools.py` to use v2 system
6. **Deploy** - Push to Streamlit Cloud with Neo4j secrets

---

## Schema Visualization

```
    (Student)      (Entrepreneur)    (Corporate)
        |                |                |
      [USES]          [USES]          [USES]
        |                |                |
        v                v                v
  (Design Thinking) (Mom Test)  (Three Box Solution)
        |                |                |
    [ADDRESSES]      [ADDRESSES]      [ADDRESSES]
        |                |                |
        v                v                v
  (Ill-Defined)    (Well-Defined)    (Undefined)
        ^                ^                ^
        |                |                |
    Time: 1-5y       Time: <1y       Time: 5-20y
   Uncertainty:    Uncertainty:    Uncertainty:
     MEDIUM            LOW            HIGH
```

---

**Questions?** Check the test suite in `larry_neo4j_rag_v2.py` or run the schema initializer with `--help` flag.
