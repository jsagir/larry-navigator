import requests
import json
import uuid
from typing import List, Dict, Any

# Configuration
RASA_API_URL = os.getenv("RASA_API_URL", "http://localhost:5005/webhooks/rest/webhook")

def map_streamlit_session_to_rasa(st_session_state: Dict[str, Any]) -> str:
    """
    Maps the Streamlit session state to a unique Rasa conversation ID (sender_id).
    This ensures conversation continuity.
    """
    if "rasa_sender_id" not in st_session_state:
        st_session_state["rasa_sender_id"] = str(uuid.uuid4())
    return st_session_state["rasa_sender_id"]

def update_streamlit_from_rasa(rasa_slots: Dict[str, Any], st_session_state: Dict[str, Any]):
    """
    Updates Streamlit session state with key slots from Rasa to keep the UI synchronized.
    """
    # Update core indicators in the sidebar
    if "persona" in rasa_slots:
        st_session_state["persona"] = rasa_slots["persona"]
    if "problem_type" in rasa_slots:
        st_session_state["problem_type"] = rasa_slots["problem_type"]
    
    # Update portfolio slots
    if "opportunities_now" in rasa_slots:
        st_session_state["opportunities_now"] = rasa_slots["opportunities_now"]
    if "opportunities_new" in rasa_slots:
        st_session_state["opportunities_new"] = rasa_slots["opportunities_new"]
    if "opportunities_next" in rasa_slots:
        st_session_state["opportunities_next"] = rasa_slots["opportunities_next"]

def parse_rasa_response(rasa_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses the Rasa response into a format usable by the Streamlit UI.
    It handles standard text messages and custom JSON messages.
    """
    parsed_messages = []
    for message in rasa_response:
        if "text" in message:
            # Standard text response from Rasa
            parsed_messages.append({
                "role": "assistant",
                "type": "regular",
                "content": message["text"]
            })
        elif "custom" in message:
            # Custom JSON message from custom actions (e.g., provocative, framework)
            custom_data = message["custom"]
            parsed_messages.append({
                "role": "assistant",
                "type": custom_data.get("type", "accent"), # Default to accent if type is missing
                "content": custom_data.get("text", "Custom message received.")
            })
    return parsed_messages

def send_to_rasa(message: str, sender_id: str) -> List[Dict[str, Any]]:
    """
    Sends a user message to the Rasa REST API and returns the response.
    """
    payload = {
        "sender": sender_id,
        "message": message
    }
    
    try:
        response = requests.post(RASA_API_URL, json=payload, timeout=30)
        response.raise_for_status() # Raise an exception for bad status codes
        
        rasa_response = response.json()
        
        # The Rasa response is a list of messages
        return rasa_response
        
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Rasa API: {e}")
        # Fallback response if Rasa is down or errors out
        return [{
            "text": "I'm sorry, my conversational engine is currently offline. Please try again later.",
            "custom": {"type": "diagnostic"}
        }]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [{
            "text": "An unexpected error occurred while processing your request.",
            "custom": {"type": "diagnostic"}
        }]

# Note: The original plan requested async functions, but Streamlit's main loop is synchronous.
# We use the synchronous requests library here for simplicity in the Streamlit context.
# For a true async Streamlit app, we would use a library like aiohttp and run the calls in an executor.
# Given the constraints, the synchronous call is the most reliable integration method.
