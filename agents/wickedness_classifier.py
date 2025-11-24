"""
Wickedness Classifier Agent - Larry Navigator v2.0
Classifies problem wickedness: tame | messy | complex | wicked
"""

import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from config.prompts import WICKEDNESS_CLASSIFIER_PROMPT


class WickednessClassifierAgent:
    """Agent to classify problem wickedness"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def classify(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classify wickedness level

        Args:
            conversation_history: List of messages

        Returns:
            {
                "wickedness": "tame" | "messy" | "complex" | "wicked",
                "score": 0.0-1.0,
                "reasoning": "...",
                "characteristics_present": [...],
                "stakeholder_count": "few" | "several" | "many"
            }
        """
        conversation_text = self._format_conversation(conversation_history)

        prompt = f"""{WICKEDNESS_CLASSIFIER_PROMPT}

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
            print(f"❌ Wickedness Classifier error: {e}")
            return {
                "wickedness": "messy",
                "score": 0.5,
                "reasoning": f"Classification failed: {str(e)}",
                "characteristics_present": ["error"],
                "stakeholder_count": "several"
            }

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n\n".join(formatted)

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        wickedness = result.get("wickedness", "messy")
        if wickedness not in ["tame", "messy", "complex", "wicked"]:
            wickedness = "messy"

        score = result.get("score", 0.5)
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            score = 0.5

        stakeholder_count = result.get("stakeholder_count", "several")
        if stakeholder_count not in ["few", "several", "many"]:
            stakeholder_count = "several"

        return {
            "wickedness": wickedness,
            "score": float(score),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "characteristics_present": result.get("characteristics_present", []),
            "stakeholder_count": stakeholder_count
        }
