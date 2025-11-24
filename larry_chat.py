"""
Larry Chat Handler - Fast Streaming with Intelligent Routing
Primary: Gemini File Search (fast, streaming)
Secondary: Neo4j and Web Search (when intelligently detected)
"""

import os
import json
from typing import Iterator, Optional
from google import genai
from google.genai import types

from larry_router import route_query, should_use_streaming, get_route_description
# Neo4j tool temporarily disabled - importing from correct module
from larry_neo4j_rag import is_neo4j_configured
from larry_tools import WebSearchTool
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT


class LarryChat:
    """Main chat handler with intelligent routing and streaming support."""
    
    def __init__(self):
        """Initialize chat handler with Gemini and tools."""
        self.gemini_api_key = os.getenv("GOOGLE_AI_API_KEY")
        self.file_search_store = self._load_file_search_store()

        # Initialize tools
        # Neo4j tool temporarily disabled
        self.neo4j_tool = None
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
    
    def chat(self, user_message: str, conversation_history: list = None, show_thinking: bool = True) -> Iterator[str]:
        """
        Process a chat message with intelligent routing and streaming.

        Args:
            user_message: The user's input message
            conversation_history: List of previous messages for context
            show_thinking: Whether to display reasoning process (default: True)

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
            yield from self._handle_file_search(user_message, conversation_history, show_thinking)
    
    def _handle_file_search(self, user_message: str, conversation_history: list = None, show_thinking: bool = True) -> Iterator[str]:
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

            # Use Gemini 3 Pro Preview (best reasoning capability)
            model_name = "gemini-3-pro-preview"

            # If showing thinking, prepend reasoning instruction to user message
            if show_thinking and contents:
                last_content = contents[-1]
                original_text = last_content["parts"][0]["text"]
                reasoning_prompt = (
                    f"{original_text}\n\n"
                    "Please think through this step-by-step:\n"
                    "1. First, explain what information you're searching for\n"
                    "2. Then, show your reasoning process\n"
                    "3. Finally, provide your answer\n\n"
                    "Format your response with: **Thinking:** section first, then **Answer:** section."
                )
                contents[-1] = {"role": "user", "parts": [{"text": reasoning_prompt}]}

            # Stream response
            response = self.gemini_client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=config
            )

            thinking_shown = False
            sources_shown = False
            collected_sources = []

            for chunk in response:
                # Extract thinking/reasoning if available
                if hasattr(chunk, 'candidates') and chunk.candidates:
                    candidate = chunk.candidates[0]

                    # Check for thinking/reasoning in parts
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            # Show thinking section (if model supports it)
                            if hasattr(part, 'thought') and part.thought and not thinking_shown:
                                yield f"\n<details>\n<summary>🧠 <b>Larry's Reasoning Process</b></summary>\n\n```\n{part.thought}\n```\n</details>\n\n"
                                thinking_shown = True

                            # Collect grounding metadata (sources used)
                            if hasattr(part, 'grounding_metadata') and part.grounding_metadata:
                                if hasattr(part.grounding_metadata, 'grounding_chunks'):
                                    for grounding_chunk in part.grounding_metadata.grounding_chunks:
                                        if hasattr(grounding_chunk, 'retrieved_context'):
                                            context = grounding_chunk.retrieved_context
                                            source_info = {}

                                            if hasattr(context, 'title'):
                                                source_info['title'] = context.title
                                            if hasattr(context, 'uri'):
                                                source_info['uri'] = context.uri

                                            # Get confidence score if available
                                            if hasattr(grounding_chunk, 'grounding_score'):
                                                source_info['confidence'] = grounding_chunk.grounding_score

                                            if source_info and source_info not in collected_sources:
                                                collected_sources.append(source_info)

                # Yield main response text
                if chunk.text:
                    yield chunk.text

            # Show sources at the end (after response completes)
            if collected_sources and not sources_shown:
                yield "\n\n---\n\n"
                yield "**📚 Sources Referenced:**\n\n"
                for i, source in enumerate(collected_sources[:5], 1):
                    title = source.get('title', 'Unknown')
                    confidence = source.get('confidence', None)
                    conf_str = f" (confidence: {confidence:.2f})" if confidence else ""
                    yield f"{i}. {title}{conf_str}\n"
                sources_shown = True

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
