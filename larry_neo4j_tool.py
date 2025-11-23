"""
Neo4j Query Tool for MCP-style Natural Language to Cypher Conversion
This tool enables the agent to query Neo4j knowledge graphs using natural language.
"""

import os
from typing import Optional
from langchain_core.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from larry_config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE_PRECISE


class Neo4jQueryTool(BaseTool):
    """Tool for querying Neo4j knowledge graph using natural language."""
    
    name: str = "neo4j_knowledge_graph"
    description: str = """Query the user's Neo4j knowledge graph database using natural language.
    
    This tool converts your natural language question into a Cypher query, executes it on the Neo4j database,
    and returns the results. Use this when the user asks about:
    - Information stored in their knowledge graph
    - Relationships between entities
    - Connections, patterns, or insights from their graph data
    - "What do I know about X?"
    - "Show me connections to Y"
    - "What's in my knowledge graph?"
    
    Input should be a natural language question about the knowledge graph.
    The tool will automatically:
    1. Retrieve the database schema
    2. Generate an appropriate Cypher query
    3. Execute the query
    4. Return formatted results
    
    Example inputs:
    - "What entities are in my knowledge graph?"
    - "Show me all relationships for the concept 'AI Safety'"
    - "What do I know about machine learning?"
    - "Find connections between quantum computing and cryptography"
    """
    
    graph: Optional[Neo4jGraph] = None
    llm: Optional[ChatAnthropic] = None
    
    def __init__(self):
        super().__init__()
        self._initialize_neo4j()
    
    def _initialize_neo4j(self):
        """Initialize Neo4j connection and LLM for Cypher generation."""
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        if not all([neo4j_uri, neo4j_user, neo4j_password]):
            print("⚠️ Neo4j credentials not found in environment variables")
            return
        
        try:
            # Initialize Neo4j graph connection
            self.graph = Neo4jGraph(
                url=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password,
                database=neo4j_database
            )
            
            # Verify connection and fetch schema
            self.graph.refresh_schema()
            print(f"✅ Neo4j connected successfully to {neo4j_database}")
            
            # Initialize LLM for Cypher generation
            self.llm = ChatAnthropic(
                model=CLAUDE_MODEL,
                temperature=CLAUDE_TEMPERATURE_PRECISE,
                max_tokens=CLAUDE_MAX_TOKENS
            )
            
        except Exception as e:
            print(f"❌ Neo4j initialization failed: {e}")
            self.graph = None
            self.llm = None
    
    def _run(self, query: str) -> str:
        """Execute the natural language query against Neo4j."""
        if not self.graph or not self.llm:
            return "Neo4j is not configured. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD environment variables."
        
        try:
            # Create custom Cypher generation prompt
            cypher_prompt = PromptTemplate(
                input_variables=["schema", "question"],
                template="""You are a Neo4j Cypher expert. Generate a Cypher query to answer the user's question.
                
Database Schema:
{schema}

Question: {question}

Instructions:
- Generate ONLY the Cypher query, no explanations
- Use the schema to understand available nodes and relationships
- Make the query efficient and specific
- Use LIMIT to prevent returning too many results (default: 25)
- Return relevant properties of nodes and relationships
- AVOID UNION queries - use OR conditions instead
- If you must use UNION, ensure ALL queries return the EXACT SAME column names
- Prefer simple MATCH queries with WHERE clauses over complex UNIONs
- Use labels() and properties() functions to explore unknown schemas

Cypher Query:"""
            )
            
            # Create GraphCypherQAChain for Text2Cypher
            chain = GraphCypherQAChain.from_llm(
                llm=self.llm,
                graph=self.graph,
                verbose=True,
                cypher_prompt=cypher_prompt,
                return_intermediate_steps=True,
                allow_dangerous_requests=True  # Required for write queries if needed
            )
            
            # Execute the query
            result = chain.invoke({"query": query})
            
            # Extract results
            if "intermediate_steps" in result and len(result["intermediate_steps"]) > 0:
                cypher_query = result["intermediate_steps"][0].get("query", "")
                graph_result = result.get("result", "")
                
                # Format response
                response = f"""**Query Results:**

{graph_result}

*Generated Cypher:*
```cypher
{cypher_query}
```
"""
                return response
            else:
                return result.get("result", "No results found in the knowledge graph.")
                
        except Exception as e:
            error_msg = f"Error querying Neo4j: {str(e)}"
            print(f"❌ {error_msg}")
            return f"I encountered an error while querying the knowledge graph: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)


def is_neo4j_configured() -> bool:
    """Check if Neo4j is properly configured."""
    return all([
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
    ])


def get_neo4j_schema() -> Optional[str]:
    """Get the Neo4j database schema for display purposes."""
    if not is_neo4j_configured():
        return None
    
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        graph.refresh_schema()
        return graph.schema
    except Exception as e:
        print(f"Failed to retrieve Neo4j schema: {e}")
        return None
