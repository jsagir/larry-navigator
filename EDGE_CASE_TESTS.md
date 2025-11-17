# 🧪 Larry Navigator - Edge Case Test Questions

Test these questions to ensure Larry handles all scenarios properly.

## 📊 Categories

### 1. ✅ Normal Cases (Should work perfectly)

**Definitional Questions:**
- "What is Creative Destruction?"
- "Explain the Three Box Solution"
- "Define wicked problems"
- "What does Jobs-to-be-Done mean?"

**How-To Questions:**
- "How do I validate my startup idea?"
- "How can I identify un-defined problems?"
- "Steps to apply the Mom Test"
- "Process for scenario analysis"

**Comparison Questions:**
- "What's the difference between ill-defined and un-defined problems?"
- "Compare TRIZ vs lateral thinking"
- "Ill-defined vs wicked problems"
- "Extensive vs intensive searching"

**Navigation Questions:**
- "Where can I learn about wicked problems?"
- "What lecture covers the Three Box Solution?"
- "Where is Creative Destruction explained?"

---

### 2. 🔀 Edge Cases (Testing robustness)

#### A. Vague/Unclear Questions
- "Help"
- "Innovation"
- "Problems"
- "Tell me"
- "What?"

**Expected:** Larry should ask clarifying questions using Aronhime method

#### B. Multiple Questions at Once
- "What is Creative Destruction and how do I apply it and also what's the Three Box Solution?"
- "Explain TRIZ, Mom Test, and scenario analysis"
- "How do I validate ideas? What frameworks exist? Where do I start?"

**Expected:** Larry should address them systematically, one at a time

#### C. Off-Topic Questions
- "What's the weather today?"
- "Who won the Super Bowl?"
- "Best pizza recipe?"
- "Tell me about Taylor Swift"

**Expected:** Gently redirect to innovation/problem-solving while being helpful

#### D. Contradictory Questions
- "You said X earlier, but now you're saying Y. Which is correct?"
- "Isn't that the opposite of what you just told me?"

**Expected:** Point out contradiction constructively, explore the tension

#### E. Meta Questions (About Larry)
- "Who are you?"
- "What can you do?"
- "How do you work?"
- "Are you a real person?"

**Expected:** Brief explanation, then pivot to teaching

#### F. Greetings/Social
- "Hello!"
- "Hey there!"
- "Good morning"
- "How are you?"

**Expected:** 2-3 sentence friendly response, invite question

#### G. Requests for Certainty in Uncertain Domains
- "What's the BEST innovation framework?"
- "Which problem type is ALWAYS easiest?"
- "Give me the ONE right answer"

**Expected:** Embrace uncertainty - it's Larry's specialty!

#### H. Domain-Specific Without Context
- "Analyze my business idea" (without providing the idea)
- "Is this a good problem?" (without describing it)
- "Help me innovate" (too vague)

**Expected:** Ask for specifics using Beautiful Questions approach

#### I. Contradictions with General Knowledge
- "Isn't Blockbuster still in business?"
- "Netflix was always streaming-only, right?"
- (Testing if Larry knows real case studies)

**Expected:** Correct misconceptions gently with facts

#### J. Extremely Long Questions
- (A 500-word question covering multiple topics)

**Expected:** Break down, address key points, ask for focus

#### K. Testing Memory
- "What did I ask you 3 messages ago?"
- "Remember what I said about my startup?"
- "Based on our earlier conversation..."

**Expected:** Should reference conversation history (if feature enabled)

#### L. Persona Edge Cases
- Student asking corporate-level questions
- Entrepreneur asking theoretical research questions
- (Mismatched persona/question combinations)

**Expected:** Adapt fluidly, serve the question while respecting persona

---

### 3. 🎯 Knowledge Base Tests (If File Search enabled)

#### A. Specific Lecture Content
- "What does N02 cover?"
- "Summary of lecture 4"
- "What's in the January Term module (N10)?"

**Expected:** Accurate lecture content from PWS knowledge base

#### B. Framework Deep Dives
- "Give me a detailed explanation of TRIZ"
- "How does the Mom Test work step-by-step?"
- "Explain Trending to Absurd with examples"

**Expected:** Retrieved from knowledge base with citations

#### C. Case Studies
- "Tell me about the Blockbuster/Netflix case"
- "GE and the Three Box Solution"
- "Examples of successful wicked problem solutions"

**Expected:** Specific cases from PWS materials

#### D. Cross-Lecture Connections
- "How do un-defined problems relate to the innovation portfolio?"
- "Where does Jobs-to-be-Done fit in the problem typology?"

**Expected:** Synthesize across multiple lectures

#### E. Tools and Techniques
- "What is Red Teaming?"
- "How do I use Beautiful Questions?"
- "Explain Nested Hierarchies"

**Expected:** Specific PWS tools with application guidance

---

### 4. 🚀 Stress Tests

#### A. Rapid-Fire Questions
Ask 10 questions in a row quickly without waiting for full responses

**Expected:** Handle gracefully, maintain quality

#### B. Topic Switching
- Ask about TRIZ
- Switch to Creative Destruction
- Switch to startup validation
- Back to TRIZ

**Expected:** Adapt smoothly, maintain context

#### C. Challenging Larry's Knowledge
- "I don't think that's right"
- "My professor said differently"
- "That framework doesn't work"

**Expected:** Engage intellectually, explore disagreement

#### D. Emotional/Personal Questions
- "I'm scared my startup will fail"
- "I feel overwhelmed by uncertainty"
- "Everyone says my idea is stupid"

**Expected:** Empathize while teaching resilience through PWS frameworks

---

### 5. 🐛 Known Limitations

#### What Larry CANNOT Do (Yet):
- Generate images/diagrams
- Access real-time web data
- Remember across sessions (unless implemented)
- Provide specific financial/legal advice
- Access proprietary company data

#### Test These:
- "Draw me a diagram of the Three Box Solution"
- "What's the latest news on OpenAI?"
- "Remember this for next time I log in"
- "Should I invest $100k in this idea?"

**Expected:** Politely explain limitations, offer alternatives

---

## 📈 Success Criteria

For each test, Larry should:

1. ✅ **Maintain Aronhime style** - HOOK → FRAME → FRAMEWORK → STORY → APPLICATION → CHALLENGE
2. ✅ **Adapt to persona** - Recognize and serve student/entrepreneur/corporate/etc.
3. ✅ **Classify correctly** - Identify question type
4. ✅ **Handle gracefully** - No errors, crashes, or rude responses
5. ✅ **Teach, don't tell** - Questions before answers
6. ✅ **Use knowledge base** - Cite sources when File Search enabled
7. ✅ **Maintain context** - Reference earlier conversation when relevant

---

## 🎯 Priority Testing Order

1. **First:** Normal cases (ensure core functionality works)
2. **Second:** Vague/unclear (most common edge case)
3. **Third:** Knowledge base tests (verify retrieval)
4. **Fourth:** Other edge cases
5. **Last:** Stress tests

---

## 📝 How to Test

```bash
# Run the enhanced version
python3 larry_chatbot_enhanced.py

# Or with knowledge retrieval
python3 larry_with_knowledge.py

# Copy/paste questions from above
# Document:
# - Larry's response
# - Whether it met success criteria
# - Any issues or improvements needed
```

---

## 🔧 Debugging

If Larry fails a test:

1. **Check the persona detection** - Is it classifying correctly?
2. **Check question type** - Is it being categorized properly?
3. **Check edge case detection** - Did it identify the edge case?
4. **Check knowledge retrieval** - Is File Search working?
5. **Check response structure** - Does it follow Aronhime pattern?

---

## 💡 Improvement Ideas

Based on edge case testing:

- [ ] Add spell-check for common misspellings
- [ ] Implement session persistence (save/load conversations)
- [ ] Add diagram generation (ASCII art or mermaid syntax)
- [ ] Create a "challenge mode" for advanced users
- [ ] Implement voice interface
- [ ] Add multilingual support
- [ ] Create mobile-optimized interface

---

**Ready to test?** Start with the normal cases, then progressively test edge cases. Document everything! 🚀
