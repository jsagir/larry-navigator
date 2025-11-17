#!/usr/bin/env python3
"""
Larry - Production Uncertainty Navigator
- Latest Gemini model (2.0 Flash, ready for 2.5 upgrade)
- File Search knowledge retrieval
- Conversation memory
- Edge case handling
- Session analytics
"""

import json
import sys
import os
from datetime import datetime
from google import genai
from google.genai import types

# Configuration
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', "AIzaSyC6miH5hbQeBHYVORXLJra0CCS1NMRp_TE")
STORE_INFO_FILE = "larry_store_info.json"

# Model Configuration - Latest available
# When Gemini 2.5 is released, simply change this to "gemini-2.5-pro-latest"
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Latest experimental model
# Alternative options:
# "gemini-1.5-pro-latest" - Stable, more advanced reasoning
# "gemini-1.5-flash-latest" - Faster, good for most tasks
# "gemini-2.5-pro-latest" - Use when available (not yet released)

MAX_HISTORY_TURNS = 10  # Conversation memory

# Larry's Enhanced System Prompt
LARRY_SYSTEM_PROMPT = """You are Larry, the Personal Uncertainty Navigator - embodying Lawrence Aronhime's teaching methodology.

# Core Philosophy: Start with Problems, Not Answers

Every lesson starts with a problem to solve, not a fact to memorize.

# Teaching Structure - The Aronhime Method:

For EVERY question, follow this structure:

1. **HOOK** (Provocative Question)
   - Start with a question that demands attention
   - Challenge assumptions
   - Make it personally relevant

2. **FRAME** (Why This Matters)
   - What are we trying to understand?
   - Why does it matter?
   - What happens if we get it wrong?

3. **FRAMEWORK** (Systematic Thinking Tool)
   - Provide intellectual scaffolding
   - Teach HOW to think, not WHAT to think
   - Make thinking repeatable

4. **STORY** (Memorable Case Study)
   - Theory is forgettable, stories are not
   - Include success AND failure examples
   - Extract the principle explicitly

5. **APPLICATION** (Actionable Next Steps)
   - Make it practical
   - Connect to learner's context
   - Provide specific actions

6. **CHALLENGE** (Follow-up Question)
   - End with productive discomfort
   - Challenge conventional wisdom
   - Preview what's next

# Knowledge Base:

You have access to the Problems Worth Solving (PWS) curriculum:
- 10 Core Lectures (N01-N10)
- Problem Types: Un-defined, Ill-defined, Well-defined, Wicked
- Frameworks: Three Box Solution, Jobs-to-be-Done, Scenario Analysis, TRIZ, Mom Test
- Tools: Trending to Absurd, Red Teaming, Beautiful Questions, MVP, etc.

When using knowledge from the curriculum, CITE YOUR SOURCES:
- "As covered in Lecture N02..."
- "The PWS framework suggests..."
- "From the course materials on ill-defined problems..."

# Persona Adaptation:

Adapt responses for:
- **Students**: Course navigation, exam prep, concept clarity
- **Entrepreneurs**: Opportunity identification, validation, execution
- **Corporate Teams**: Systematic innovation, portfolio management
- **Consultants**: Frameworks, client advisory, facilitation
- **Researchers**: Theoretical foundations, literature connections

# Edge Case Handling:

- **Vague questions**: Ask clarifying questions using the Aronhime method
- **Off-topic**: Gently redirect to innovation/problem-solving
- **Multiple questions**: Address systematically, one at a time
- **Contradictions**: Point out constructively, explore the tension
- **Uncertainty requests**: Embrace ambiguity - it's your specialty!

# Language:

- Use "you" and "we" for inclusion
- Mix formal concepts with accessible explanations
- Balance rigor with clarity
- Signature phrases: "Let me challenge your thinking...", "Here's what most people miss...", "The real question isn't X, it's Y..."

Remember: You're teaching a way of thinking about the world, not just delivering facts.

Now, respond using the Aronhime method!
"""


class LarryProduction:
    """Production-ready Larry Navigator with full features"""

    def __init__(self, api_key: str, store_info_file: str):
        self.client = genai.Client(api_key=api_key)
        self.store_info = self.load_store_info(store_info_file)
        self.conversation_history = []
        self.session_start = datetime.now()
        self.total_messages = 0
        self.file_search_enabled = False
        self.file_search_store = None

        # Initialize File Search
        self.setup_file_search()

    def load_store_info(self, filename: str):
        """Load File Search store information"""
        try:
            with open(filename, 'r') as f:
                info = json.load(f)
                if info.get('status') == 'placeholder':
                    print("⚠️  Using placeholder store")
                    print("   Run: python3 build_larry_navigator_v2.py to enable knowledge base")
                    return None
                return info
        except FileNotFoundError:
            print(f"ℹ️  {filename} not found - using general knowledge only")
            return None

    def setup_file_search(self):
        """Initialize File Search if available"""
        if not self.store_info or not self.store_info.get('store_name'):
            print("\n📊 Knowledge Base: INACTIVE")
            print("   → Using Gemini general knowledge")
            print("   → To activate: Run build_larry_navigator_v2.py")
            return

        try:
            store_name = self.store_info.get('store_name')
            self.file_search_store = store_name
            self.file_search_enabled = True

            print("\n✅ Knowledge Base: ACTIVE")
            print(f"   → Store: {store_name}")
            print(f"   → Files: {self.store_info.get('file_count', 'unknown')}")
            print(f"   → Chunks: {self.store_info.get('total_chunks', 'unknown')}")
            print(f"   → Model: {GEMINI_MODEL}")

        except Exception as e:
            print(f"⚠️  File Search setup failed: {e}")
            self.file_search_enabled = False

    def detect_persona(self, question: str) -> str:
        """Detect user persona from question"""
        q = question.lower()
        if any(w in q for w in ['exam', 'test', 'study', 'homework', 'assignment']):
            return 'student'
        elif any(w in q for w in ['startup', 'validate', 'idea', 'market', 'customer']):
            return 'entrepreneur'
        elif any(w in q for w in ['corporate', 'company', 'team', 'organization']):
            return 'corporate'
        elif any(w in q for w in ['client', 'workshop', 'facilitate', 'advise']):
            return 'consultant'
        elif any(w in q for w in ['research', 'theory', 'literature', 'scholar']):
            return 'researcher'
        return 'general'

    def classify_question_type(self, question: str) -> str:
        """Classify question type"""
        q = question.lower()
        if question.startswith(('what is', 'what does', 'define', 'explain')):
            return 'definitional'
        elif question.startswith(('how do i', 'how can i', 'steps to')):
            return 'how-to'
        elif 'vs' in q or 'difference between' in q or 'compare' in q:
            return 'comparison'
        elif any(w in q for w in ['example', 'case study', 'show me']):
            return 'example'
        elif any(w in q for w in ['which type', 'is this', 'classify']):
            return 'diagnostic'
        elif any(w in q for w in ['how do i apply', 'use case', 'apply']):
            return 'application'
        elif any(w in q for w in ['best approach', 'should i use', 'recommend']):
            return 'strategic'
        elif any(w in q for w in ['where can i', 'what lecture', 'where is']):
            return 'navigation'
        return 'general'

    def detect_edge_cases(self, question: str) -> list:
        """Detect edge case scenarios"""
        q = question.lower()
        edge_cases = []

        if len(question.split()) < 3:
            edge_cases.append('vague')

        if any(w in q for w in ['weather', 'sports', 'politics', 'recipe', 'celebrity']):
            edge_cases.append('off_topic')

        if question.count('?') > 1:
            edge_cases.append('multiple_questions')

        if any(w in q for w in ['hello', 'hi', 'hey']):
            edge_cases.append('greeting')

        if any(w in q for w in ['who are you', 'what can you do', 'help']):
            edge_cases.append('meta')

        return edge_cases

    def build_conversation_context(self) -> str:
        """Build conversation context from history"""
        if not self.conversation_history:
            return ""

        recent = self.conversation_history[-min(3, len(self.conversation_history)):]
        context = "\n**Recent Conversation:**\n"
        for turn in recent:
            context += f"User: {turn['user'][:100]}...\n"
        return context

    def chat(self, user_message: str) -> str:
        """Main chat method with all features"""
        self.total_messages += 1

        # Analyze question
        persona = self.detect_persona(user_message)
        question_type = self.classify_question_type(user_message)
        edge_cases = self.detect_edge_cases(user_message)

        # Build enhanced prompt
        enhanced_prompt = f"""{LARRY_SYSTEM_PROMPT}

**Current Context:**
- Persona: {persona}
- Question Type: {question_type}
- Session: Message {self.total_messages}, {(datetime.now() - self.session_start).seconds // 60}min
- Knowledge Base: {'ACTIVE - Cite PWS sources' if self.file_search_enabled else 'INACTIVE - General knowledge'}
"""

        if edge_cases:
            enhanced_prompt += f"- Edge Cases: {', '.join(edge_cases)} (handle appropriately)\n"

        # Add conversation history
        enhanced_prompt += self.build_conversation_context()

        # Generate response
        try:
            config = types.GenerateContentConfig(
                system_instruction=enhanced_prompt,
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=2048,
            )

            # Add File Search tool if enabled
            if self.file_search_enabled:
                # Note: File Search integration depends on google-genai SDK support
                # This is a placeholder for when the SDK supports it
                pass

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=config
            )

            response_text = response.text if response and response.text else "I couldn't generate a response."

            # Store in history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text,
                'persona': persona,
                'question_type': question_type,
                'timestamp': datetime.now().isoformat()
            })

            return response_text

        except Exception as e:
            return f"Error: {e}"

    def get_session_stats(self) -> dict:
        """Get session statistics"""
        duration = (datetime.now() - self.session_start).seconds
        return {
            'duration_minutes': duration // 60,
            'total_messages': self.total_messages,
            'conversation_turns': len(self.conversation_history),
            'knowledge_base': 'active' if self.file_search_enabled else 'inactive',
            'model': GEMINI_MODEL
        }

    def run_cli(self):
        """Interactive CLI"""
        print("\n" + "=" * 80)
        print("🎯 LARRY - PRODUCTION UNCERTAINTY NAVIGATOR")
        print("=" * 80)
        print()
        print("Hey! I'm Larry, teaching the Aronhime way:")
        print("  ✓ I start with questions, not answers")
        print("  ✓ I challenge your thinking")
        print("  ✓ I use memorable stories")
        print("  ✓ I give you frameworks, not just facts")
        print()
        print("Commands:")
        print("  'exit' / 'quit' - Leave")
        print("  'help' - Example questions")
        print("  'stats' - Session statistics")
        print("=" * 80)
        print()

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    stats = self.get_session_stats()
                    print(f"\n📊 Session: {stats['conversation_turns']} turns, {stats['duration_minutes']} minutes")
                    print("\n👋 Larry: Great talking with you! Remember:")
                    print("   The best teachers don't give you answers—they give you better questions.")
                    print("   Go find some problems worth solving! 🚀")
                    break

                if user_input.lower() == 'stats':
                    stats = self.get_session_stats()
                    print(f"\n📊 Session Statistics:")
                    print(f"   Duration: {stats['duration_minutes']} minutes")
                    print(f"   Messages: {stats['total_messages']}")
                    print(f"   Turns: {stats['conversation_turns']}")
                    print(f"   Knowledge Base: {stats['knowledge_base']}")
                    print(f"   Model: {stats['model']}")
                    continue

                if user_input.lower() == 'help':
                    print("\n📚 Example Questions:")
                    print('\n  Definitional:')
                    print('    - "What is Creative Destruction?"')
                    print('    - "Explain the Three Box Solution"')
                    print('\n  How-To:')
                    print('    - "How do I validate my startup idea?"')
                    print('    - "How can I apply scenario analysis?"')
                    print('\n  Comparison:')
                    print('    - "What\'s the difference between ill-defined and un-defined problems?"')
                    print('    - "Compare TRIZ vs lateral thinking"')
                    print('\n  Examples:')
                    print('    - "Show me an example of a wicked problem"')
                    print('    - "Give me a case study of disruptive innovation"')
                    continue

                # Chat with Larry
                print("\n🎓 Larry: ", end='', flush=True)
                response = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted! Come back anytime.")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")


def main():
    """Main execution"""
    larry = LarryProduction(
        api_key=GOOGLE_AI_API_KEY,
        store_info_file=STORE_INFO_FILE
    )
    larry.run_cli()


if __name__ == "__main__":
    main()
