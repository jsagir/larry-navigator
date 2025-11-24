"""
Diagnosis Consolidator Agent - Larry Navigator v2.0
Synthesizes all diagnostic agent outputs into coherent assessment
"""

import json
from typing import Dict, Any
from google import genai
from google.genai import types
from config.prompts import DIAGNOSIS_CONSOLIDATOR_PROMPT


class DiagnosisConsolidatorAgent:
    """Agent to consolidate all diagnostic outputs"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"

    def consolidate(
        self,
        definition_output: Dict[str, Any],
        complexity_output: Dict[str, Any],
        risk_uncertainty_output: Dict[str, Any],
        wickedness_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolidate all diagnostic outputs

        Args:
            definition_output: From definition classifier
            complexity_output: From complexity assessor
            risk_uncertainty_output: From risk-uncertainty evaluator
            wickedness_output: From wickedness classifier

        Returns:
            {
                "summary": "...",
                "consistency_check": {...},
                "dominant_characteristic": "...",
                "recommended_approach": "...",
                "confidence": 0.0-1.0
            }
        """

        # Format diagnostic data
        diagnostic_data = f"""
**Definition Classification:**
- Classification: {definition_output.get('classification')}
- Confidence: {definition_output.get('confidence')}
- Reasoning: {definition_output.get('reasoning')}
- Signals: {', '.join(definition_output.get('key_signals', []))}

**Complexity Assessment (Cynefin):**
- Complexity: {complexity_output.get('complexity')}
- Confidence: {complexity_output.get('confidence')}
- Reasoning: {complexity_output.get('reasoning')}
- Characteristics: {', '.join(complexity_output.get('characteristics', []))}

**Risk-Uncertainty Position:**
- Position: {risk_uncertainty_output.get('position')}
- Reasoning: {risk_uncertainty_output.get('reasoning')}
- Known Unknowns: {', '.join(risk_uncertainty_output.get('known_unknowns', []))}
- Unknown Unknowns: {', '.join(risk_uncertainty_output.get('unknown_unknowns', []))}

**Wickedness Classification:**
- Wickedness: {wickedness_output.get('wickedness')}
- Score: {wickedness_output.get('score')}
- Reasoning: {wickedness_output.get('reasoning')}
- Characteristics: {', '.join(wickedness_output.get('characteristics_present', []))}
- Stakeholders: {wickedness_output.get('stakeholder_count')}
"""

        prompt = f"""{DIAGNOSIS_CONSOLIDATOR_PROMPT}

**Diagnostic Data to Synthesize:**

{diagnostic_data}

Respond with ONLY a JSON object following the schema above.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,  # Slightly higher for synthesis
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            return self._validate_output(result)

        except Exception as e:
            print(f"❌ Diagnosis Consolidator error: {e}")
            return {
                "summary": f"Unable to consolidate diagnosis: {str(e)}",
                "consistency_check": {
                    "is_consistent": False,
                    "tensions": ["consolidation error"]
                },
                "dominant_characteristic": "Unknown",
                "recommended_approach": "Manual review needed",
                "confidence": 0.0
            }

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # Validate consistency_check structure
        consistency_check = result.get("consistency_check", {})
        if not isinstance(consistency_check, dict):
            consistency_check = {"is_consistent": True, "tensions": []}

        if "is_consistent" not in consistency_check:
            consistency_check["is_consistent"] = True
        if "tensions" not in consistency_check:
            consistency_check["tensions"] = []

        # Validate confidence
        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.5

        return {
            "summary": result.get("summary", "No summary available"),
            "consistency_check": consistency_check,
            "dominant_characteristic": result.get("dominant_characteristic", "Unknown"),
            "recommended_approach": result.get("recommended_approach", "Continue exploration"),
            "confidence": float(confidence)
        }
