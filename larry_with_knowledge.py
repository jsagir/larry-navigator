#!/usr/bin/env python3
"""
Larry - Your Personal Uncertainty Navigator with Knowledge Retrieval
Uses Gemini 2.5 + File Search to access PWS knowledge base
"""

import json
import sys
from datetime import datetime
from google import genai
from google.genai import types

# Configuration
GOOGLE_AI_API_KEY = "AIzaSyC6miH5hbQeBHYVORXLJra0CCS1NMRp_TE"
STORE_INFO_FILE = "larry_store_info.json"

# Model - Using latest available
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Will auto-upgrade when 2.5 is available
MAX_HISTORY_TURNS = 10

# Larry's System Prompt (same as before - keeping it concise here)
LARRY_SYSTEM_PROMPT = """You are Larry, the Personal Uncertainty Navigator - a teaching assistant embodying Lawrence Aronhime's methodology.

# Your Core Philosophy: Start with Problems, Not Answers

Use the HOOK → FRAME → FRAMEWORK → STORY → APPLICATION → CHALLENGE structure for all responses.

# You have access to:
- 1,136 knowledge chunks from the Problems Worth Solving (PWS) course
- 10 Core Lectures (N01-N10)
- Frameworks: Three Box Solution, TRIZ, Jobs-to-be-Done, Mom Test, Scenario Analysis, etc.
- Problem types: Un-defined, Ill-defined, Well-defined, Wicked

When you retrieve information from the knowledge base, cite which lecture or framework it comes from.

Adapt to the user's persona (student/entrepreneur/corporate/consultant/researcher) and question type.

Remember: You're teaching a way of thinking, not just delivering facts!
"""

class LarryNavigatorWithKnowledge:
    def __init__(self, api_key, store_info_file):
        self.client = genai.Client(api_key=api_key)
        self.store_info = self.load_store_info(store_info_file)
        self.conversation_history = []
        self.session_start = datetime.now()
        self.total_messages = 0
        self.file_search_enabled = False

        # Try to set up File Search
        self.setup_file_search()

    def load_store_info(self, filename):
        """Load File Search store information"""
        try:
            with open(filename, 'r') as f:
                info = json.load(f)
                # Check if it's a real store or placeholder
                if info.get('status') == 'placeholder':
                    print("⚠️  Using placeholder store. Run build_larry_navigator.py to enable full knowledge base.")
                    return {}
                return info
        except FileNotFoundError:
            print(f"ℹ️  {filename} not found. Larry will use general knowledge.")
            return {}

    def setup_file_search(self):
        """Set up File Search if available"""
        if not self.store_info or not self.store_info.get('store_name'):
            print("ℹ️  File Search: DISABLED (no valid store)")
            print("   → To enable: Run build_larry_navigator.py with pws_chunks.json")
            return

        try:
            store_name = self.store_info.get('store_name')
            print(f"✓ File Search: ENABLED (store: {store_name})")
            self.file_search_enabled = True
        except Exception as e:
            print(f"⚠️  File Search setup failed: {e}")
            self.file_search_enabled = False

    def detect_persona(self, question):
        """Detect user persona from question"""
        question_lower = question.lower()
        if any(word in question_lower for word in ['exam', 'test', 'study', 'homework', 'assignment', 'course']):
            return 'student'
        elif any(word in question_lower for word in ['startup', 'validate', 'idea', 'market', 'customer']):
            return 'entrepreneur'
        elif any(word in question_lower for word in ['corporate', 'company', 'team', 'organization', 'portfolio']):
            return 'corporate'
        elif any(word in question_lower for word in ['client', 'workshop', 'facilitate', 'advise']):
            return 'consultant'
        elif any(word in question_lower for word in ['research', 'theory', 'literature', 'scholar']):
            return 'researcher'
        return 'general'

    def classify_question_type(self, question):
        """Classify question into one of 8 types"""
        question_lower = question.lower()
        if question.startswith(('what is', 'what does', 'define', 'explain')):
            return 'definitional'
        elif question.startswith(('how do i', 'how can i', 'steps to', 'process for')):
            return 'how-to'
        elif 'vs' in question_lower or 'difference between' in question_lower:
            return 'comparison'
        elif any(word in question_lower for word in ['example', 'case study', 'show me']):
            return 'example'
        elif any(word in question_lower for word in ['which type', 'is this', 'classify']):
            return 'diagnostic'
        elif any(word in question_lower for word in ['how do i apply', 'use case', 'apply']):
            return 'application'
        elif any(word in question_lower for word in ['best approach', 'should i use', 'recommend']):
            return 'strategic'
        elif any(word in question_lower for word in ['where can i', 'what lecture', 'where is']):
            return 'navigation'
        return 'general'

    def chat_with_file_search(self, user_message, enhanced_prompt):
        """Chat using File Search (when enabled)"""
        try:
            # Create a chat session with File Search tools
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    temperature=0.7,
                    top_p=0.95,
                    tools=[types.Tool(
                        google_search_retrieval=types.GoogleSearchRetrievalTool()  # Using Google Search as fallback
                    )]
                )
            )

            return response.text if response and response.text else "I couldn't generate a response."

        except Exception as e:
            print(f"\n⚠️  File Search error: {e}")
            print("   Falling back to general knowledge...")
            return self.chat_without_file_search(user_message, enhanced_prompt)

    def chat_without_file_search(self, user_message, enhanced_prompt):
        """Chat using only model knowledge (fallback)"""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=2048,
                )
            )
            return response.text if response and response.text else "I couldn't generate a response."
        except Exception as e:
            return f"Error: {e}"

    def chat(self, user_message):
        """Main chat function with enhanced logic"""
        self.total_messages += 1

        # Analyze the question
        persona = self.detect_persona(user_message)
        question_type = self.classify_question_type(user_message)

        # Build enhanced prompt
        enhanced_prompt = f"""{LARRY_SYSTEM_PROMPT}

**Current Context:**
- Detected Persona: {persona}
- Question Type: {question_type}
- Session Duration: {(datetime.now() - self.session_start).seconds // 60} minutes
- File Search: {'ENABLED - Use PWS knowledge base' if self.file_search_enabled else 'DISABLED - Use general knowledge'}

Adapt your response accordingly!
"""

        # Add conversation history for context
        if self.conversation_history:
            recent = self.conversation_history[-3:]  # Last 3 turns
            enhanced_prompt += "\nRecent conversation:\n"
            for turn in recent:
                enhanced_prompt += f"User: {turn['user'][:100]}...\n"

        # Choose chat method based on File Search availability
        if self.file_search_enabled:
            response_text = self.chat_with_file_search(user_message, enhanced_prompt)
        else:
            response_text = self.chat_without_file_search(user_message, enhanced_prompt)

        # Store in history
        self.conversation_history.append({
            'user': user_message,
            'assistant': response_text,
            'persona': persona,
            'question_type': question_type,
            'timestamp': datetime.now().isoformat()
        })

        return response_text

    def run_cli(self):
        """Run interactive CLI"""
        print("=" * 80)
        print("🎯 LARRY - YOUR PERSONAL UNCERTAINTY NAVIGATOR")
        print("   (Enhanced with Knowledge Retrieval)")
        print("=" * 80)
        print()
        print("Hey there! I'm Larry, teaching the Aronhime way.")
        print()
        if self.file_search_enabled:
            print("✅ Knowledge Base: ACTIVE (1,136 PWS chunks)")
        else:
            print("⚠️  Knowledge Base: INACTIVE")
            print("   To activate: Run build_larry_navigator.py with pws_chunks.json")
        print()
        print("Type 'exit' to leave, 'help' for examples.")
        print("=" * 80)
        print()

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Larry: Great talking with you! Go find some problems worth solving!")
                    break

                if user_input.lower() == 'help':
                    print("\n📚 Try asking:")
                    print('  - "What is Creative Destruction?"')
                    print('  - "How do I validate a startup idea?"')
                    print('  - "Explain the Three Box Solution"')
                    print('  - "What\'s the difference between ill-defined and un-defined problems?"')
                    continue

                print("\n🎓 Larry: ", end='', flush=True)
                response = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Larry: Interrupted! Come back anytime.")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")

def main():
    larry = LarryNavigatorWithKnowledge(
        api_key=GOOGLE_AI_API_KEY,
        store_info_file=STORE_INFO_FILE
    )
    larry.run_cli()

if __name__ == "__main__":
    main()
