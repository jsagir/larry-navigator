"""
Research Agent - Larry Navigator v2.0
Decides when to trigger web research and generates Tavily queries
"""

import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from config.prompts import RESEARCH_AGENT_PROMPT


class ResearchAgent:
    """Agent to identify research needs and generate queries"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def analyze_research_need(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Analyze if web research is needed and generate queries

        Args:
            user_message: Latest user message
            conversation_history: Previous messages for context

        Returns:
            {
                "should_research": true/false,
                "reasoning": "...",
                "queries": ["query1", "query2"],
                "research_focus": "..."
            }
        """

        # Format recent conversation context (last 3 messages)
        recent_context = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        context_text = self._format_conversation(recent_context)

        prompt = f"""{RESEARCH_AGENT_PROMPT}

**Recent Conversation Context:**

{context_text}

**Latest User Message:**

{user_message}

Respond with ONLY a JSON object following the schema above.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return self._validate_output(result)

        except Exception as e:
            print(f"❌ Research Agent error: {e}")
            return {
                "should_research": False,
                "reasoning": f"Analysis failed: {str(e)}",
                "queries": [],
                "research_focus": ""
            }

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n\n".join(formatted)

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        should_research = result.get("should_research", False)
        if not isinstance(should_research, bool):
            should_research = False

        queries = result.get("queries", [])
        if not isinstance(queries, list):
            queries = []

        # Limit to max 3 queries
        if len(queries) > 3:
            queries = queries[:3]

        return {
            "should_research": should_research,
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "queries": queries,
            "research_focus": result.get("research_focus", "")
        }
