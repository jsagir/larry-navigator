"""
Complexity Assessor Agent - Larry Navigator v2.0
Classifies complexity using Cynefin framework: simple | complicated | complex | chaotic
"""

import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from config.prompts import COMPLEXITY_ASSESSOR_PROMPT


class ComplexityAssessorAgent:
    """Agent to assess problem complexity using Cynefin"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def assess(self, conversation_history: List[Dict[str, str]], problem_definition: str = "") -> Dict[str, Any]:
        """Assess complexity using Cynefin framework

        Args:
            conversation_history: List of messages
            problem_definition: Current problem definition if available

        Returns:
            {
                "complexity": "simple" | "complicated" | "complex" | "chaotic",
                "confidence": 0.0-1.0,
                "reasoning": "...",
                "characteristics": [...]
            }
        """
        conversation_text = self._format_conversation(conversation_history)

        prompt = f"""{COMPLEXITY_ASSESSOR_PROMPT}

**Conversation to Analyze:**

{conversation_text}

**Current Problem Definition:** {problem_definition if problem_definition else "Not yet defined"}

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
            print(f"❌ Complexity Assessor error: {e}")
            return {
                "complexity": "complex",
                "confidence": 0.0,
                "reasoning": f"Assessment failed: {str(e)}",
                "characteristics": ["error"]
            }

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n\n".join(formatted)

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        complexity = result.get("complexity", "complex")
        if complexity not in ["simple", "complicated", "complex", "chaotic"]:
            complexity = "complex"

        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.5

        return {
            "complexity": complexity,
            "confidence": float(confidence),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "characteristics": result.get("characteristics", [])
        }
