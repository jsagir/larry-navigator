import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents import initialize_agent, AgentExecutor, AgentType, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import the tools and system prompt
from larry_tools import UncertaintyNavigatorTool
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT

# --- Agent Initialization and Execution ---

def initialize_larry_agent():
    """Initializes the LangChain Agent with Anthropic Claude and tools."""
    # 1. Initialize LLM
    # Use the ANTHROPIC_API_KEY environment variable
    try:
        llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.2,
            max_tokens=4096
        )
    except Exception as e:
        # Fallback for local testing if key is missing
        print(f"Anthropic LLM initialization failed: {e}. Check ANTHROPIC_API_KEY.")
        return None

    # 2. Define Tools
    tools = [
        UncertaintyNavigatorTool()
    ]

    # 3. Initialize Memory
    # Use a window of 5 turns to keep the conversation focused
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,
        return_messages=True,
        output_key="output"
    )

    # 4. Initialize Agent
    # Use the stable initialize_agent function with the CONVERSATIONAL_REACT_DESCRIPTION agent type
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": LARRY_SYSTEM_PROMPT
        }
    )
    
    return agent

def chat_with_larry_agent(user_input: str, agent):
    """Executes a single turn of the conversation with the LangChain Agent."""
    if not agent:
        return "Error: Larry Agent is not initialized. Please check your API keys."

    # The agent's memory handles the history, so we just pass the new input
    response = agent.invoke({"input": user_input})
    
    # The response structure depends on the agent type, but for CONVERSATIONAL_REACT_DESCRIPTION,
    # the final output is usually in the 'output' key.
    return response.get("output", "I'm sorry, I couldn't process that request.")

def get_current_state(agent):
    """Retrieves the current state (persona, problem type, etc.) from the agent's memory or context."""
    # For this simple agent, we can't easily retrieve the internal state, 
    # but we can return a placeholder based on the system prompt's intent.
    # In a real-world scenario, the agent would have a custom tool to set/get state.
    return {
        "persona": "Entrepreneur",
        "problem_type": "Ill-Defined",
        "risk_level": "High"
    }
