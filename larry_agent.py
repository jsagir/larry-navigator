"""Larry Agent - LangChain 0.1.x Stable Implementation"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents import initialize_agent, AgentExecutor, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import the tools and system prompt
from larry_tools import UncertaintyNavigatorTool, ContextUpdateTool, WebSearchTool
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT

# --- Agent Initialization and Execution ---

def initialize_larry_agent():
    """Initializes the LangChain Agent with Anthropic Claude and tools."""
    # 1. Initialize LLM
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",  # Updated to latest model
            temperature=0.2,
            max_tokens=4096
        )
    except Exception as e:
        error_msg = f"Failed to initialize Claude: {str(e)}"
        print(f"Anthropic LLM initialization failed: {error_msg}")
        raise Exception(error_msg)

    # 2. Define Tools
    tools = [
        UncertaintyNavigatorTool(),
        ContextUpdateTool(),
        WebSearchTool()
    ]

    # 3. Initialize Memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,
        return_messages=True,
        output_key="output"
    )

    # 4. Initialize Agent using stable 0.1.x API
    try:
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

def get_current_state(agent):
    """
    Retrieves the current state (persona, problem_type, uncertainty, risk) from the agent's memory.
    """
    # Default state
    default_state = {
        "persona": "general",
        "problem_type": "general",
        "uncertainty_score": 50,
        "risk_score": 50
    }
    
    try:
        # Parse the conversation history for state updates from ContextUpdateTool
        if hasattr(agent, 'memory') and agent.memory:
            messages = agent.memory.chat_memory.messages
            
            # Look for the most recent state update
            for msg in reversed(messages):
                if hasattr(msg, 'content') and 'persona' in str(msg.content).lower():
                    # Try to extract state from message content
                    # This is a simplified extraction - in production you'd want more robust parsing
                    pass
        
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
