import os
import json
from typing import Type, Optional, List
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

# --- 1. Anthropic Claude Initialization ---
# We will use Claude for the core reasoning and final answer generation
def get_claude_llm():
    # Uses ANTHROPIC_API_KEY environment variable
    return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.2)

# --- 2. Uncertainty Navigator Tool (The Killer Feature) ---

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
        # --- A. RAG Orchestration ---
        
        rag_context = []
        
        # 1. Neo4j Graph RAG (Claude-powered sequential reasoning)
        if is_neo4j_configured():
            try:
                graph = Neo4jGraph()
                claude_llm = get_claude_llm()
                
                # Use Claude for the Cypher QA Chain
                chain = GraphCypherQAChain.from_llm(
                    llm=claude_llm,
                    graph=graph,
                    verbose=False,
                    return_intermediate_steps=False
                )
                
                graph_result = chain.invoke({"query": query})
                rag_context.append(f"NETWORK-EFFECT GRAPH CONTEXT: {graph_result.get('result', 'No relevant graph data found.')}")
                
            except Exception as e:
                rag_context.append(f"NETWORK-EFFECT GRAPH ERROR: Could not connect or query Neo4j. {str(e)}")

        # 2. Exa.ai Web Search (Latest Trends)
        exa_api_key = os.getenv("EXA_API_KEY")
        if exa_api_key:
            try:
                web_result = integrate_search_with_response(
                    user_message=query,
                    persona=persona,
                    problem_type=problem_type,
                    exa_api_key=exa_api_key
                )
                rag_context.append(f"WEB SEARCH CONTEXT: {web_result}")
            except Exception as e:
                rag_context.append(f"WEB SEARCH ERROR: Could not perform Exa.ai search. {str(e)}")

        # 3. PWS File Search (Core Documents)
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if api_key:
            try:
                # Load store info (assuming larry_store_info.json is available)
                with open("larry_store_info.json", "r") as f:
                    store_info = json.load(f)
                store_name = store_info.get("store_name")
                
                client = genai.Client(api_key=api_key)
                
                # Use the Gemini API for the File Search tool (since the store is Gemini-based)
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
                rag_context.append(f"PWS DOCUMENT CONTEXT: {response.text}")
                
            except Exception as e:
                rag_context.append(f"PWS DOCUMENT ERROR: Could not perform File Search. {str(e)}")

        full_context = "\n\n---\n\n".join(rag_context)
        
        # --- B. Claude-Powered Diagnostic and Generation ---
        
        claude_llm = get_claude_llm()
        
        # 1. Provocative Question Generation Prompt
        provocative_prompt = PromptTemplate.from_template(
            """
            Based on the following user query and the retrieved RAG context, generate a single, high-impact, provocative question that challenges the user's assumptions or forces them to consider a critical blind spot.
            
            User Query: {query}
            
            Context: {context}
            
            Persona: {persona}
            Problem Type: {problem_type}
            
            Your output MUST be ONLY the question itself, starting with "Provocative Question:".
            """
        )
        
        # 2. Final Answer Generation Prompt
        final_answer_prompt = PromptTemplate.from_template(
            """
            You are Larry, the Uncertainty Navigator. Your goal is to provide a structured, insightful answer in the hyper-minimalist De Stijl mentor style.
            
            User Query: {query}
            
            Context: {context}
            
            Persona: {persona}
            Problem Type: {problem_type}
            
            Provocative Question: {provocative_question}
            
            {system_prompt}
            
            Your final output MUST be a single, cohesive response that:
            1. Directly answers the user's query using the provided context.
            2. Incorporates the spirit of the Provocative Question into your guidance.
            3. Uses the De Stijl style (minimal, direct, structured).
            4. Does NOT include the "Provocative Question:" prefix in the final output.
            """
        )
        
        # --- C. Sequential Execution (Claude's Strength) ---
        
        # Step 1: Generate Provocative Question
        provocative_chain = provocative_prompt | claude_llm
        provocative_response = provocative_chain.invoke({
            "query": query,
            "context": full_context,
            "persona": persona,
            "problem_type": problem_type
        })
        
        # Clean the provocative question
        provocative_question = provocative_response.content.replace("Provocative Question:", "").strip()
        
        # Step 2: Generate Final Answer
        final_chain = final_answer_prompt | claude_llm
        final_response = final_chain.invoke({
            "query": query,
            "context": full_context,
            "persona": persona,
            "problem_type": problem_type,
            "provocative_question": provocative_question,
            "system_prompt": LARRY_SYSTEM_PROMPT
        })
        
        # --- D. Structured Output ---
        
        # Return a structured JSON string that the Agent can pass back to the Streamlit app
        return json.dumps({
            "final_answer": final_response.content,
            "provocative_question": provocative_question,
            "context_used": full_context[:500] + "..." # Truncate context for clean output
        })

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

# --- 4. List of all tools for the Agent ---

def get_larry_tools(persona: str, problem_type: str):
    """
    Returns the list of tools. The UncertaintyNavigatorTool is the main tool.
    """
    return [
        UncertaintyNavigatorTool(),
        ContextUpdateTool()
    ]
