import os
import json
from typing import Type, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field

from langchain_core.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from langchain_community.tools.file_management import FileSearchTool
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from google.generativeai import types
from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate

# Import existing utilities
from larry_web_search import integrate_search_with_response
from larry_neo4j_rag import is_neo4j_configured
from larry_framework_recommender import calculate_uncertainty_risk
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT
from larry_config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE_DEFAULT

# --- 1. Anthropic Claude Initialization ---

def get_claude_llm(session_id: str = None):
    """
    Returns a ChatAnthropic instance.
    In multi-user environments, pass session_id to scope the instance to the user's session.
    
    Args:
        session_id: Optional session identifier for multi-user isolation
        
    Returns:
        ChatAnthropic instance
    """
    # For now, create a new instance each time to ensure session isolation
    # In production, you could cache instances per session_id
    return ChatAnthropic(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        temperature=CLAUDE_TEMPERATURE_DEFAULT
    )

# --- 2. Web Search Tool (Standalone) ---

class WebSearchToolInput(BaseModel):
    """Input for WebSearchTool."""
    query: str = Field(description="The search query to find current information on the web.")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for current, real-time information using Exa.ai neural search. "
        "Use this when the user asks about recent events, current trends, latest research, "
        "or specific companies/products. Returns formatted results with sources and citations."
    )
    args_schema: Type[BaseModel] = WebSearchToolInput
    
    def _run(self, query: str) -> str:
        """Execute web search using Exa.ai"""
        exa_api_key = os.getenv("EXA_API_KEY")
        
        if not exa_api_key:
            return "Web search is not configured. EXA_API_KEY environment variable is missing."
        
        try:
            # Use default persona and problem type for standalone search
            web_result = integrate_search_with_response(
                user_message=query,
                persona="general",
                problem_type="general",
                exa_api_key=exa_api_key
            )
            
            if web_result:
                return web_result
            else:
                return "No relevant web results found for this query."
                
        except Exception as e:
            return f"Web search error: {str(e)}"

# --- 3. Uncertainty Navigator Tool (The Killer Feature) ---

class UncertaintyNavigatorToolInput(BaseModel):
    """Input for UncertaintyNavigatorTool."""
    query: str = Field(description="The user's full message or question that requires a multi-source RAG and diagnostic analysis.")
    persona: str = Field(description="The current user persona (e.g., 'entrepreneur', 'corporate').")
    problem_type: str = Field(description="The current problem type (e.g., 'ill-defined', 'undefined').")

class UncertaintyNavigatorTool(BaseTool):
    name: str = "uncertainty_navigator_tool"
    description: str = (
        "This is the primary tool for answering complex, multi-source questions. "
        "It orchestrates the full RAG pipeline (Neo4j, Web Search, File Search), "
        "uses Anthropic Claude for sequential reasoning, generates a provocative question, "
        "and returns a structured, final answer."
    )
    args_schema: Type[BaseModel] = UncertaintyNavigatorToolInput
    
    def _run(self, query: str, persona: str, problem_type: str) -> str:
        # --- A. Parallel RAG Orchestration ---
        
        # Define RAG source functions for parallel execution
        def fetch_neo4j_context():
            """Query Neo4j graph database."""
            if not is_neo4j_configured():
                return None
            
            try:
                graph = Neo4jGraph()
                claude_llm = get_claude_llm()
                chain = GraphCypherQAChain.from_llm(
                    llm=claude_llm,
                    graph=graph,
                    verbose=False,
                    return_intermediate_steps=False
                )
                result = chain.invoke({"query": query})
                return f"NETWORK-EFFECT GRAPH CONTEXT: {result.get('result', 'No relevant graph data found.')}"
            except Exception as e:
                return f"NETWORK-EFFECT GRAPH ERROR: {str(e)}"
        
        def fetch_web_context():
            """Query Exa.ai web search."""
            exa_api_key = os.getenv("EXA_API_KEY")
            if not exa_api_key:
                return None
            
            try:
                web_result = integrate_search_with_response(
                    user_message=query,
                    persona=persona,
                    problem_type=problem_type,
                    exa_api_key=exa_api_key
                )
                return f"WEB SEARCH CONTEXT: {web_result}" if web_result else None
            except Exception as e:
                return f"WEB SEARCH ERROR: {str(e)}"
        
        def fetch_file_context():
            """Query Gemini file search."""
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key or not os.path.exists("larry_store_info.json"):
                return None
            
            try:
                with open("larry_store_info.json", "r") as f:
                    store_info = json.load(f)
                store_name = store_info.get("store_name")
                
                if not store_name:
                    return "PWS DOCUMENT INFO: Store name not found in configuration."
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Based on the PWS documents, answer the following question: {query}",
                    config=types.GenerateContentConfig(
                        tools=[
                            types.Tool(
                                file_search=types.FileSearch(
                                    file_search_store_names=[store_name]
                                )
                            )
                        ]
                    )
                )
                return f"PWS DOCUMENT CONTEXT: {response.text}"
            except Exception as e:
                return f"PWS DOCUMENT ERROR: {str(e)}"
        
        # Execute all sources in parallel
        rag_context = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            futures = {
                executor.submit(fetch_neo4j_context): 'neo4j',
                executor.submit(fetch_web_context): 'web',
                executor.submit(fetch_file_context): 'files'
            }
            
            # Collect results as they complete (with 10 second timeout)
            for future in as_completed(futures, timeout=10):
                try:
                    result = future.result()
                    if result:  # Only add non-None results
                        rag_context.append(result)
                except Exception as e:
                    source_name = futures[future]
                    rag_context.append(f"{source_name.upper()} ERROR: {str(e)}")
        
        full_context = "\n\n---\n\n".join(rag_context)
        
        # --- B. Combined Claude API Call (Cost Optimization) ---
        
        claude_llm = get_claude_llm()
        
        # Combined prompt that generates both provocative question AND final answer
        combined_prompt = PromptTemplate.from_template(
            """
            You are Larry, the Uncertainty Navigator. Provide a response in TWO parts:
            
            1. First, generate a PROVOCATIVE QUESTION that challenges the user's assumptions.
            2. Then, provide your COMPREHENSIVE ANSWER using the De Stijl style.
            
            User Query: {query}
            Context: {context}
            Persona: {persona}
            Problem Type: {problem_type}
            
            {system_prompt}
            
            Format your response EXACTLY as follows:
            
            PROVOCATIVE QUESTION:
            [Your single, high-impact provocative question]
            
            ANSWER:
            [Your detailed answer incorporating the provocative question's spirit]
            """
        )
        
        # Single Claude API call
        combined_chain = combined_prompt | claude_llm
        combined_response = combined_chain.invoke({
            "query": query,
            "context": full_context,
            "persona": persona,
            "problem_type": problem_type,
            "system_prompt": LARRY_SYSTEM_PROMPT
        })
        
        # Parse the combined response
        response_text = combined_response.content
        
        # Extract answer (provocative question already incorporated)
        if "ANSWER:" in response_text:
            parts = response_text.split("ANSWER:", 1)
            final_answer = parts[1].strip()
        else:
            # Fallback if format not followed
            final_answer = response_text
        
        # --- C. Return Clean Text Output ---
        
        # Return only the final answer text for clean display
        # The provocative question is already incorporated in the answer
        return final_answer

# --- 3. Context Update Tool (Internal State) ---

class ContextUpdateToolInput(BaseModel):
    """Input for ContextUpdateTool."""
    user_message: str = Field(description="The user's latest message to be analyzed for context update.")

class ContextUpdateTool(BaseTool):
    name: str = "context_update_tool"
    description: str = (
        "Use this tool to analyze the user's message and update the internal state "
        "such as the user's persona, problem type, and calculate uncertainty/risk scores. "
        "This tool does not return an answer to the user, only updates the internal state."
    )
    args_schema: Type[BaseModel] = ContextUpdateToolInput
    
    def _run(self, user_message: str) -> str:
        # 1. Simple Heuristic for Persona/Problem Type (from larry_state_engine.py)
        def _detect_persona(message: str) -> str:
            message_lower = message.lower()
            if any(word in message_lower for word in ["startup", "founder", "venture", "market fit"]):
                return "entrepreneur"
            elif any(word in message_lower for word in ["corporate", "company", "stakeholder", "portfolio"]):
                return "corporate"
            elif any(word in message_lower for word in ["research", "theory", "hypothesis", "literature"]):
                return "researcher"
            elif any(word in message_lower for word in ["client", "workshop", "facilitate", "consult"]):
                return "consultant"
            elif any(word in message_lower for word in ["exam", "study", "assignment"]):
                return "student"
            return "general"

        def _classify_problem_type(message: str) -> str:
            message_lower = message.lower()
            if any(word in message_lower for word in ["future", "trend", "macro", "scenario", "long-term", "disrupt"]):
                return "undefined"
            elif any(word in message_lower for word in ["opportunity", "near-term", "expansion", "growth", "next step"]):
                return "ill-defined"
            elif any(word in message_lower for word in ["implement", "build", "execute", "prototype", "solution", "finalize"]):
                return "well-defined"
            return "general"

        persona = _detect_persona(user_message)
        problem_type = _classify_problem_type(user_message)
        
        # 2. Calculate Uncertainty/Risk
        uncertainty_level, risk_level, uncertainty_score, risk_score = calculate_uncertainty_risk(
            problem_type, user_message
        )
        
        # Return a JSON string with the updated state
        return json.dumps({
            "persona": persona,
            "problem_type": problem_type,
            "uncertainty_score": uncertainty_score,
            "risk_score": risk_score,
            "message": "Internal state updated successfully."
        })


