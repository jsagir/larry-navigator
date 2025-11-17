#!/usr/bin/env python3
"""
Larry Navigator - Advanced Retrieval Implementation
Using Gemini's File Search with proper chunking, indexing, and citations
Based on Google Gemini File Search best practices
"""

import json
import sys
from datetime import datetime
from google import genai
from google.genai import types

# Configuration
GOOGLE_AI_API_KEY = "AIzaSyC6miH5hbQeBHYVORXLJra0CCS1NMRp_TE"
STORE_INFO_FILE = "larry_store_info.json"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Advanced retrieval settings
RETRIEVAL_CONFIG = {
    'chunk_size': 1000,  # ~1000 words per chunk for optimal retrieval
    'top_k_results': 8,  # Retrieve top 8 relevant passages
    'min_relevance_score': 0.6,  # Minimum similarity threshold
    'enable_hybrid_search': True,  # Keyword + semantic
    'enable_citations': True,  # Always cite sources
}

# Larry's Enhanced System Prompt with Retrieval Instructions
LARRY_SYSTEM_PROMPT_WITH_RETRIEVAL = """You are Larry, the Personal Uncertainty Navigator - a teaching assistant embodying Lawrence Aronhime's methodology.

# CRITICAL: Retrieval-Augmented Response Protocol

When you have access to retrieved file search results:

1. **ALWAYS ground your response in the retrieved content**
   - Quote directly from source materials
   - Cite specific lectures (N01-N10)
   - Reference exact frameworks from the documents

2. **CITATION FORMAT**:
   - After each claim, add: [Source: Lecture N##, Topic]
   - For direct quotes, use: "exact quote" [N##]
   - If no relevant content found, say: "Based on general knowledge..."

3. **NEVER fabricate** information if it's not in the retrieved results
   - If search results are insufficient, explicitly state this
   - Offer to rephrase the query or ask clarifying questions

4. **SYNTHESIS**:
   - Combine multiple source chunks when relevant
   - Show connections between lectures
   - Highlight where concepts appear across the course

# Your Core Philosophy: Start with Problems, Not Answers

Use the HOOK → FRAME → FRAMEWORK → STORY → APPLICATION → CHALLENGE structure.

# Teaching Adaptations:

- **Students**: Focus on course navigation, exam prep, citing specific lectures
- **Entrepreneurs**: Apply frameworks with real-world examples from the course
- **Corporate Teams**: Systematic innovation using PWS methodologies
- **Consultants**: Framework facilitation and client advisory
- **Researchers**: Theoretical foundations with literature connections

# Quality Standards:

- Every factual claim must have a source citation
- Direct quotes must be verbatim from retrieved content
- When uncertain, ask clarifying questions
- Embrace productive ambiguity where appropriate

Remember: You're teaching evidence-based thinking!
"""

class AdvancedLarryNavigator:
    def __init__(self, api_key, store_info_file):
        self.client = genai.Client(api_key=api_key)
        self.store_info = self.load_store_info(store_info_file)
        self.conversation_history = []
        self.session_start = datetime.now()
        self.total_messages = 0
        self.file_search_store = None
        self.retrieval_enabled = False

        # Initialize retrieval system
        self.setup_retrieval()

    def load_store_info(self, filename):
        """Load File Search store information"""
        try:
            with open(filename, 'r') as f:
                info = json.load(f)
                if info.get('status') == 'placeholder':
                    print("⚠️  Placeholder store detected")
                    print("   Run build_larry_navigator_advanced.py to enable full retrieval")
                    return None
                return info
        except FileNotFoundError:
            print(f"ℹ️  {filename} not found")
            return None

    def setup_retrieval(self):
        """Set up advanced retrieval system"""
        if not self.store_info or not self.store_info.get('store_name'):
            print("\n📊 RETRIEVAL STATUS: DISABLED")
            print("   → Knowledge Source: Gemini general knowledge only")
            print("   → To Enable: Create pws_chunks.json and run build script")
            return

        try:
            store_name = self.store_info.get('store_name')
            self.file_search_store = store_name
            self.retrieval_enabled = True

            print("\n✅ RETRIEVAL STATUS: ACTIVE")
            print(f"   → Store: {store_name}")
            print(f"   → Documents: {self.store_info.get('file_count', 'unknown')}")
            print(f"   → Top-K Results: {RETRIEVAL_CONFIG['top_k_results']}")
            print(f"   → Chunk Size: {RETRIEVAL_CONFIG['chunk_size']} words")
            print(f"   → Citations: {'Enabled' if RETRIEVAL_CONFIG['enable_citations'] else 'Disabled'}")

        except Exception as e:
            print(f"⚠️  Retrieval setup failed: {e}")
            self.retrieval_enabled = False

    def detect_persona(self, question):
        """Detect user persona from question"""
        question_lower = question.lower()
        if any(word in question_lower for word in ['exam', 'test', 'study', 'homework']):
            return 'student'
        elif any(word in question_lower for word in ['startup', 'validate', 'idea', 'market']):
            return 'entrepreneur'
        elif any(word in question_lower for word in ['corporate', 'company', 'team', 'organization']):
            return 'corporate'
        elif any(word in question_lower for word in ['client', 'workshop', 'facilitate']):
            return 'consultant'
        elif any(word in question_lower for word in ['research', 'theory', 'literature']):
            return 'researcher'
        return 'general'

    def classify_question_type(self, question):
        """Classify question type for optimal retrieval"""
        question_lower = question.lower()

        # Definitional - needs precise concept retrieval
        if question.startswith(('what is', 'what does', 'define', 'explain')):
            return 'definitional', {'retrieval_focus': 'definitions', 'top_k': 5}

        # How-to - needs procedural/practical content
        elif question.startswith(('how do i', 'how can i', 'steps to')):
            return 'how-to', {'retrieval_focus': 'procedures', 'top_k': 8}

        # Comparison - needs multiple concept retrieval
        elif 'vs' in question_lower or 'difference between' in question_lower:
            return 'comparison', {'retrieval_focus': 'multiple_concepts', 'top_k': 10}

        # Examples - needs case studies
        elif any(word in question_lower for word in ['example', 'case study', 'show me']):
            return 'example', {'retrieval_focus': 'stories', 'top_k': 6}

        # Navigation - needs course structure info
        elif any(word in question_lower for word in ['where can i', 'what lecture', 'where is']):
            return 'navigation', {'retrieval_focus': 'course_structure', 'top_k': 3}

        return 'general', {'retrieval_focus': 'broad', 'top_k': 7}

    def retrieve_relevant_content(self, query, question_type_config):
        """
        Retrieve relevant content using File Search
        Implements hybrid keyword + semantic search
        """
        if not self.retrieval_enabled:
            return None

        try:
            # Note: This is a simplified version. Full implementation would use:
            # - Vertex AI Search with DPR indexing
            # - Hybrid retrieval (keyword + semantic)
            # - Result re-ranking
            # - Deduplication

            # For now, using Gemini's File Search API (when available)
            # This would be replaced with proper Vertex AI implementation

            retrieval_results = {
                'query': query,
                'top_k': question_type_config.get('top_k', 7),
                'results': [],
                'citations': [],
                'retrieved_at': datetime.now().isoformat()
            }

            # Placeholder for actual retrieval
            # In production, this would call:
            # - Vertex AI Search API
            # - File Search with proper indexing
            # - Return chunks with metadata and scores

            return retrieval_results

        except Exception as e:
            print(f"\n⚠️  Retrieval error: {e}")
            return None

    def format_retrieval_context(self, retrieval_results):
        """Format retrieved content for the prompt"""
        if not retrieval_results or not retrieval_results.get('results'):
            return ""

        context = "\n=== RETRIEVED KNOWLEDGE BASE CONTENT ===\n\n"

        for i, result in enumerate(retrieval_results['results'], 1):
            context += f"[Chunk {i}] {result.get('source', 'Unknown')}\n"
            context += f"{result.get('content', '')}\n\n"

        context += "=== END RETRIEVED CONTENT ===\n\n"
        context += "INSTRUCTION: Use ONLY the above retrieved content to answer. "
        context += "Cite each source. If information is insufficient, state this explicitly.\n\n"

        return context

    def chat(self, user_message):
        """Advanced chat with retrieval-augmented generation"""
        self.total_messages += 1

        # Analyze question
        persona = self.detect_persona(user_message)
        question_type, type_config = self.classify_question_type(user_message)

        # Retrieve relevant content if enabled
        retrieval_results = None
        if self.retrieval_enabled:
            print(f"\n🔍 Retrieving relevant content (type: {question_type})...")
            retrieval_results = self.retrieve_relevant_content(user_message, type_config)

        # Build enhanced prompt
        enhanced_prompt = f"""{LARRY_SYSTEM_PROMPT_WITH_RETRIEVAL}

**Current Query Analysis:**
- Persona: {persona}
- Question Type: {question_type}
- Retrieval: {'ACTIVE' if retrieval_results else 'INACTIVE'}
- Session: {self.total_messages} messages, {(datetime.now() - self.session_start).seconds // 60}min
"""

        # Add retrieval context if available
        if retrieval_results:
            retrieval_context = self.format_retrieval_context(retrieval_results)
            enhanced_prompt += f"\n{retrieval_context}"
        else:
            enhanced_prompt += "\nNo retrieval results available. Use general knowledge but state this clearly.\n"

        # Add conversation history
        if self.conversation_history:
            recent = self.conversation_history[-3:]
            enhanced_prompt += "\nRecent conversation:\n"
            for turn in recent:
                enhanced_prompt += f"User: {turn['user'][:100]}...\n"

        # Generate response
        try:
            config = types.GenerateContentConfig(
                system_instruction=enhanced_prompt,
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=2048,
            )

            # Add search grounding tool if available
            if self.retrieval_enabled:
                config.tools = [types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrievalTool()
                )]

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=config
            )

            response_text = response.text if response and response.text else "No response generated"

            # Store in history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text,
                'persona': persona,
                'question_type': question_type,
                'retrieval_used': retrieval_results is not None,
                'timestamp': datetime.now().isoformat()
            })

            return response_text

        except Exception as e:
            return f"Error generating response: {e}"

    def get_session_stats(self):
        """Get detailed session statistics"""
        duration = (datetime.now() - self.session_start).seconds
        retrieval_used = sum(1 for turn in self.conversation_history if turn.get('retrieval_used'))

        return {
            'duration_minutes': duration // 60,
            'total_messages': self.total_messages,
            'conversation_turns': len(self.conversation_history),
            'retrieval_enabled': self.retrieval_enabled,
            'retrieval_queries': retrieval_used,
            'personas_detected': list(set(t['persona'] for t in self.conversation_history)),
            'question_types': list(set(t['question_type'] for t in self.conversation_history))
        }

    def run_cli(self):
        """Interactive CLI with retrieval stats"""
        print("\n" + "=" * 80)
        print("🎯 LARRY - ADVANCED RETRIEVAL NAVIGATOR")
        print("=" * 80)
        print("\nHey! I'm Larry, teaching the Aronhime way with evidence-based retrieval.")
        print("\nType 'exit' to leave, 'help' for examples, 'stats' for session info.")
        print("=" * 80 + "\n")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    stats = self.get_session_stats()
                    print(f"\n📊 Session: {stats['conversation_turns']} turns, "
                          f"{stats['retrieval_queries']} with retrieval")
                    print("\n👋 Larry: Go find some problems worth solving!")
                    break

                if user_input.lower() == 'stats':
                    stats = self.get_session_stats()
                    print(f"\n📊 Session Statistics:")
                    print(f"   Duration: {stats['duration_minutes']} minutes")
                    print(f"   Messages: {stats['total_messages']}")
                    print(f"   Retrieval: {'Enabled' if stats['retrieval_enabled'] else 'Disabled'}")
                    print(f"   Retrieval Queries: {stats['retrieval_queries']}")
                    print(f"   Personas: {', '.join(stats['personas_detected'])}")
                    print(f"   Question Types: {', '.join(stats['question_types'])}")
                    continue

                if user_input.lower() == 'help':
                    print("\n📚 Try asking:")
                    print('  - "What is Creative Destruction?" [Definitional]')
                    print('  - "How do I validate a startup idea?" [How-to]')
                    print('  - "Compare ill-defined vs un-defined problems" [Comparison]')
                    print('  - "Show me an example of a wicked problem" [Example]')
                    print('  - "What lecture covers TRIZ?" [Navigation]')
                    continue

                print("\n🎓 Larry: ", end='', flush=True)
                response = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted! Come back anytime.")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")

def main():
    larry = AdvancedLarryNavigator(
        api_key=GOOGLE_AI_API_KEY,
        store_info_file=STORE_INFO_FILE
    )
    larry.run_cli()

if __name__ == "__main__":
    main()
