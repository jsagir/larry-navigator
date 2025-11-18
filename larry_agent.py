import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain.memory import ConversationBufferWindowMemory

# Import the tools and system prompt
from larry_tools import UncertaintyNavigatorTool, ContextUpdateTool
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT

# --- Agent Initialization and Execution ---

def initialize_larry_agent():
    """Initializes the LangChain Agent with Anthropic Claude and tools."""
    # 1. Initialize LLM
    # Use the ANTHROPIC_API_KEY environment variable
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0.2,
            max_tokens=4096
        )
    except Exception as e:
        # Fallback for local testing if key is missing
        print(f"Anthropic LLM initialization failed: {e}. Check ANTHROPIC_API_KEY.")
        return None

    # 2. Define Tools
    tools = [
        UncertaintyNavigatorTool(),
        ContextUpdateTool()
    ]

    # 3. Initialize Memory
    # Use a window of 5 turns to keep the conversation focused
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,
        return_messages=True,
        output_key="output"
    )

    # 4. Initialize Agent with LangChain 0.2+ API
    # Create a conversational prompt template
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", LARRY_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor

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
    # Extract state from the agent's memory
    # The ContextUpdateTool stores state in the conversation history
    try:
        memory = agent.memory
        if memory and hasattr(memory, 'chat_memory'):
            messages = memory.chat_memory.messages
            # Search for the most recent state update from ContextUpdateTool
            for message in reversed(messages):
                if hasattr(message, 'content') and 'persona' in message.content:
                    try:
                        import json
                        state = json.loads(message.content)
                        return {
                            "persona": state.get("persona", "general"),
                            "problem_type": state.get("problem_type", "general"),
                            "uncertainty_score": state.get("uncertainty_score", 50),
                            "risk_score": state.get("risk_score", 50),
                            "recommended_frameworks": []
                        }
                    except:
                        pass
    except:
        pass
    
    # Default state if no updates found
    return {
        "persona": "general",
        "problem_type": "general",
        "uncertainty_score": 50,
        "risk_score": 50,
        "recommended_frameworks": []
    }
