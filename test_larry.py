#!/usr/bin/env python3
"""
Test Larry with a sample question
"""

import sys
import os
sys.path.insert(0, '/home/jsagi')

from larry_chatbot import LarryNavigator

# Initialize Larry
print("Initializing Larry...")
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_AI_API_KEY not set!")
    print("Set it with: export GOOGLE_AI_API_KEY=your-key-here")
    sys.exit(1)

larry = LarryNavigator(
    api_key=api_key,
    store_info_file="larry_store_info.json"
)
print("✓ Larry initialized!\n")

# Test questions
test_questions = [
    "What is Creative Destruction?",
    "How do I validate a startup idea?",
    "What's the difference between un-defined and ill-defined problems?",
]

print("=" * 80)
print("TESTING LARRY - Sample Questions")
print("=" * 80)
print()

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {question}")
    print('='*80)
    print()

    response = larry.chat(question)
    print(response)
    print()

    if i < len(test_questions):
        input("\n[Press Enter for next question...]")

print("\n" + "=" * 80)
print("TESTING COMPLETE!")
print("=" * 80)
print("\nTo chat with Larry interactively, run in YOUR terminal:")
print("  cd /home/jsagi")
print("  source pws-navigator-env/bin/activate")
print("  python3 larry_chatbot.py")
