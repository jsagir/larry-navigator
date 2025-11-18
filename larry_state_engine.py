import os
import re
import json
from google import genai
from google.genai import types
from typing import Dict, Any, Tuple, List

# Import existing RAG utilities
from larry_web_search import integrate_search_with_response
from larry_neo4j_rag import get_neo4j_rag_context, is_neo4j_configured, is_faiss_configured, get_faiss_rag_context
from larry_framework_recommender import (
    recommend_frameworks,
    calculate_uncertainty_risk,
    get_framework_notification,
    get_all_frameworks_sorted
)

# Load the system prompt (assuming it's available in the same directory)
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3
LARRY_SYSTEM_PROMPT = LARRY_SYSTEM_PROMPT_V3

class LarryStateEngine:
    """
    A simple, stateful engine to manage the conversation flow, persona,
    problem classification, and RAG orchestration, replacing the Rasa middleware.
    """
    
    def __init__(self, api_key: str, exa_api_key: str, store_info: Dict[str, Any]):
        self.api_key = api_key
        self.exa_api_key = exa_api_key
        self.store_info = store_info
        self.client = genai.Client(api_key=api_key)
        
        # Initialize state variables
        self.persona = "general"
        self.problem_type = "general"
        self.uncertainty_score = 50
        self.risk_score = 50
        self.recommended_frameworks = []
        
    def _detect_persona(self, message: str) -> str:
        """Simple heuristic for persona detection."""
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

    def _classify_problem_type(self, message: str) -> Tuple[str, int]:
        """Classify problem type and return type and initial uncertainty score."""
        message_lower = message.lower()
        if any(word in message_lower for word in ["future", "trend", "macro", "scenario", "long-term", "disrupt"]):
            return "undefined", 0
        elif any(word in message_lower for word in ["opportunity", "near-term", "expansion", "growth", "next step"]):
            return "ill-defined", 50
        elif any(word in message_lower for word in ["implement", "build", "execute", "prototype", "solution", "finalize"]):
            return "well-defined", 85
        return "general", 50

    def _update_state(self, user_message: str):
        """Updates persona, problem type, and calculates risk/uncertainty."""
        
        # 1. Update Persona (if a stronger signal is found)
        new_persona = self._detect_persona(user_message)
        if new_persona != "general":
            self.persona = new_persona
            
        # 2. Update Problem Type
        new_problem_type, initial_score = self._classify_problem_type(user_message)
        self.problem_type = new_problem_type
        
        # 3. Calculate Uncertainty/Risk
        uncertainty_level, risk_level, uncertainty_score, risk_score = calculate_uncertainty_risk(
            self.problem_type, user_message
        )
        self.uncertainty_score = uncertainty_score
        self.risk_score = risk_score
        
        # 4. Recommend Frameworks
        self.recommended_frameworks = recommend_frameworks(
            self.problem_type,
            self.persona,
            user_message,
            max_recommendations=3
        )

    def _orchestrate_rag(self, user_message: str) -> Tuple[str, str, str]:
        """Orchestrates the three RAG sources (Web, Neo4j, FAISS)."""
        
        search_results = ""
        neo4j_context = ""
        faiss_context = ""
        
        # 1. Web Search (Exa.ai)
        if self.exa_api_key:
            # Simulate Streamlit spinner for the UI
            # with st.spinner("🔍 Searching latest research..."):
            search_results = integrate_search_with_response(
                user_message=user_message,
                persona=self.persona,
                problem_type=self.problem_type,
                exa_api_key=self.exa_api_key
            )
            
        # 2. Neo4j Graph RAG (Network-Effect)
        if is_neo4j_configured():
            # with st.spinner("🌐 Querying Network-Effect Graph..."):
            neo4j_context, neo4j_error = get_neo4j_rag_context(
                user_message, self.persona, self.problem_type, self.api_key
            )
            if neo4j_error:
                print(f"Neo4j RAG Error: {neo4j_error}")
                neo4j_context = ""
                
        # 3. FAISS Vector RAG (Simulated)
        if is_faiss_configured():
            # with st.spinner("🧠 Searching Vector Store (FAISS)..."):
            faiss_context = get_faiss_rag_context(user_message)
            
        return search_results, neo4j_context, faiss_context

    def chat(self, user_message: str) -> List[Dict[str, str]]:
        """
        Main chat function. Updates state, orchestrates RAG, and generates response.
        Returns a list of structured messages for the Streamlit UI.
        """
        
        # 1. Update State
        self._update_state(user_message)
        
        # 2. Orchestrate RAG
        search_results, neo4j_context, faiss_context = self._orchestrate_rag(user_message)
        
        # 3. Build Enhanced Prompt
        enhanced_prompt = f"""{LARRY_SYSTEM_PROMPT}

**DETECTED CONTEXT:**
- User Persona: {self.persona}
- Problem Type: {self.problem_type}

Adapt your response accordingly! Use appropriate frameworks and language for this persona and problem type.
"""
        if search_results:
            enhanced_prompt += f"\n\n**CURRENT WEB RESEARCH:**\n{search_results}\n\nIntegrate these cutting-edge findings into your response with proper citations."
        if neo4j_context:
            enhanced_prompt += f"\n\n**NETWORK-EFFECT GRAPH CONTEXT:**\n{neo4j_context}\n\nUse this structured knowledge to provide a more insightful, relationship-aware answer."
        if faiss_context:
            enhanced_prompt += f"\n\n**FAISS VECTOR CONTEXT:**\n{faiss_context}\n\nIntegrate this vector-based context into your response."

        # 4. Generate Content
        tools_config = []
        if self.store_info:
            tools_config.append(
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[self.store_info["store_name"]]
                    )
                )
            )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    tools=tools_config,
                    temperature=0.7,
                    top_p=0.95,
                )
            )
            
            full_response_text = response.text if response and response.text else "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            full_response_text = f"Error during content generation: {str(e)}"
            
        # 5. Parse and Structure Response (Simplified to the original Streamlit logic)
        messages = []
        sections = full_response_text.split("\n\n")
        
        for section in sections:
            if not section.strip():
                continue
            # Simple heuristic for accent messages (can be improved later)
            if any(phrase in section for phrase in ["?", "Suppose", "What if", "Think about", "Action:", "Next step:", "Framework", "Tool", "Model", "Method"]):
                messages.append({"type": "accent", "content": section})
            else:
                messages.append({"type": "regular", "content": section})
                
        return messages

# Helper function to load store info (copied from larry_app.py)
def load_store_info():
    """Load File Search store information"""
    from pathlib import Path
    store_file = Path(__file__).parent / "larry_store_info.json"
    if store_file.exists():
        with open(store_file, "r") as f:
            return json.load(f)
    return None
