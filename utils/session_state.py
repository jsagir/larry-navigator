"""
Session State Management for Larry Navigator v2.0
Tracks 4-dimensional problem diagnosis
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime


class ProblemDiagnosis:
    """Structured data for problem diagnosis"""

    def __init__(self):
        # Dimension 1: Definition Track
        self.definition: str = "undefined"  # undefined | ill-defined | well-defined
        self.definition_confidence: float = 0.0  # 0.0 to 1.0

        # Dimension 2: Complexity (Cynefin)
        self.complexity: str = "complex"  # simple | complicated | complex | chaotic
        self.complexity_confidence: float = 0.0

        # Dimension 3: Risk-Uncertainty Position
        self.risk_uncertainty: float = 0.5  # 0.0 (risk/known unknowns) to 1.0 (uncertainty/unknown unknowns)

        # Dimension 4: Wickedness
        self.wickedness: str = "messy"  # tame | messy | complex | wicked
        self.wickedness_score: float = 0.0  # 0.0 to 1.0

        # Metadata
        self.last_updated: str = datetime.now().isoformat()
        self.update_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "definition": self.definition,
            "definition_confidence": self.definition_confidence,
            "complexity": self.complexity,
            "complexity_confidence": self.complexity_confidence,
            "risk_uncertainty": self.risk_uncertainty,
            "wickedness": self.wickedness,
            "wickedness_score": self.wickedness_score,
            "last_updated": self.last_updated,
            "update_count": self.update_count
        }

    def update_from_dict(self, data: Dict[str, Any]):
        """Update from agent output"""
        if "definition" in data:
            self.definition = data["definition"]
        if "definition_confidence" in data:
            self.definition_confidence = data["definition_confidence"]
        if "complexity" in data:
            self.complexity = data["complexity"]
        if "complexity_confidence" in data:
            self.complexity_confidence = data["complexity_confidence"]
        if "risk_uncertainty" in data:
            self.risk_uncertainty = data["risk_uncertainty"]
        if "wickedness" in data:
            self.wickedness = data["wickedness"]
        if "wickedness_score" in data:
            self.wickedness_score = data["wickedness_score"]

        self.last_updated = datetime.now().isoformat()
        self.update_count += 1


def initialize_session_state():
    """Initialize all session state variables"""

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Problem diagnosis (4 dimensions)
    if "diagnosis" not in st.session_state:
        st.session_state.diagnosis = ProblemDiagnosis()

    # Research tracking
    if "research_history" not in st.session_state:
        st.session_state.research_history = []

    if "active_research" not in st.session_state:
        st.session_state.active_research = None

    # Agent status
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = {
            "definition_classifier": "idle",      # idle | running | complete
            "complexity_assessor": "idle",
            "risk_uncertainty_evaluator": "idle",
            "wickedness_classifier": "idle",
            "diagnosis_consolidator": "idle",
            "research_agent": "idle"
        }

    # Stats
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now().isoformat()

    if "total_turns" not in st.session_state:
        st.session_state.total_turns = 0

    if "total_research_queries" not in st.session_state:
        st.session_state.total_research_queries = 0

    # UI state
    if "show_research_panel" not in st.session_state:
        st.session_state.show_research_panel = False

    if "show_diagnostic_details" not in st.session_state:
        st.session_state.show_diagnostic_details = True


def get_diagnosis() -> ProblemDiagnosis:
    """Get current problem diagnosis"""
    return st.session_state.diagnosis


def update_diagnosis(dimension: str, value: Any, confidence: Optional[float] = None):
    """Update a specific dimension of the diagnosis

    Args:
        dimension: "definition" | "complexity" | "risk_uncertainty" | "wickedness"
        value: New value for that dimension
        confidence: Optional confidence score (0.0 to 1.0)
    """
    diagnosis = st.session_state.diagnosis

    if dimension == "definition":
        diagnosis.definition = value
        if confidence is not None:
            diagnosis.definition_confidence = confidence

    elif dimension == "complexity":
        diagnosis.complexity = value
        if confidence is not None:
            diagnosis.complexity_confidence = confidence

    elif dimension == "risk_uncertainty":
        diagnosis.risk_uncertainty = value

    elif dimension == "wickedness":
        diagnosis.wickedness = value
        if confidence is not None:
            diagnosis.wickedness_score = confidence

    diagnosis.last_updated = datetime.now().isoformat()
    diagnosis.update_count += 1


def add_message(role: str, content: str):
    """Add a message to chat history"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    st.session_state.total_turns += 1


def add_research_result(query: str, results: list, synthesis: str):
    """Add research results to history"""
    st.session_state.research_history.append({
        "query": query,
        "results": results,
        "synthesis": synthesis,
        "timestamp": datetime.now().isoformat()
    })
    st.session_state.total_research_queries += 1


def set_agent_status(agent_name: str, status: str):
    """Update agent status

    Args:
        agent_name: Name of the agent
        status: "idle" | "running" | "complete"
    """
    if agent_name in st.session_state.agent_status:
        st.session_state.agent_status[agent_name] = status


def get_session_stats() -> Dict[str, Any]:
    """Get session statistics"""
    start_time = datetime.fromisoformat(st.session_state.session_start_time)
    duration = datetime.now() - start_time

    return {
        "total_turns": st.session_state.total_turns,
        "total_research_queries": st.session_state.total_research_queries,
        "session_duration_minutes": int(duration.total_seconds() / 60),
        "diagnosis_updates": st.session_state.diagnosis.update_count
    }


def reset_session():
    """Reset the entire session (for new problem)"""
    st.session_state.messages = []
    st.session_state.diagnosis = ProblemDiagnosis()
    st.session_state.research_history = []
    st.session_state.active_research = None
    st.session_state.session_start_time = datetime.now().isoformat()
    st.session_state.total_turns = 0
    st.session_state.total_research_queries = 0

    # Reset agent status
    for agent in st.session_state.agent_status:
        st.session_state.agent_status[agent] = "idle"
