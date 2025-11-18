import os
from neo4j import GraphDatabase, basic_auth
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate

# --- Configuration ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# --- Neo4j Connection and Graph RAG ---

def get_neo4j_graph():
    """Initializes and returns the LangChain Neo4jGraph object."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        return None
    try:
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE
        )
        # Verify connection by fetching schema
        graph.get_schema
        return graph
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
        return None

def get_neo4j_rag_context(user_message, persona, problem_type, api_key):
    """
    Uses LangChain's GraphCypherQAChain to generate Cypher and execute the query.
    This provides the "Network-Effect" RAG context.
    """
    graph = get_neo4j_graph()
    if not graph:
        return None, "Neo4j is not configured or connection failed."

    # Use Claude for Cypher generation and QA (consistent with the rest of the app)
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0.0  # Low temperature for deterministic Cypher generation
    )

    # Custom prompt to guide the LLM for Cypher generation
    CYPHER_GENERATION_TEMPLATE = """
    You are an expert Neo4j Cypher query generator. Your task is to translate a user's question into a single, valid, read-only Cypher query.
    The graph schema is:
    {schema}
    
    Focus on retrieving relevant nodes and relationships that could answer the question.
    DO NOT make up properties or labels. The query MUST start with MATCH and end with RETURN.
    DO NOT include any explanation or text outside of the Cypher query itself.
    
    Question: {question}
    """
    
    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=CYPHER_GENERATION_TEMPLATE,
    )

    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=False,
        cypher_prompt=cypher_prompt,
        return_intermediate_steps=True
    )

    try:
        # LangChain's GraphCypherQAChain will generate Cypher, execute it, and then
        # use the LLM to answer the question based on the result.
        # We only want the intermediate steps (Cypher and result) for RAG context.
        result = chain({"query": user_message})
        
        # Extract the generated Cypher and the graph result
        cypher_query = result["intermediate_steps"][0]["query"]
        graph_result = result["intermediate_steps"][1]["context"]
        
        # Format the context for the main RAG prompt
        formatted_context = f"""
        **Generated Cypher Query:**
        ```cypher
        {cypher_query}
        ```
        
        **Graph Database Result:**
        {graph_result}
        """
        
        return formatted_context, None

    except Exception as e:
        return None, f"Error in GraphCypherQAChain: {e}"

# --- Status Check ---
def is_neo4j_configured():
    """Checks if the necessary environment variables are set."""
    return all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD])

# --- FAISS Placeholder (Simulated) ---
# Since FAISS requires embeddings and a corpus, we will simulate its presence for the hybrid RAG logic.
def is_faiss_configured():
    """Simulates FAISS configuration check."""
    # In a real app, this would check for the existence of the FAISS index file.
    return True 

def get_faiss_rag_context(user_message):
    """Simulates FAISS vector search and returns context."""
    # In a real app, this would perform a vector search against the FAISS index.
    return f"Simulated FAISS Vector Search Result for: '{user_message}'. This represents context from the vector store."

if __name__ == '__main__':
    # Example usage (requires environment variables to be set)
    if is_neo4j_configured():
        print("Neo4j is configured. Testing Graph RAG...")
        # Note: This test will fail without a live Neo4j instance and a valid API key
        # test_message = "What are the key relationships between innovation and risk management?"
        # context, error = get_neo4j_rag_context(test_message, "corporate", "ill-defined", "YOUR_GEMINI_API_KEY")
        # if error:
        #     print(f"Test Error: {error}")
        # else:
        #     print("--- Neo4j RAG Context ---")
        #     print(context)
    else:
        print("Neo4j environment variables are not set. Cannot run Graph RAG test.")
    
    if is_faiss_configured():
        print("\nFAISS is configured. Testing Vector RAG simulation...")
        print(get_faiss_rag_context("test query"))
