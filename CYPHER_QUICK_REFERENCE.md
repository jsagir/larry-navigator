# Larry Navigator - Cypher Query Quick Reference

## 🎯 Framework Discovery Queries

### 1. Find Frameworks by Problem Type
**Use when:** User asks "Which framework for [problem type]?"

```cypher
MATCH (f:Framework)-[:ADDRESSES]->(pt:ProblemType {name: $problem_type})
OPTIONAL MATCH (a:Author)-[:CREATED]->(f)
RETURN f.name, f.description, f.difficulty, collect(a.name) AS authors
ORDER BY f.difficulty
LIMIT 5
```
**Parameters:** `problem_type` = "Undefined" | "Ill-Defined" | "Well-Defined" | "Wicked"

---

### 2. Find Frameworks by Persona
**Use when:** User asks "What frameworks for [persona]?"

```cypher
MATCH (p:Persona {name: $persona})-[:USES]->(f:Framework)
OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
RETURN f.name, f.description, f.difficulty, collect(pt.name) AS problem_types
ORDER BY f.difficulty
LIMIT 5
```
**Parameters:** `persona` = "Student" | "Entrepreneur" | "Corporate" | "Consultant" | "Researcher" | "Nonprofit Leader"

---

### 3. Find Beginner Frameworks
**Use when:** User is new to innovation frameworks

```cypher
MATCH (f:Framework {difficulty: 'BEGINNER'})
OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
RETURN f.name, f.description, f.time_required, collect(pt.name) AS suitable_for
ORDER BY f.time_required
LIMIT 5
```

---

### 4. Find Related Frameworks
**Use when:** User asks "What's similar to [framework]?"

```cypher
MATCH (f:Framework {name: $framework_name})
OPTIONAL MATCH (f)-[r:COMPLEMENTS|BUILDS_ON|REQUIRES]-(related:Framework)
RETURN related.name, type(r) AS relationship, related.description
LIMIT 5
```
**Parameters:** `framework_name` = Any framework name

---

## 🔍 Problem Type Classification

### 5. Classify by Time Horizon
**Use when:** User describes a time horizon

```cypher
MATCH (pt:ProblemType)
WHERE pt.time_horizon = $time_horizon
OPTIONAL MATCH (f:Framework)-[:ADDRESSES]->(pt)
RETURN pt.name, pt.description, pt.uncertainty_level,
       collect(f.name) AS recommended_frameworks
LIMIT 1
```
**Parameters:** `time_horizon` = "5-20 years" | "1-5 years" | "<1 year" | "Variable"

---

### 6. Get Problem Type Details
**Use when:** User asks about a specific problem type

```cypher
MATCH (pt:ProblemType {name: $problem_type})
OPTIONAL MATCH (f:Framework)-[:ADDRESSES]->(pt)
OPTIONAL MATCH (p:Persona)-[:USES]->(f)
RETURN pt.name, pt.description, pt.time_horizon, pt.uncertainty_level,
       pt.characteristics, pt.tools, collect(DISTINCT f.name) AS frameworks,
       collect(DISTINCT p.name) AS common_personas
```
**Parameters:** `problem_type` = Problem type name

---

## 📚 Concept & Knowledge Discovery

### 7. Search Concepts by Keyword
**Use when:** User searches for a concept

```cypher
CALL db.index.fulltext.queryNodes('concept_search', $search_term)
YIELD node, score
MATCH (node:Concept)
OPTIONAL MATCH (node)-[:RELATED_TO]-(related:Concept)
OPTIONAL MATCH (node)-[:USED_IN]->(f:Framework)
RETURN node.name, node.description, collect(DISTINCT related.name)[..3],
       collect(DISTINCT f.name)[..3], score
ORDER BY score DESC
LIMIT 5
```
**Parameters:** `search_term` = Search keywords

---

### 8. Find Document Chunks
**Use when:** Searching for specific content

```cypher
CALL db.index.fulltext.queryNodes('document_search', $search_term)
YIELD node, score
MATCH (node:DocumentChunk)
RETURN node.chunk_id, node.content, node.source_file, node.document_type,
       node.frameworks, node.problem_types, score
ORDER BY score DESC
LIMIT 3
```
**Parameters:** `search_term` = Search keywords

---

## 👤 Author & Book Queries

### 9. Find Authors by Expertise
**Use when:** User asks about thought leaders

```cypher
MATCH (a:Author)
WHERE a.expertise CONTAINS $expertise
OPTIONAL MATCH (a)-[:WROTE]->(b:Book)
OPTIONAL MATCH (a)-[:CREATED]->(f:Framework)
RETURN a.name, a.expertise, a.books, collect(DISTINCT f.name) AS frameworks
LIMIT 5
```
**Parameters:** `expertise` = Expertise area keyword

---

### 10. Get Book Information
**Use when:** User asks about a book

```cypher
MATCH (b:Book)
WHERE b.title CONTAINS $book_title
OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
OPTIONAL MATCH (b)-[:DISCUSSES]->(c:Concept)
OPTIONAL MATCH (b)-[:INTRODUCES]->(f:Framework)
RETURN b.title, a.name, b.publication_year,
       collect(DISTINCT c.name)[..5], collect(DISTINCT f.name)
LIMIT 1
```
**Parameters:** `book_title` = Book title or keyword

---

## 📊 Portfolio & Innovation Horizon

### 11. Get Portfolio Horizon Frameworks
**Use when:** User asks about Now/New/Next

```cypher
MATCH (h:PortfolioHorizon {name: $horizon})
MATCH (pt:ProblemType)<-[:ADDRESSES]-(f:Framework)
WHERE
    (h.name = 'Now' AND pt.name = 'Well-Defined') OR
    (h.name = 'New' AND pt.name = 'Ill-Defined') OR
    (h.name = 'Next' AND pt.name IN ['Undefined', 'Ill-Defined'])
RETURN h.name, h.resource_allocation, h.time_frame,
       collect(DISTINCT f.name), collect(DISTINCT pt.name)
```
**Parameters:** `horizon` = "Now" | "New" | "Next"

---

### 12. Portfolio Recommendations
**Use when:** User asks about portfolio balance

```cypher
MATCH (h:PortfolioHorizon)
OPTIONAL MATCH (h)<-[:FITS_IN]-(f:Framework)
RETURN h.name, h.description, h.resource_allocation, h.time_frame,
       collect(DISTINCT f.name) AS example_frameworks
ORDER BY CASE h.name WHEN 'Now' THEN 1 WHEN 'New' THEN 2 WHEN 'Next' THEN 3 END
```

---

## 🎓 Learning Paths & Recommendations

### 13. Learning Path for Persona
**Use when:** User asks "Where should I start?"

```cypher
MATCH (p:Persona {name: $persona})-[:USES]->(f:Framework)
MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
WITH f, pt, p,
    CASE f.difficulty
        WHEN 'BEGINNER' THEN 1
        WHEN 'INTERMEDIATE' THEN 2
        WHEN 'ADVANCED' THEN 3
    END AS difficulty_order
RETURN f.name, f.difficulty, f.description, pt.name, f.time_required
ORDER BY difficulty_order, f.time_required
LIMIT 5
```
**Parameters:** `persona` = Persona name

---

### 14. Prerequisite Frameworks
**Use when:** User asks "What do I need to learn first?"

```cypher
MATCH (f:Framework {name: $framework_name})
MATCH path = (prereq:Framework)-[:BUILDS_ON|REQUIRES*1..2]->(f)
RETURN prereq.name, prereq.description, prereq.difficulty, length(path) AS steps_away
ORDER BY steps_away, prereq.difficulty
```
**Parameters:** `framework_name` = Target framework

---

## 📖 Case Studies & Examples

### 15. Find Case Studies
**Use when:** User asks for real examples

```cypher
MATCH (cs:CaseStudy)-[:DEMONSTRATES]->(f:Framework {name: $framework_name})
OPTIONAL MATCH (cs)-[:INVOLVES]->(c:Company)
RETURN cs.title, cs.description, cs.outcome, cs.industry, c.name
ORDER BY cs.success_level DESC
LIMIT 3
```
**Parameters:** `framework_name` = Framework name

---

## 🚀 Advanced Queries

### 16. Discover Framework Clusters
**Use when:** Exploring related frameworks

```cypher
MATCH (f:Framework {name: $framework_name})
CALL apoc.path.subgraphNodes(f, {
    relationshipFilter: "COMPLEMENTS|BUILDS_ON|REQUIRES",
    maxLevel: 2
})
YIELD node
MATCH (node)-[:ADDRESSES]->(pt:ProblemType)
RETURN node.name, node.description, collect(DISTINCT pt.name)
LIMIT 8
```
**Parameters:** `framework_name` = Starting framework

---

### 17. Find by Multiple Criteria
**Use when:** Complex filtering needed

```cypher
MATCH (f:Framework)
WHERE f.difficulty = $difficulty
  AND f.time_required CONTAINS $time_constraint
MATCH (f)-[:ADDRESSES]->(pt:ProblemType {name: $problem_type})
MATCH (p:Persona {name: $persona})-[:USES]->(f)
RETURN f.name, f.description, f.team_size, pt.name
LIMIT 5
```
**Parameters:**
- `difficulty` = "BEGINNER" | "INTERMEDIATE" | "ADVANCED"
- `time_constraint` = Time period keyword
- `problem_type` = Problem type
- `persona` = Persona name

---

### 18. Semantic Framework Search
**Use when:** General/fuzzy search

```cypher
CALL db.index.fulltext.queryNodes('framework_search', $search_query)
YIELD node, score
MATCH (node:Framework)
OPTIONAL MATCH (node)-[:ADDRESSES]->(pt:ProblemType)
OPTIONAL MATCH (p:Persona)-[:USES]->(node)
RETURN node.name, node.description, node.difficulty,
       collect(DISTINCT pt.name), collect(DISTINCT p.name), score
ORDER BY score DESC
LIMIT 5
```
**Parameters:** `search_query` = Free text search

---

## 🔬 Diagnostic Queries

### 19. Diagnose Problem and Recommend
**Use when:** Comprehensive analysis needed

```cypher
MATCH (pt:ProblemType)
WHERE pt.time_horizon = $time_horizon
MATCH (f:Framework)-[:ADDRESSES]->(pt)
MATCH (p:Persona {name: $persona})-[:USES]->(f)
WITH f, pt, p,
    CASE f.difficulty
        WHEN 'BEGINNER' THEN 1
        WHEN 'INTERMEDIATE' THEN 2
        WHEN 'ADVANCED' THEN 3
    END AS difficulty_score
RETURN pt.name, pt.description, pt.uncertainty_level,
       f.name AS recommended_framework, f.description, f.difficulty,
       f.time_required, pt.tools AS alternative_tools
ORDER BY difficulty_score
LIMIT 3
```
**Parameters:**
- `time_horizon` = Time horizon
- `persona` = Persona name

---

## ✨ Content Enrichment

### 20. Enrich Response with Context
**Use when:** Need comprehensive framework information

```cypher
MATCH (f:Framework {name: $framework_name})
OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
OPTIONAL MATCH (p:Persona)-[:USES]->(f)
OPTIONAL MATCH (a:Author)-[:CREATED]->(f)
OPTIONAL MATCH (f)-[rel:COMPLEMENTS|BUILDS_ON]-(related:Framework)
OPTIONAL MATCH (cs:CaseStudy)-[:DEMONSTRATES]->(f)
RETURN f.name, f.description, f.difficulty, f.time_required, f.team_size,
       collect(DISTINCT pt.name), collect(DISTINCT pt.characteristics),
       collect(DISTINCT p.name), collect(DISTINCT a.name),
       collect(DISTINCT {name: related.name, relationship: type(rel)}),
       collect(DISTINCT cs.title)[..2]
```
**Parameters:** `framework_name` = Framework name

---

## 🎨 Visual Schema Reference

```
NODE TYPES                  RELATIONSHIPS

Framework ●─────┐          ─[:ADDRESSES]→      Links framework to problem type
ProblemType ●   │          ─[:USES]→           Links persona to framework
Persona ●       │          ─[:CREATED]→        Links author to framework
Author ●────────┤          ─[:WROTE]→          Links author to book
Book ●          │          ─[:COMPLEMENTS]→    Related frameworks
Concept ●       │          ─[:BUILDS_ON]→      Dependent frameworks
Method ●        │          ─[:REQUIRES]→       Prerequisite frameworks
Topic ●         │          ─[:DEMONSTRATES]→   Links case study to framework
CaseStudy ●     │          ─[:DISCUSSES]→      Links content to concepts
DocumentChunk ●─┘          ─[:INTRODUCES]→     Links book to framework
PortfolioHorizon ●
```

---

## 📋 Common Parameter Values

### Problem Types
- `Undefined` - 5-20 year horizon, HIGH uncertainty
- `Ill-Defined` - 1-5 year horizon, MEDIUM uncertainty
- `Well-Defined` - <1 year horizon, LOW uncertainty
- `Wicked` - Variable horizon, VERY HIGH uncertainty

### Personas
- `Student` - Academic learning
- `Entrepreneur` - Action-oriented, startup focus
- `Corporate` - Strategic, portfolio management
- `Consultant` - Prescriptive, client advisory
- `Researcher` - Analytical, theory focus
- `Nonprofit Leader` - Mission-driven, impact focus

### Difficulty Levels
- `BEGINNER` - Easy to learn, quick to implement
- `INTERMEDIATE` - Moderate complexity
- `ADVANCED` - Complex, requires expertise

### Portfolio Horizons
- `Now` - 0-12 months, 70% resources, incremental
- `New` - 1-3 years, 20% resources, adjacent
- `Next` - 3-5 years, 10% resources, disruptive

---

## 🔧 Query Tips

1. **Use LIMIT** - Always limit results to avoid large result sets
2. **Use OPTIONAL MATCH** - For relationships that may not exist
3. **Order Results** - Use ORDER BY for consistent, useful ordering
4. **Collect Aggregations** - Use `collect()` to group related data
5. **Full-text Search** - Use indexed searches for keyword matching
6. **Timeout Awareness** - Keep queries under 5 seconds

---

**Pro Tip:** Test queries in Neo4j Browser before using in code!
