import os
import json
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents.tool_calling.create_tool_calling_agent import create_tool_calling_agent
from langchain.agents.agent_toolkits import AgentExecutor
from langchain.memory import ConversationBufferWindowMemory

# Import the tools and system prompt
from larry_tools import get_larry_tools
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3

# --- 1. Agent System Prompt ---

AGENT_SYSTEM_PROMPT = (
    LARRY_SYSTEM_PROMPT_V3 +
    "\n\n"
    "You are an intelligent conversational agent designed to help users navigate uncertainty. "
    "Your primary function is to use the provided tools to gather context and then provide "
    "a structured, insightful answer in the style of a hyper-minimalist De Stijl mentor. "
    "**ALWAYS** use the `context_update_tool` first to analyze the user's message and update the internal state. "
    "After updating the context, **ALWAYS** use the `uncertainty_navigator_tool` to generate the final, structured response."
)

# --- 2. Agent Initialization ---

def initialize_larry_agent(api_key: str, history: List[Dict[str, str]]) -> AgentExecutor:
    """
    Initializes the LangChain Agent with memory, tools, and the Anthropic Claude model.
    """
    # Note: Anthropic API Key is expected to be in the ANTHROPIC_API_KEY environment variable
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Fallback to a generic LLM if Anthropic is not configured, but warn
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.5)
    else:
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.5)

    # 2. Get Tools (Persona and Problem Type are retrieved dynamically in the tool)
    tools = get_larry_tools(persona="general", problem_type="general")

    # 3. Create Prompt Template
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # 4. Initialize Memory (to store conversation history)
    memory = ConversationBufferWindowMemory(
        k=10, # Keep the last 10 turns in memory
        memory_key="chat_history",
        return_messages=True,
        input_key="input"
    )
    
    # Load history into memory
    for message in history:
        if message["role"] == "user":
            memory.chat_memory.add_user_message(message["content"])
        elif message["role"] == "assistant":
            # The assistant's content is the structured JSON from the tool
            # We only load the final answer for the memory
            try:
                content = json.loads(message["content"])["final_answer"]
            except:
                content = message["content"]
            memory.chat_memory.add_ai_message(content)

    # 5. Create the Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 6. Create the Agent Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor

# --- 3. Main Chat Function ---

def chat_with_larry_agent(agent_executor: AgentExecutor, user_message: str) -> str:
    """
    Executes the agent with the user's message.
    The agent is expected to return the structured JSON from the UncertaintyNavigatorTool.
    """
    
    response = agent_executor.invoke({"input": user_message})
    
    # The agent's final output is the structured JSON string from the tool
    return response["output"]

# --- 4. State Retrieval Function (for Streamlit Sidebar) ---

def get_current_state(agent_executor: AgentExecutor) -> Dict[str, Any]:
    """
    Retrieves the current state (persona, problem_type, etc.) by running the ContextUpdateTool.
    """
    
    # We run the ContextUpdateTool directly to get the latest state without triggering the full agent loop.
    context_tool = next(tool for tool in agent_executor.tools if tool.name == "context_update_tool")
    
    # We need a message to analyze. We use the last user message from memory.
    last_user_message = "general inquiry"
    if agent_executor.memory.chat_memory.messages:
        for msg in reversed(agent_executor.memory.chat_memory.messages):
            if isinstance(msg, HumanMessage):
                last_user_message = msg.content
                break
    
    try:
        state_json = context_tool.run(last_user_message)
        state = json.loads(state_json)
        
        # Add recommended frameworks based on the new state
        from larry_framework_recommender import recommend_frameworks
        state["recommended_frameworks"] = recommend_frameworks(
            state["problem_type"],
            state["persona"],
            last_user_message,
            max_recommendations=3
        )
        
        return state
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return {
            "persona": "general",
            "problem_type": "general",
            "uncertainty_score": 50,
            "risk_score": 50,
            "recommended_frameworks": []
        }
