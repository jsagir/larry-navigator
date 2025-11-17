#!/usr/bin/env python3
"""
Larry - Your Personal Uncertainty Navigator (Enhanced Version)
Chatbot with Lawrence Aronhime's teaching style + Gemini 2.5 Pro
"""

import json
import sys
from datetime import datetime
from google import genai
from google.genai import types

# Configuration
GOOGLE_AI_API_KEY = "AIzaSyC6miH5hbQeBHYVORXLJra0CCS1NMRp_TE"
STORE_INFO_FILE = "larry_store_info.json"

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Can upgrade to "gemini-1.5-pro-latest" or newer when available
MAX_HISTORY_TURNS = 10  # Keep last 10 conversation turns for context

# Larry's System Prompt (Aronhime Style)
LARRY_SYSTEM_PROMPT = """You are Larry, the Personal Uncertainty Navigator - a teaching assistant embodying Lawrence Aronhime's methodology.

# Your Core Philosophy: Start with Problems, Not Answers

Lawrence Aronhime's principle: *Every lesson starts with a problem to solve, not a fact to memorize.*

# Your Teaching Style - The Aronhime Response Pattern:

For EVERY question, follow this structure:

1. **HOOK** (Provocative Question)
   - Start with a question that refuses to be ignored
   - Challenge assumptions
   - Make it personally relevant

2. **FRAME** (Why This Matters)
   - Orient the learner: What are we trying to understand?
   - Why does it matter? What happens if we get it wrong?
   - What will you be able to do after understanding this?

3. **FRAMEWORK** (Systematic Thinking Tool)
   - Provide scaffolding for intellectual construction
   - Teach HOW to think, not WHAT to think
   - Make thinking repeatable and scalable

4. **STORY** (Memorable Case Study)
   - Theory is forgettable. Stories are not.
   - Include both success and failure examples
   - Extract the principle explicitly after the story

5. **APPLICATION** (What You Can Do Now)
   - Make it actionable
   - Connect to the learner's context
   - Provide next steps

6. **CHALLENGE** (Follow-up Question/Next Step)
   - End with productive discomfort
   - Challenge conventional wisdom
   - Create scenarios with no clear answer
   - Preview what's coming next

# Language Patterns:

- Use "you" and "we" to create inclusion
- Mix formal concepts with informal explanations
- Balance accessibility with intellectual rigor

## Signature Phrases:
- "Let me challenge your thinking..."
- "Here's what most people miss..."
- "The real question isn't X, it's Y..."
- "Notice what's happening here..."

## Emphasis:
- **Bold** for key concepts
- *Italics* for subtle emphasis
- Rhetorical questions for reflection
- Repetition for critical points

# Sentence Length by Context:

- **CASUAL CONVERSATION** (greetings, small talk): 2-3 sentences
- **TEACHING/SCENARIOS** (explaining concepts, frameworks): 5-6 sentences per section
- **EMERGENCY/CRISIS**: 3-4 sentences (clear, direct)

# Question Types You Handle:

1. **Definitional**: "What is X?" → Clear definition + context + where it's covered
2. **How-To**: "How do I X?" → Step-by-step + tools + examples + pitfalls
3. **Diagnostic**: "What type is this?" → Framework + characteristics + classification
4. **Comparison**: "X vs Y?" → Side-by-side + distinguishing features + when to use
5. **Application**: "How do I apply X?" → Framework + industry adaptation + examples
6. **Strategic**: "What's the best approach?" → Context assessment + recommendations
7. **Navigation**: "Where can I learn X?" → Direct links + learning path + prerequisites
8. **Examples/Cases**: "Show me an example" → Relevant cases + key learnings

# Content You Know:

- **Lectures**: N01 (Introduction), N02 (Un-Defined Problems), N03 (Ill-Defined), N04 (Wicked Problems), N05 (Domains), N06 (Portfolio), N07 (Well-Defined), N08 (Prior Art), N10 (January Term)
- **Problem Types**: Un-defined, Ill-defined, Well-defined, Wicked
- **Frameworks**: Problem Typology, Three Box Solution, Scenario Analysis, Trending to Absurd, TRIZ, Lateral Thinking, Jobs-to-be-Done, Mom Test, and many more
- **Tools**: Extensive/Intensive Searching, Nested Hierarchies, Red Teaming, Beautiful Questions, etc.

# Your Personas (Adapt your response):

1. **Students**: Focus on course navigation, concept clarity, exam prep
2. **Entrepreneurs**: Focus on opportunity identification, validation, execution
3. **Corporate Teams**: Focus on systematic innovation, portfolio management, culture
4. **Consultants**: Focus on frameworks, client advisory, facilitation
5. **Researchers**: Focus on theoretical foundations, literature, comparative analysis

# Special Instructions for Edge Cases:

- **Off-topic questions**: Gently redirect to innovation/problem-solving while being helpful
- **Vague questions**: Ask clarifying questions using the Aronhime method
- **Multiple questions**: Address them systematically, one at a time
- **Contradictions**: Point them out constructively and explore the tension
- **Requests for certainty**: Embrace uncertainty - it's your specialty!

# Remember:

- You're not just teaching content. You're teaching a way of thinking about the world.
- The best teachers don't give you the answers. They give you better questions.
- Create productive discomfort - ambiguity mirrors real-world complexity.
- Every response is an opportunity to transform passive learners into active thinkers.

Now, respond to the user's question using the Aronhime method!
"""

class LarryNavigator:
    def __init__(self, api_key, store_info_file):
        self.client = genai.Client(api_key=api_key)
        self.store_info = self.load_store_info(store_info_file)
        self.conversation_history = []
        self.session_start = datetime.now()
        self.total_messages = 0

    def load_store_info(self, filename):
        """Load File Search store information"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ℹ️  Note: {filename} not found. Larry will use general knowledge.")
            return {}

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
        else:
            return 'general'

    def classify_question_type(self, question):
        """Classify question into one of 8 types"""
        question_lower = question.lower()

        if question.startswith(('what is', 'what does', 'define', 'explain')):
            return 'definitional'
        elif question.startswith(('how do i', 'how can i', 'steps to', 'process for')):
            return 'how-to'
        elif 'vs' in question_lower or 'difference between' in question_lower or 'compare' in question_lower:
            return 'comparison'
        elif any(word in question_lower for word in ['example', 'case study', 'show me', 'demonstrate']):
            return 'example'
        elif any(word in question_lower for word in ['which type', 'is this', 'classify', 'what kind']):
            return 'diagnostic'
        elif any(word in question_lower for word in ['how do i apply', 'use case', 'apply']):
            return 'application'
        elif any(word in question_lower for word in ['best approach', 'should i use', 'recommend', 'strategy']):
            return 'strategic'
        elif any(word in question_lower for word in ['where can i', 'what lecture', 'where is']):
            return 'navigation'
        else:
            return 'general'

    def detect_edge_case(self, question):
        """Detect edge cases and special scenarios"""
        question_lower = question.lower()

        edge_cases = []

        # Vague/unclear
        if len(question.split()) < 3:
            edge_cases.append('vague')

        # Off-topic
        off_topic_keywords = ['weather', 'sports', 'politics', 'recipe', 'celebrity']
        if any(word in question_lower for word in off_topic_keywords):
            edge_cases.append('off_topic')

        # Multiple questions
        if '?' in question and question.count('?') > 1:
            edge_cases.append('multiple_questions')

        # Greeting
        if any(greeting in question_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
            edge_cases.append('greeting')

        # Meta questions about Larry
        if any(word in question_lower for word in ['who are you', 'what can you do', 'help']):
            edge_cases.append('meta')

        return edge_cases

    def build_conversation_context(self):
        """Build conversation context from history"""
        if not self.conversation_history:
            return None

        # Keep only recent history to avoid token limits
        recent_history = self.conversation_history[-MAX_HISTORY_TURNS:]

        context = "Previous conversation:\n"
        for turn in recent_history:
            context += f"User: {turn['user']}\n"
            context += f"Larry: {turn['assistant'][:200]}...\n\n"  # Truncate long responses

        return context

    def chat(self, user_message):
        """Chat with Larry using enhanced logic"""
        self.total_messages += 1

        # Detect persona, question type, and edge cases
        persona = self.detect_persona(user_message)
        question_type = self.classify_question_type(user_message)
        edge_cases = self.detect_edge_case(user_message)

        # Build enhanced prompt with context
        enhanced_prompt = f"{LARRY_SYSTEM_PROMPT}\n\n**Current Context:**\n"
        enhanced_prompt += f"- Detected Persona: {persona}\n"
        enhanced_prompt += f"- Question Type: {question_type}\n"

        if edge_cases:
            enhanced_prompt += f"- Edge Cases Detected: {', '.join(edge_cases)}\n"
            enhanced_prompt += "  → Handle these appropriately!\n"

        enhanced_prompt += f"- Session Duration: {(datetime.now() - self.session_start).seconds // 60} minutes\n"
        enhanced_prompt += f"- Messages in session: {self.total_messages}\n"

        # Add conversation history if available
        conversation_context = self.build_conversation_context()
        if conversation_context:
            enhanced_prompt += f"\n{conversation_context}"

        enhanced_prompt += "\nAdapt your response accordingly!"

        # Generate response
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    temperature=0.7,  # Balance creativity and consistency
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,  # Allow longer, more detailed responses
                )
            )

            # Extract response text
            if response and response.text:
                response_text = response.text

                # Store in conversation history
                self.conversation_history.append({
                    'user': user_message,
                    'assistant': response_text,
                    'persona': persona,
                    'question_type': question_type,
                    'timestamp': datetime.now().isoformat()
                })

                return response_text
            else:
                return "I'm sorry, I couldn't generate a response. Could you rephrase your question?"

        except Exception as e:
            return f"Error communicating with Larry: {e}"

    def get_session_stats(self):
        """Get session statistics"""
        duration = (datetime.now() - self.session_start).seconds
        return {
            'duration_minutes': duration // 60,
            'total_messages': self.total_messages,
            'conversation_turns': len(self.conversation_history)
        }

    def run_cli(self):
        """Run interactive CLI"""
        print("=" * 80)
        print("🎯 LARRY - YOUR PERSONAL UNCERTAINTY NAVIGATOR (Enhanced)")
        print("=" * 80)
        print()
        print("Hey there! I'm Larry, and I teach the way Professor Aronhime does:")
        print("  → I start with questions, not answers")
        print("  → I challenge your thinking")
        print("  → I use stories you'll remember")
        print("  → I give you frameworks, not just facts")
        print()
        print("🆕 Enhanced with:")
        print("  ✓ Conversation memory (remembers context)")
        print("  ✓ Advanced reasoning (Gemini 2.0)")
        print("  ✓ Edge case handling")
        print("  ✓ Session tracking")
        print()
        print("I know all about Problems Worth Solving, innovation frameworks,")
        print("un-defined/ill-defined/well-defined problems, and how to navigate uncertainty.")
        print()
        print("Type 'exit' or 'quit' to leave. Type 'help' for example questions.")
        print("Type 'stats' to see session statistics.")
        print("=" * 80)
        print()

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    stats = self.get_session_stats()
                    print(f"\n📊 Session Stats: {stats['conversation_turns']} turns, {stats['duration_minutes']} minutes")
                    print("\n👋 Larry: Great talking with you! Remember: the best teachers don't give you answers—they give you better questions. Go find some problems worth solving!")
                    break

                if user_input.lower() == 'help':
                    self.show_help()
                    continue

                if user_input.lower() == 'stats':
                    stats = self.get_session_stats()
                    print(f"\n📊 Session Statistics:")
                    print(f"   Duration: {stats['duration_minutes']} minutes")
                    print(f"   Total messages: {stats['total_messages']}")
                    print(f"   Conversation turns: {stats['conversation_turns']}")
                    continue

                # Chat with Larry
                print("\n🎓 Larry: ", end='', flush=True)
                response = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Larry: Interrupted! Come back anytime.")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")

    def show_help(self):
        """Show example questions"""
        print("\n" + "=" * 80)
        print("📚 EXAMPLE QUESTIONS YOU CAN ASK LARRY:")
        print("=" * 80)
        print()
        print("**For Students:**")
        print('  - "What is Creative Destruction?"')
        print('  - "How do I prepare for the exam on innovation frameworks?"')
        print('  - "What\'s the difference between un-defined and ill-defined problems?"')
        print()
        print("**For Entrepreneurs:**")
        print('  - "How do I validate my startup idea?"')
        print('  - "Is my problem un-defined, ill-defined, or well-defined?"')
        print('  - "What frameworks help with finding innovation opportunities?"')
        print()
        print("**For Corporate Teams:**")
        print('  - "How do I build a systematic innovation process?"')
        print('  - "What is the Three Box Solution?"')
        print('  - "How do I manage an innovation portfolio?"')
        print()
        print("**General:**")
        print('  - "Show me examples of wicked problems"')
        print('  - "What tools work for un-defined problems?"')
        print('  - "Tell me about Scenario Analysis"')
        print("=" * 80)

def main():
    larry = LarryNavigator(
        api_key=GOOGLE_AI_API_KEY,
        store_info_file=STORE_INFO_FILE
    )
    larry.run_cli()

if __name__ == "__main__":
    main()
