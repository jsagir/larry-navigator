"""Larry Agent - LangChain 0.1.x Stable Implementation."""
import json
import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents import initialize_agent, AgentExecutor, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import the tools and system prompt
from larry_tools import WebSearchTool
from larry_neo4j_tool import Neo4jQueryTool, is_neo4j_configured
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT
from larry_config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE_DEFAULT, CONVERSATION_MEMORY_WINDOW

# --- Agent Initialization and Execution ---

def initialize_larry_agent():
    """Initializes the LangChain Agent with Anthropic Claude and tools."""
    # 1. Initialize LLM
    try:
        llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            temperature=CLAUDE_TEMPERATURE_DEFAULT,
            max_tokens=CLAUDE_MAX_TOKENS
        )
    except Exception as e:
        error_msg = f"Failed to initialize Claude: {str(e)}"
        print(f"Anthropic LLM initialization failed: {error_msg}")
        raise Exception(error_msg)

    # 2. Define Tools
    tools = [
        WebSearchTool()
    ]
    
    # Add Neo4j tool if configured
    if is_neo4j_configured():
        tools.append(Neo4jQueryTool())
        print("✅ Neo4j Knowledge Graph tool added to agent")
    else:
        print("ℹ️ Neo4j not configured, skipping Neo4j tool")

    # 3. Initialize Memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=CONVERSATION_MEMORY_WINDOW,
        return_messages=True,
        output_key="output"
    )

    # 4. Initialize Agent using stable 0.1.x API
    # Use STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION for multi-input tool support
    try:
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
            handle_parsing_errors=True,
            agent_kwargs={
                "system_message": LARRY_SYSTEM_PROMPT,
                "prefix": LARRY_SYSTEM_PROMPT
            }
        )
        print("✅ Larry agent initialized successfully")
        return agent
    except Exception as e:
        error_msg = f"Failed to create agent: {str(e)}"
        print(f"Agent initialization failed: {error_msg}")
        raise Exception(error_msg)

def chat_with_larry_agent(user_input: str, agent):
    """Executes a single turn of the conversation with the LangChain Agent."""
    if not agent:
        return "Error: Larry Agent is not initialized. Please check your API keys."

    # The agent's memory handles the history, so we just pass the new input
    response = agent.invoke({"input": user_input})
    
    # Extract the output
    return response.get("output", "No response generated.")

# --- State Extraction Helpers ---

STATE_FIELDS = {"persona", "problem_type", "uncertainty_score", "risk_score"}


def _stringify_message_content(content) -> str:
    """Normalize message content to a plain string for parsing."""
    if isinstance(content, str):
        return content

    # LangChain messages can be a list of text blocks
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)

    return str(content)


def _extract_state_from_content(content: str):
    """Attempt to extract state JSON from a message string."""
    if not content:
        return None

    # Capture JSON either inline or inside fenced code blocks
    json_candidates = []

    # Look for JSON in fenced code blocks: ```json {...} ```
    fenced_matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL)
    json_candidates.extend(fenced_matches)

    # Look for inline JSON
    if not json_candidates and "{" in content and "}" in content:
        json_candidates.append(content[content.find("{") : content.rfind("}") + 1])

    # Try to parse each candidate
    for candidate in json_candidates:
        try:
            parsed = json.loads(candidate)
            # Verify all required fields are present
            if STATE_FIELDS.issubset(parsed):
                return parsed
        except Exception:
            continue

    return None


def get_current_state(agent):
    """Retrieve the most recent state (persona, problem_type, uncertainty, risk)."""
    default_state = {
        "persona": "general",
        "problem_type": "general",
        "uncertainty_score": 50,
        "risk_score": 50,
    }

    try:
        if hasattr(agent, "memory") and agent.memory:
            # Iterate through messages in reverse (most recent first)
            for msg in reversed(agent.memory.chat_memory.messages):
                if not hasattr(msg, "content"):
                    continue

                # Normalize message content to string
                content_str = _stringify_message_content(msg.content)

                # Try to extract state JSON
                parsed_state = _extract_state_from_content(content_str)

                if parsed_state:
                    # Merge parsed state with defaults for safety
                    return {
                        **default_state,
                        **{k: parsed_state.get(k, v) for k, v in default_state.items()}
                    }

        return default_state
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return default_state

if __name__ == '__main__':
    # Example usage
    import os
    os.environ["ANTHROPIC_API_KEY"] = "your-key-here"
    
    agent = initialize_larry_agent()
    if agent:
        print("Agent initialized successfully!")
        response = chat_with_larry_agent("Hello, I need help with a decision.", agent)
        print(f"Larry: {response}")
    else:
        print("Failed to initialize agent.")
