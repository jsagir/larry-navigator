"""
Definition Classifier Agent - Larry Navigator v2.0
Classifies problem definition state: undefined | ill-defined | well-defined
"""

import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from config.prompts import DEFINITION_CLASSIFIER_PROMPT


class DefinitionClassifierAgent:
    """Agent to classify problem definition state"""

    def __init__(self, api_key: str):
        """Initialize agent with Gemini client

        Args:
            api_key: Google AI API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def classify(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classify the problem definition state

        Args:
            conversation_history: List of {"role": "user/assistant", "content": "..."}

        Returns:
            {
                "classification": "undefined" | "ill-defined" | "well-defined",
                "confidence": 0.0-1.0,
                "reasoning": "...",
                "key_signals": [...]
            }
        """
        # Format conversation for analysis
        conversation_text = self._format_conversation(conversation_history)

        # Create prompt
        prompt = f"""{DEFINITION_CLASSIFIER_PROMPT}

**Conversation to Analyze:**

{conversation_text}

Respond with ONLY a JSON object following the schema above.
"""

        try:
            # Call Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Low temperature for consistency
                    response_mime_type="application/json"
                )
            )

            # Parse JSON response
            result = json.loads(response.text)

            # Validate and return
            return self._validate_output(result)

        except Exception as e:
            print(f"❌ Definition Classifier error: {e}")
            # Return fallback
            return {
                "classification": "undefined",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
                "key_signals": ["error"]
            }

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history as text

        Args:
            history: Conversation messages

        Returns:
            Formatted text
        """
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent output and fill in defaults if needed

        Args:
            result: Raw agent output

        Returns:
            Validated output
        """
        # Ensure required fields
        classification = result.get("classification", "undefined")
        if classification not in ["undefined", "ill-defined", "well-defined"]:
            classification = "undefined"

        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.5

        return {
            "classification": classification,
            "confidence": float(confidence),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "key_signals": result.get("key_signals", [])
        }
