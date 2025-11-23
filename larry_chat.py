"""
Larry Chat Handler - Fast Streaming with Intelligent Routing
Primary: Gemini File Search (fast, streaming)
Secondary: Neo4j and Web Search (when intelligently detected)
"""

import os
import json
from typing import Iterator, Optional
import google.generativeai as genai
from google.generativeai import types

from larry_router import route_query, should_use_streaming, get_route_description
from larry_neo4j_tool import Neo4jQueryTool, is_neo4j_configured
from larry_tools import WebSearchTool
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT


class LarryChat:
    """Main chat handler with intelligent routing and streaming support."""
    
    def __init__(self):
        """Initialize chat handler with Gemini and tools."""
        self.gemini_api_key = os.getenv("GOOGLE_AI_API_KEY")
        self.file_search_store = self._load_file_search_store()
        
        # Initialize tools
        self.neo4j_tool = Neo4jQueryTool() if is_neo4j_configured() else None
        self.web_search_tool = WebSearchTool()
        
        # Initialize Gemini client
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        else:
            self.gemini_client = None
    
    def _load_file_search_store(self) -> Optional[str]:
        """Load file search store name from configuration."""
        try:
            if os.path.exists("larry_store_info.json"):
                with open("larry_store_info.json", "r") as f:
                    store_info = json.load(f)
                    return store_info.get("store_name")
        except Exception as e:
            print(f"Failed to load file search store: {e}")
        return None
    
    def chat(self, user_message: str, conversation_history: list = None) -> Iterator[str]:
        """
        Process a chat message with intelligent routing and streaming.
        
        Args:
            user_message: The user's input message
            conversation_history: List of previous messages for context
            
        Yields:
            Response chunks (for streaming) or complete response
        """
        # Route the query
        route = route_query(user_message)
        
        # Handle based on route
        if route == "neo4j" and self.neo4j_tool:
            yield from self._handle_neo4j(user_message)
        elif route == "web_search":
            yield from self._handle_web_search(user_message)
        else:  # file_search (default)
            yield from self._handle_file_search(user_message, conversation_history)
    
    def _handle_file_search(self, user_message: str, conversation_history: list = None) -> Iterator[str]:
        """Handle file search with Gemini streaming."""
        if not self.gemini_client:
            yield "⚠️ Gemini is not configured. Please set GOOGLE_AI_API_KEY."
            return
        
        try:
            # Build conversation context
            contents = []
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
            # Add current message
            contents.append({"role": "user", "parts": [{"text": user_message}]})
            
            # Configure generation with file search
            config = types.GenerateContentConfig(
                system_instruction=LARRY_SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=8192
            )
            
            # Add file search tool if available
            if self.file_search_store:
                config.tools = [
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.file_search_store]
                        )
                    )
                ]
            
            # Stream response using Gemini 2.0 Flash (latest experimental model)
            response = self.gemini_client.models.generate_content_stream(
                model="gemini-2.0-flash-exp",
                contents=contents,
                config=config
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"⚠️ Error: {str(e)}"
    
    def _handle_neo4j(self, user_message: str) -> Iterator[str]:
        """Handle Neo4j knowledge graph queries."""
        if not self.neo4j_tool:
            yield "⚠️ Neo4j is not configured. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD."
            return
        
        try:
            # Neo4j tool returns complete response (not streaming)
            result = self.neo4j_tool._run(user_message)
            yield result
        except Exception as e:
            yield f"⚠️ Neo4j Error: {str(e)}"
    
    def _handle_web_search(self, user_message: str) -> Iterator[str]:
        """Handle web search queries."""
        try:
            # Web search tool returns complete response (not streaming)
            result = self.web_search_tool._run(user_message)
            yield result
        except Exception as e:
            yield f"⚠️ Web Search Error: {str(e)}"


def create_chat_handler() -> LarryChat:
    """Factory function to create a chat handler."""
    return LarryChat()
