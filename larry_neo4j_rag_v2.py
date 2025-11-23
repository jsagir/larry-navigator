"""
Larry Neo4j RAG v2 - Using Pre-built Cypher Queries
Much faster and more reliable than LLM-generated queries
"""

import os
from neo4j import GraphDatabase
from larry_cypher_queries import CYPHER_QUERIES, select_query_for_question

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Connection timeout settings
QUERY_TIMEOUT = 5  # 5 seconds max per query


class LarryNeo4jRAG:
    """Fast, reliable Neo4j RAG using pre-built queries"""

    def __init__(self, uri=None, user=None, password=None, database="neo4j"):
        """Initialize Neo4j connection with timeout"""
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        self.database = database
        self.driver = None

        if self.is_configured():
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_lifetime=30,
                    connection_acquisition_timeout=5
                )
                # Test connection
                with self.driver.session(database=self.database) as session:
                    session.run("RETURN 1", timeout=1)
            except Exception as e:
                print(f"Neo4j connection failed: {e}")
                self.driver = None

    def is_configured(self):
        """Check if Neo4j credentials are available"""
        return all([self.uri, self.user, self.password])

    def close(self):
        """Close the driver connection"""
        if self.driver:
            self.driver.close()

    def execute_query(self, query, parameters=None, timeout=QUERY_TIMEOUT):
        """
        Execute a Cypher query with timeout

        Args:
            query: Cypher query string
            parameters: Query parameters dict
            timeout: Query timeout in seconds

        Returns:
            List of records or None if error
        """
        if not self.driver:
            return None

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {}, timeout=timeout)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Query execution error: {e}")
            return None

    def get_rag_context(self, user_message, persona="general", problem_type="general"):
        """
        Get RAG context using intelligent query selection

        Args:
            user_message: User's question
            persona: Detected persona
            problem_type: Detected problem type

        Returns:
            Formatted context string or None
        """
        if not self.driver:
            return None

        try:
            # Select the best query for this question
            query_name, query, suggested_params = select_query_for_question(
                user_message, persona, problem_type
            )

            print(f"Neo4j RAG: Using query '{query_name}' with params {suggested_params}")

            # Execute the query
            results = self.execute_query(query, suggested_params)

            if not results:
                return None

            # Format results into readable context
            context = self._format_results(query_name, results)
            return context

        except Exception as e:
            print(f"RAG context error: {e}")
            return None

    def _format_results(self, query_name, results):
        """Format query results into readable context"""

        if not results:
            return "No relevant information found in knowledge graph."

        # Different formatting based on query type
        if "framework" in query_name.lower():
            return self._format_framework_results(results)
        elif "problem_type" in query_name.lower():
            return self._format_problem_type_results(results)
        elif "author" in query_name.lower():
            return self._format_author_results(results)
        elif "portfolio" in query_name.lower():
            return self._format_portfolio_results(results)
        elif "learning" in query_name.lower():
            return self._format_learning_path_results(results)
        else:
            return self._format_generic_results(results)

    def _format_framework_results(self, results):
        """Format framework query results"""
        context_parts = ["**Relevant Frameworks from Knowledge Graph:**\n"]

        for i, record in enumerate(results[:5], 1):
            framework = record.get('framework', 'Unknown')
            description = record.get('description', '')
            difficulty = record.get('difficulty', '')
            problem_types = record.get('problem_types', [])

            context_parts.append(f"{i}. **{framework}** ({difficulty})")
            if description:
                context_parts.append(f"   - {description}")
            if problem_types:
                context_parts.append(f"   - Addresses: {', '.join(problem_types)}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _format_problem_type_results(self, results):
        """Format problem type query results"""
        if not results:
            return "No problem type information found."

        record = results[0]
        problem_type = record.get('problem_type', 'Unknown')
        description = record.get('description', '')
        uncertainty = record.get('uncertainty_level', '')
        characteristics = record.get('characteristics', [])
        frameworks = record.get('frameworks', [])

        context_parts = [
            f"**Problem Type: {problem_type}**\n",
            f"{description}\n",
            f"**Uncertainty Level:** {uncertainty}",
            f"**Characteristics:** {', '.join(characteristics)}",
        ]

        if frameworks:
            context_parts.append(f"**Recommended Frameworks:** {', '.join(frameworks[:5])}")

        return "\n".join(context_parts)

    def _format_author_results(self, results):
        """Format author query results"""
        context_parts = ["**Author Information:**\n"]

        for record in results[:3]:
            author = record.get('author', 'Unknown')
            expertise = record.get('expertise', '')
            books = record.get('books', [])
            frameworks = record.get('frameworks', [])

            context_parts.append(f"**{author}** - {expertise}")
            if books:
                context_parts.append(f"  Key Books: {', '.join(books[:3])}")
            if frameworks:
                context_parts.append(f"  Associated Frameworks: {', '.join(frameworks)}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _format_portfolio_results(self, results):
        """Format portfolio horizon results"""
        context_parts = ["**Innovation Portfolio Horizons:**\n"]

        for record in results:
            horizon = record.get('horizon', 'Unknown')
            description = record.get('description', '')
            allocation = record.get('allocation', '')
            frameworks = record.get('frameworks', [])

            context_parts.append(f"**{horizon}** ({allocation})")
            context_parts.append(f"  {description}")
            if frameworks:
                context_parts.append(f"  Example Frameworks: {', '.join(frameworks[:3])}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _format_learning_path_results(self, results):
        """Format learning path results"""
        context_parts = ["**Recommended Learning Path:**\n"]

        for i, record in enumerate(results[:5], 1):
            framework = record.get('framework', 'Unknown')
            level = record.get('level', '')
            problem_type = record.get('problem_type', '')
            time = record.get('time_commitment', '')

            context_parts.append(f"{i}. {framework} ({level})")
            context_parts.append(f"   Problem Type: {problem_type} | Time: {time}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _format_generic_results(self, results):
        """Format generic query results"""
        context_parts = ["**Knowledge Graph Results:**\n"]

        for i, record in enumerate(results[:5], 1):
            # Get the most relevant fields
            main_field = None
            for key in ['framework', 'concept', 'name', 'title']:
                if key in record and record[key]:
                    main_field = record[key]
                    break

            if main_field:
                context_parts.append(f"{i}. {main_field}")

                # Add description if available
                description = record.get('description', '')
                if description:
                    context_parts.append(f"   {description}")

                context_parts.append("")

        return "\n".join(context_parts)

    def get_framework_details(self, framework_name):
        """Get detailed information about a specific framework"""
        query = CYPHER_QUERIES["enrich_response_with_context"]
        results = self.execute_query(query, {"framework_name": framework_name})

        if results and len(results) > 0:
            return results[0]
        return None

    def search_by_keyword(self, keyword):
        """Simple keyword search across all content"""
        query = CYPHER_QUERIES["semantic_framework_search"]
        results = self.execute_query(query, {"search_query": keyword})
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def is_neo4j_configured():
    """Check if Neo4j environment variables are set"""
    return all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD])


def get_neo4j_rag_context_fast(user_message, persona="general", problem_type="general"):
    """
    Quick function to get Neo4j RAG context
    Auto-manages connection and handles errors gracefully

    Returns:
        Formatted context string or None
    """
    if not is_neo4j_configured():
        return None

    rag = None
    try:
        rag = LarryNeo4jRAG()
        if rag.driver:
            context = rag.get_rag_context(user_message, persona, problem_type)
            return context
        return None
    except Exception as e:
        print(f"Neo4j RAG error: {e}")
        return None
    finally:
        if rag:
            rag.close()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Larry Neo4j RAG v2 - Test Suite")
    print("=" * 60)

    if not is_neo4j_configured():
        print("⚠ Neo4j not configured. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
        exit(1)

    # Test connection
    print("\n1. Testing connection...")
    rag = LarryNeo4jRAG()

    if rag.driver:
        print("✓ Connected to Neo4j")

        # Test queries
        test_cases = [
            ("Which framework should I use for undefined problems?", "Entrepreneur", "Undefined"),
            ("What's a good learning path for students?", "Student", None),
            ("Tell me about Design Thinking", None, None),
            ("How do I manage my innovation portfolio?", "Corporate", None),
        ]

        print("\n2. Testing queries...")
        for question, persona, problem_type in test_cases:
            print(f"\n{'='*60}")
            print(f"Q: {question}")
            print(f"Persona: {persona}, Problem Type: {problem_type}")
            print(f"{'='*60}")

            context = rag.get_rag_context(question, persona, problem_type)

            if context:
                print(context)
            else:
                print("No context returned")

        rag.close()
        print("\n✓ Test complete")
    else:
        print("✗ Failed to connect to Neo4j")
