#!/usr/bin/env python3
"""
Larry - Your Personal Uncertainty Navigator
Chatbot with Lawrence Aronhime's teaching style
"""

import json
import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Configuration
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
STORE_INFO_FILE = "larry_store_info.json"

if not GOOGLE_AI_API_KEY:
    print("✗ Error: GOOGLE_AI_API_KEY not found!")
    print("Please create a .env file with your API key:")
    print("  GOOGLE_AI_API_KEY=your-api-key-here")
    print("\nGet your API key from: https://aistudio.google.com/apikey")
    sys.exit(1)

# Larry's System Prompt (Aronhime Style)
# Use the new comprehensive system prompt
LARRY_SYSTEM_PROMPT = LARRY_SYSTEM_PROMPT_V3

class LarryNavigator:
    def __init__(self, api_key, store_info_file):
        self.client = genai.Client(api_key=api_key)
        self.store_info = self.load_store_info(store_info_file)
        self.conversation_history = []

    def load_store_info(self, filename):
        """Load File Search store information"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"✗ Error: {filename} not found. Run build_larry_navigator.py first!")
            sys.exit(1)

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

    def chat(self, user_message):
        """Chat with Larry using File Search"""
        # Detect persona and question type
        persona = self.detect_persona(user_message)
        question_type = self.classify_question_type(user_message)

        # Add context to system prompt
        enhanced_prompt = f"{LARRY_SYSTEM_PROMPT}\n\n**Current Context:**\n- Detected Persona: {persona}\n- Question Type: {question_type}\n\nAdapt your response accordingly!"

        # Build conversation with File Search
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.store_info['store_name']]
                            )
                        )
                    ],
                    temperature=0.7,
                    top_p=0.95,
                )
            )

            # Extract response text
            if response and response.text:
                return response.text
            else:
                return "I'm sorry, I couldn't generate a response. Could you rephrase your question?"

        except Exception as e:
            return f"Error communicating with Larry: {e}"

    def run_cli(self):
        """Run interactive CLI"""
        print("=" * 80)
        print("🎯 LARRY - YOUR PERSONAL UNCERTAINTY NAVIGATOR")
        print("=" * 80)
        print()
        print("Hey there! I'm Larry, and I teach the way Professor Aronhime does:")
        print("  → I start with questions, not answers")
        print("  → I challenge your thinking")
        print("  → I use stories you'll remember")
        print("  → I give you frameworks, not just facts")
        print()
        print("I know all about Problems Worth Solving, innovation frameworks,")
        print("un-defined/ill-defined/well-defined problems, and how to navigate uncertainty.")
        print()
        print("Type 'exit' or 'quit' to leave. Type 'help' for example questions.")
        print("=" * 80)
        print()

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Larry: Great talking with you! Remember: the best teachers don't give you answers—they give you better questions. Go find some problems worth solving!")
                    break

                if user_input.lower() == 'help':
                    self.show_help()
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
