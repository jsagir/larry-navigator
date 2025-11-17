import os
from neo4j import GraphDatabase, basic_auth
from google import genai
from google.genai import types

# --- Configuration ---
# Neo4j connection details will be loaded from environment variables/secrets
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# --- Neo4j Connection ---
def get_neo4j_driver():
    """Initializes and returns the Neo4j driver."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        return None
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        return driver
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
        return None

# --- Cypher Generation and Querying ---

def generate_cypher_query(user_message, persona, problem_type, api_key):
    """
    Uses the Gemini model to translate a natural language query into a Cypher query.
    This is the core of the "Network-Effect" RAG.
    """
    if not api_key:
        return None, "Error: Gemini API key is missing for Cypher generation."

    # System instruction for the Cypher generation model
    cypher_system_prompt = f"""
    You are an expert Neo4j Cypher query generator. Your task is to translate a user's question into a single, valid, read-only Cypher query.
    The database schema is unknown, so you must use generic graph traversal patterns.
    The user's context is: Persona: {persona}, Problem Type: {problem_type}.
    Focus on retrieving relevant nodes and relationships that could answer the question.
    DO NOT make up properties or labels. Use `MATCH (n)-[r]-(m)` for general traversal.
    The query MUST start with `MATCH` and end with `RETURN`.
    DO NOT include any explanation or text outside of the Cypher query itself.
    Example: MATCH (n) WHERE n.name CONTAINS 'innovation' RETURN n LIMIT 5
    """

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=cypher_system_prompt,
                temperature=0.0, # Low temperature for deterministic output
            )
        )
        # Clean up the response to ensure it's just the Cypher query
        cypher_query = response.text.strip()
        if cypher_query.startswith("```cypher"):
            cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
        elif cypher_query.startswith("```"):
            cypher_query = cypher_query.replace("```", "").strip()

        return cypher_query, None

    except Exception as e:
        return None, f"Error generating Cypher: {e}"

def execute_cypher_query(driver, cypher_query):
    """Executes the Cypher query and formats the results."""
    if not driver:
        return "Error: Neo4j driver is not initialized."

    def run_query(tx):
        result = tx.run(cypher_query)
        # Convert results to a list of dictionaries for easy consumption
        return [record.data() for record in result]

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.execute_read(run_query)

        # Format results into a string for the main RAG prompt
        formatted_results = f"Neo4j Graph RAG (Network-Effect) Results for Query: '{cypher_query}'\n\n"
        if not results:
            formatted_results += "No relevant graph data found."
        else:
            for i, record in enumerate(results):
                formatted_results += f"--- Record {i+1} ---\n"
                for key, value in record.items():
                    # Simple formatting for nodes/relationships
                    if isinstance(value, dict) and 'properties' in value:
                        formatted_results += f"{key}: Node/Relationship with properties: {value['properties']}\n"
                    else:
                        formatted_results += f"{key}: {value}\n"
                if i >= 4: # Limit to 5 records for brevity in the prompt
                    formatted_results += f"... and {len(results) - i - 1} more records.\n"
                    break

        return formatted_results

    except Exception as e:
        return f"Error executing Cypher query: {e}"

def get_neo4j_rag_context(user_message, persona, problem_type, api_key):
    """Main function to get context from Neo4j."""
    driver = get_neo4j_driver()
    if not driver:
        return None, "Neo4j is not configured or connection failed."

    # 1. Generate Cypher
    cypher_query, error = generate_cypher_query(user_message, persona, problem_type, api_key)
    if error:
        return None, error

    # 2. Execute Cypher
    rag_context = execute_cypher_query(driver, cypher_query)

    # 3. Close driver (optional, but good practice)
    driver.close()

    return rag_context, None

# --- Status Check ---
def is_neo4j_configured():
    """Checks if the necessary environment variables are set."""
    return all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD])

if __name__ == '__main__':
    # Example usage (requires environment variables to be set)
    if is_neo4j_configured():
        test_message = "What are the key relationships between innovation and risk management?"
        context, error = get_neo4j_rag_context(test_message, "corporate", "ill-defined", "YOUR_GEMINI_API_KEY")
        if error:
            print(f"Test Error: {error}")
        else:
            print("--- Neo4j RAG Context ---")
            print(context)
    else:
        print("Neo4j environment variables are not set. Cannot run test.")
