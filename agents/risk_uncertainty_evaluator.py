"""
Risk-Uncertainty Evaluator Agent - Larry Navigator v2.0
Positions problem on risk-uncertainty spectrum: 0.0 (risk) to 1.0 (uncertainty)
"""

import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from config.prompts import RISK_UNCERTAINTY_EVALUATOR_PROMPT


class RiskUncertaintyEvaluatorAgent:
    """Agent to evaluate risk vs uncertainty position"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def evaluate(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Evaluate risk-uncertainty position

        Args:
            conversation_history: List of messages

        Returns:
            {
                "position": 0.0-1.0,
                "reasoning": "...",
                "known_unknowns": [...],
                "unknown_unknowns": [...]
            }
        """
        conversation_text = self._format_conversation(conversation_history)

        prompt = f"""{RISK_UNCERTAINTY_EVALUATOR_PROMPT}

**Conversation to Analyze:**

{conversation_text}

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
            print(f"❌ Risk-Uncertainty Evaluator error: {e}")
            return {
                "position": 0.5,
                "reasoning": f"Evaluation failed: {str(e)}",
                "known_unknowns": [],
                "unknown_unknowns": []
            }

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n\n".join(formatted)

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        position = result.get("position", 0.5)
        if not isinstance(position, (int, float)) or position < 0 or position > 1:
            position = 0.5

        return {
            "position": float(position),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "known_unknowns": result.get("known_unknowns", []),
            "unknown_unknowns": result.get("unknown_unknowns", [])
        }
