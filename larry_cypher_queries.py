"""
Larry Navigator - Cypher Query Library
Pre-built, optimized Cypher queries for different question types and scenarios
"""

# ============================================================================
# QUERY LIBRARY - Organized by Use Case
# ============================================================================

CYPHER_QUERIES = {

    # ========================================================================
    # 1. FRAMEWORK DISCOVERY
    # ========================================================================

    "find_frameworks_by_problem_type": """
        // Find frameworks suitable for a specific problem type
        MATCH (f:Framework)-[:ADDRESSES]->(pt:ProblemType {name: $problem_type})
        OPTIONAL MATCH (a:Author)-[:CREATED]->(f)
        RETURN
            f.name AS framework,
            f.description AS description,
            f.difficulty AS difficulty,
            f.time_required AS time_required,
            f.team_size AS team_size,
            collect(DISTINCT a.name) AS authors
        ORDER BY
            CASE f.difficulty
                WHEN 'BEGINNER' THEN 1
                WHEN 'INTERMEDIATE' THEN 2
                WHEN 'ADVANCED' THEN 3
            END
        LIMIT 5
    """,

    "find_frameworks_by_persona": """
        // Find frameworks recommended for a specific persona
        MATCH (p:Persona {name: $persona})-[:USES]->(f:Framework)
        OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
        RETURN
            f.name AS framework,
            f.description AS description,
            f.difficulty AS difficulty,
            collect(DISTINCT pt.name) AS problem_types
        ORDER BY f.difficulty
        LIMIT 5
    """,

    "find_beginner_frameworks": """
        // Find beginner-friendly frameworks
        MATCH (f:Framework {difficulty: 'BEGINNER'})
        OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
        RETURN
            f.name AS framework,
            f.description AS description,
            f.time_required AS time_required,
            collect(DISTINCT pt.name) AS suitable_for
        ORDER BY f.time_required
        LIMIT 5
    """,

    "find_related_frameworks": """
        // Find frameworks related to a given framework
        MATCH (f:Framework {name: $framework_name})
        OPTIONAL MATCH (f)-[r:COMPLEMENTS|BUILDS_ON|REQUIRES]-(related:Framework)
        RETURN
            related.name AS framework,
            type(r) AS relationship,
            related.description AS description,
            related.difficulty AS difficulty
        LIMIT 5
    """,

    # ========================================================================
    # 2. PROBLEM TYPE CLASSIFICATION
    # ========================================================================

    "classify_by_time_horizon": """
        // Classify problem by time horizon
        MATCH (pt:ProblemType)
        WHERE pt.time_horizon = $time_horizon
        OPTIONAL MATCH (f:Framework)-[:ADDRESSES]->(pt)
        RETURN
            pt.name AS problem_type,
            pt.description AS description,
            pt.uncertainty_level AS uncertainty,
            pt.characteristics AS characteristics,
            collect(DISTINCT f.name) AS recommended_frameworks
        LIMIT 1
    """,

    "get_problem_type_details": """
        // Get detailed information about a problem type
        MATCH (pt:ProblemType {name: $problem_type})
        OPTIONAL MATCH (f:Framework)-[:ADDRESSES]->(pt)
        OPTIONAL MATCH (p:Persona)-[:USES]->(f)
        RETURN
            pt.name AS problem_type,
            pt.description AS description,
            pt.time_horizon AS time_horizon,
            pt.uncertainty_level AS uncertainty_level,
            pt.characteristics AS characteristics,
            pt.tools AS recommended_tools,
            collect(DISTINCT f.name) AS frameworks,
            collect(DISTINCT p.name) AS common_personas
    """,

    # ========================================================================
    # 3. CONCEPT & KNOWLEDGE DISCOVERY
    # ========================================================================

    "search_concepts_by_keyword": """
        // Full-text search across concepts
        CALL db.index.fulltext.queryNodes('concept_search', $search_term)
        YIELD node, score
        MATCH (node:Concept)
        OPTIONAL MATCH (node)-[:RELATED_TO]-(related:Concept)
        OPTIONAL MATCH (node)-[:USED_IN]->(f:Framework)
        RETURN
            node.name AS concept,
            node.description AS description,
            collect(DISTINCT related.name)[..3] AS related_concepts,
            collect(DISTINCT f.name)[..3] AS used_in_frameworks,
            score
        ORDER BY score DESC
        LIMIT 5
    """,

    "find_document_chunks": """
        // Find relevant document chunks by content
        CALL db.index.fulltext.queryNodes('document_search', $search_term)
        YIELD node, score
        MATCH (node:DocumentChunk)
        RETURN
            node.chunk_id AS chunk_id,
            node.content AS content,
            node.source_file AS source,
            node.document_type AS type,
            node.frameworks AS frameworks,
            node.problem_types AS problem_types,
            score
        ORDER BY score DESC
        LIMIT 3
    """,

    # ========================================================================
    # 4. AUTHOR & BOOK QUERIES
    # ========================================================================

    "find_authors_by_expertise": """
        // Find authors by expertise area
        MATCH (a:Author)
        WHERE a.expertise CONTAINS $expertise
        OPTIONAL MATCH (a)-[:WROTE]->(b:Book)
        OPTIONAL MATCH (a)-[:CREATED]->(f:Framework)
        RETURN
            a.name AS author,
            a.expertise AS expertise,
            a.books AS books,
            collect(DISTINCT f.name) AS frameworks
        LIMIT 5
    """,

    "get_book_information": """
        // Get information about a specific book
        MATCH (b:Book)
        WHERE b.title CONTAINS $book_title
        OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
        OPTIONAL MATCH (b)-[:DISCUSSES]->(c:Concept)
        OPTIONAL MATCH (b)-[:INTRODUCES]->(f:Framework)
        RETURN
            b.title AS title,
            a.name AS author,
            b.publication_year AS year,
            collect(DISTINCT c.name)[..5] AS key_concepts,
            collect(DISTINCT f.name) AS frameworks
        LIMIT 1
    """,

    # ========================================================================
    # 5. PORTFOLIO & INNOVATION HORIZON
    # ========================================================================

    "get_portfolio_horizon_frameworks": """
        // Find frameworks suitable for a portfolio horizon
        MATCH (h:PortfolioHorizon {name: $horizon})
        MATCH (pt:ProblemType)<-[:ADDRESSES]-(f:Framework)
        WHERE
            (h.name = 'Now' AND pt.name = 'Well-Defined') OR
            (h.name = 'New' AND pt.name = 'Ill-Defined') OR
            (h.name = 'Next' AND pt.name IN ['Undefined', 'Ill-Defined'])
        RETURN
            h.name AS horizon,
            h.resource_allocation AS allocation,
            h.time_frame AS timeframe,
            collect(DISTINCT f.name) AS frameworks,
            collect(DISTINCT pt.name) AS problem_types
    """,

    "portfolio_recommendations": """
        // Get balanced portfolio recommendations
        MATCH (h:PortfolioHorizon)
        OPTIONAL MATCH (h)<-[:FITS_IN]-(f:Framework)
        RETURN
            h.name AS horizon,
            h.description AS description,
            h.resource_allocation AS recommended_allocation,
            h.time_frame AS timeframe,
            collect(DISTINCT f.name) AS example_frameworks
        ORDER BY
            CASE h.name
                WHEN 'Now' THEN 1
                WHEN 'New' THEN 2
                WHEN 'Next' THEN 3
            END
    """,

    # ========================================================================
    # 6. LEARNING PATHS & RECOMMENDATIONS
    # ========================================================================

    "learning_path_for_persona": """
        // Generate a learning path for a specific persona
        MATCH (p:Persona {name: $persona})-[:USES]->(f:Framework)
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
    """,

    "prerequisite_frameworks": """
        // Find prerequisite or foundational frameworks
        MATCH (f:Framework {name: $framework_name})
        MATCH path = (prereq:Framework)-[:BUILDS_ON|REQUIRES*1..2]->(f)
        RETURN
            prereq.name AS prerequisite,
            prereq.description AS description,
            prereq.difficulty AS difficulty,
            length(path) AS steps_away
        ORDER BY steps_away, prereq.difficulty
    """,

    # ========================================================================
    # 7. CASE STUDIES & EXAMPLES
    # ========================================================================

    "find_case_studies": """
        // Find case studies related to a framework or concept
        MATCH (cs:CaseStudy)-[:DEMONSTRATES]->(f:Framework {name: $framework_name})
        OPTIONAL MATCH (cs)-[:INVOLVES]->(c:Company)
        RETURN
            cs.title AS case_study,
            cs.description AS description,
            cs.outcome AS outcome,
            cs.industry AS industry,
            c.name AS company
        ORDER BY cs.success_level DESC
        LIMIT 3
    """,

    # ========================================================================
    # 8. ADVANCED QUERIES - NETWORK EFFECTS
    # ========================================================================

    "discover_framework_clusters": """
        // Find clusters of related frameworks
        MATCH (f:Framework {name: $framework_name})
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
    """,

    "find_by_multiple_criteria": """
        // Find frameworks matching multiple criteria
        MATCH (f:Framework)
        WHERE
            f.difficulty = $difficulty
            AND f.time_required CONTAINS $time_constraint
        MATCH (f)-[:ADDRESSES]->(pt:ProblemType {name: $problem_type})
        MATCH (p:Persona {name: $persona})-[:USES]->(f)
        RETURN
            f.name AS framework,
            f.description AS description,
            f.team_size AS team_size,
            pt.name AS problem_type
        LIMIT 5
    """,

    "semantic_framework_search": """
        // Semantic search across frameworks
        CALL db.index.fulltext.queryNodes('framework_search', $search_query)
        YIELD node, score
        MATCH (node:Framework)
        OPTIONAL MATCH (node)-[:ADDRESSES]->(pt:ProblemType)
        OPTIONAL MATCH (p:Persona)-[:USES]->(node)
        RETURN
            node.name AS framework,
            node.description AS description,
            node.difficulty AS difficulty,
            collect(DISTINCT pt.name) AS problem_types,
            collect(DISTINCT p.name) AS personas,
            score
        ORDER BY score DESC
        LIMIT 5
    """,

    # ========================================================================
    # 9. DIAGNOSTIC QUERIES
    # ========================================================================

    "diagnose_problem_and_recommend": """
        // Comprehensive diagnostic based on user context
        // Parameters: $keywords (list), $time_horizon, $persona
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

        RETURN
            pt.name AS problem_type,
            pt.description AS problem_description,
            pt.uncertainty_level AS uncertainty,
            f.name AS recommended_framework,
            f.description AS framework_description,
            f.difficulty AS difficulty,
            f.time_required AS time_required,
            pt.tools AS alternative_tools
        ORDER BY difficulty_score
        LIMIT 3
    """,

    # ========================================================================
    # 10. CONTENT ENRICHMENT
    # ========================================================================

    "enrich_response_with_context": """
        // Get rich context for a framework to enrich responses
        MATCH (f:Framework {name: $framework_name})
        OPTIONAL MATCH (f)-[:ADDRESSES]->(pt:ProblemType)
        OPTIONAL MATCH (p:Persona)-[:USES]->(f)
        OPTIONAL MATCH (a:Author)-[:CREATED]->(f)
        OPTIONAL MATCH (f)-[rel:COMPLEMENTS|BUILDS_ON]-(related:Framework)
        OPTIONAL MATCH (cs:CaseStudy)-[:DEMONSTRATES]->(f)

        RETURN
            f.name AS framework,
            f.description AS description,
            f.difficulty AS difficulty,
            f.time_required AS time_required,
            f.team_size AS team_size,
            collect(DISTINCT pt.name) AS addresses_problem_types,
            collect(DISTINCT pt.characteristics) AS problem_characteristics,
            collect(DISTINCT p.name) AS used_by_personas,
            collect(DISTINCT a.name) AS created_by,
            collect(DISTINCT {name: related.name, relationship: type(rel)}) AS related_frameworks,
            collect(DISTINCT cs.title)[..2] AS example_cases
    """
}


# ============================================================================
# QUERY PARAMETER TEMPLATES
# ============================================================================

PARAMETER_TEMPLATES = {
    "find_frameworks_by_problem_type": {
        "problem_type": ["Undefined", "Ill-Defined", "Well-Defined", "Wicked"]
    },
    "find_frameworks_by_persona": {
        "persona": ["Student", "Entrepreneur", "Corporate", "Consultant", "Researcher", "Nonprofit Leader"]
    },
    "classify_by_time_horizon": {
        "time_horizon": ["5-20 years", "1-5 years", "<1 year", "Variable"]
    },
    "get_portfolio_horizon_frameworks": {
        "horizon": ["Now", "New", "Next"]
    },
    "find_by_multiple_criteria": {
        "difficulty": ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
        "time_constraint": ["1-2 weeks", "2-4 weeks", "2-3 months", "3-6 months"],
        "problem_type": ["Undefined", "Ill-Defined", "Well-Defined", "Wicked"],
        "persona": ["Student", "Entrepreneur", "Corporate", "Consultant", "Researcher", "Nonprofit Leader"]
    }
}


# ============================================================================
# QUERY SELECTOR - Smart Query Selection
# ============================================================================

def select_query_for_question(question_text, persona=None, problem_type=None):
    """
    Intelligently select the best Cypher query based on question characteristics

    Args:
        question_text: User's question
        persona: Detected persona (optional)
        problem_type: Detected problem type (optional)

    Returns:
        tuple: (query_name, query_text, suggested_parameters)
    """
    question_lower = question_text.lower()

    # Framework discovery questions
    if any(word in question_lower for word in ["which framework", "what framework", "recommend framework"]):
        if problem_type:
            return (
                "find_frameworks_by_problem_type",
                CYPHER_QUERIES["find_frameworks_by_problem_type"],
                {"problem_type": problem_type}
            )
        elif persona:
            return (
                "find_frameworks_by_persona",
                CYPHER_QUERIES["find_frameworks_by_persona"],
                {"persona": persona}
            )
        else:
            return (
                "find_beginner_frameworks",
                CYPHER_QUERIES["find_beginner_frameworks"],
                {}
            )

    # Problem type classification
    if any(word in question_lower for word in ["what type of problem", "classify", "problem type"]):
        return (
            "get_problem_type_details",
            CYPHER_QUERIES["get_problem_type_details"],
            {"problem_type": problem_type or "Ill-Defined"}
        )

    # Related frameworks
    if any(word in question_lower for word in ["related to", "similar to", "complements"]):
        # Extract framework name from question (simplified)
        for fw in ["Design Thinking", "Jobs-to-be-Done", "Blue Ocean", "Lean Startup"]:
            if fw.lower() in question_lower:
                return (
                    "find_related_frameworks",
                    CYPHER_QUERIES["find_related_frameworks"],
                    {"framework_name": fw}
                )

    # Learning path
    if any(word in question_lower for word in ["learning path", "where to start", "progression"]):
        return (
            "learning_path_for_persona",
            CYPHER_QUERIES["learning_path_for_persona"],
            {"persona": persona or "Entrepreneur"}
        )

    # Portfolio questions
    if any(word in question_lower for word in ["portfolio", "now new next", "three box"]):
        return (
            "portfolio_recommendations",
            CYPHER_QUERIES["portfolio_recommendations"],
            {}
        )

    # Case studies
    if any(word in question_lower for word in ["example", "case study", "real world"]):
        return (
            "find_case_studies",
            CYPHER_QUERIES["find_case_studies"],
            {"framework_name": "Design Thinking"}  # Default
        )

    # Default: semantic search
    return (
        "semantic_framework_search",
        CYPHER_QUERIES["semantic_framework_search"],
        {"search_query": question_text}
    )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("Larry Cypher Query Library")
    print("=" * 60)
    print(f"Total queries available: {len(CYPHER_QUERIES)}")
    print("\nQuery categories:")

    categories = {
        "Framework Discovery": 4,
        "Problem Type Classification": 2,
        "Concept & Knowledge Discovery": 2,
        "Author & Book Queries": 2,
        "Portfolio & Innovation Horizon": 2,
        "Learning Paths & Recommendations": 2,
        "Case Studies & Examples": 1,
        "Advanced Queries": 3,
        "Diagnostic Queries": 1,
        "Content Enrichment": 1
    }

    for category, count in categories.items():
        print(f"  - {category}: {count} queries")

    print("\n" + "=" * 60)
    print("Query selection examples:")

    test_questions = [
        ("Which framework should I use for undefined problems?", "Entrepreneur", "Undefined"),
        ("What's a good learning path for students?", "Student", None),
        ("Tell me about Design Thinking", None, None),
    ]

    for question, persona, problem_type in test_questions:
        query_name, _, params = select_query_for_question(question, persona, problem_type)
        print(f"\nQ: {question}")
        print(f"   Selected: {query_name}")
        print(f"   Parameters: {params}")
