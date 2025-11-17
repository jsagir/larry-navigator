# 🎯 Larry - Your Personal Uncertainty Navigator

**An AI chatbot that teaches innovation using Lawrence Aronhime's methodology**

---

## 🚀 Quick Start

```bash
./larry
```

That's it! Larry will start chatting with you.

---

## 📚 What Larry Knows

Larry has been trained on **10 core PWS lectures** (N01-N10):

1. **N01**: Introduction to Innovation
2. **N02**: Un-Defined Problems
3. **N03**: Ill-Defined Problems
4. **N04**: Wicked Problems
5. **N05**: Domains and Cross-Domain Innovation
6. **N06**: Innovation Portfolio
7. **N07**: Well-Defined Problems
8. **N08**: Prior Art and Validation
9. **N09**: Advanced Topics
10. **N10**: January Term Projects

**Total Content**: 1,136 chunks from Neo4j knowledge graph

---

## 🎓 How Larry Teaches (The Aronhime Method)

Every response follows this structure:

1. **HOOK** - Provocative question to challenge your thinking
2. **FRAME** - Why this matters and what you'll learn
3. **FRAMEWORK** - Systematic thinking tools
4. **STORY** - Memorable case studies (successes + failures)
5. **APPLICATION** - What you can do now
6. **CHALLENGE** - Follow-up question to deepen understanding

---

## 💬 Example Questions to Ask

### For Students:
- "What is Creative Destruction?"
- "How do I prepare for the exam on innovation frameworks?"
- "What's the difference between un-defined and ill-defined problems?"

### For Entrepreneurs:
- "How do I validate my startup idea?"
- "Is my problem un-defined, ill-defined, or well-defined?"
- "What frameworks help with finding innovation opportunities?"

### For Corporate Teams:
- "How do I build a systematic innovation process?"
- "What is the Three Box Solution?"
- "How do I manage an innovation portfolio?"

### General Questions:
- "Show me examples of wicked problems"
- "What tools work for un-defined problems?"
- "Tell me about Scenario Analysis"

Type `help` in Larry to see more examples!

---

## 🧠 Larry's Intelligence

### Persona Detection
Larry automatically detects if you're a:
- 👨‍🎓 **Student** - Focus on course navigation, concepts, exam prep
- 🚀 **Entrepreneur** - Focus on validation, execution, opportunities
- 🏢 **Corporate Team** - Focus on systematic innovation, portfolios
- 💼 **Consultant** - Focus on frameworks, facilitation, advisory
- 🔬 **Researcher** - Focus on theory, literature, foundations

### Question Classification
Larry understands 8 types of questions:
1. **Definitional** - "What is X?"
2. **How-To** - "How do I X?"
3. **Diagnostic** - "What type is this?"
4. **Comparison** - "X vs Y?"
5. **Application** - "How do I apply X?"
6. **Strategic** - "What's the best approach?"
7. **Navigation** - "Where can I learn X?"
8. **Examples/Cases** - "Show me an example"

---

## 🛠️ Technical Details

### Architecture:
- **Knowledge Base**: Neo4j graph database (1,136 PWS chunks)
- **AI Model**: Google Gemini 2.0 Flash (with File Search)
- **Search**: Gemini File Search store (`larry-pws-navigator`)
- **Interface**: Python CLI with streaming responses

### Files:
```
/home/jsagi/
├── larry                          # Quick launcher script
├── larry_chatbot.py               # Main chatbot code
├── larry_store_info.json          # File Search store config
├── pws_chunks.json                # Extracted PWS content (918KB)
├── build_larry_navigator.py       # Store creation script
├── extract_pws_content.py         # Neo4j extraction script
└── neo4j_explorer.py              # Database explorer
```

### API Key:
Your Google AI API key is configured in `larry_chatbot.py`

---

## 🎨 Customization

### Change Larry's Personality:
Edit the `LARRY_SYSTEM_PROMPT` in `larry_chatbot.py`

### Add More Content:
1. Extract more from Neo4j: `python3 extract_pws_content.py`
2. Re-run upload: `python3 build_larry_navigator.py`

### Adjust Response Length:
Modify `temperature` and `top_p` in `larry_chatbot.py` (line ~160)

---

## 📊 Current Status

✅ **Working:**
- Core PWS lectures (N01-N10) uploaded
- Persona detection active
- Question classification working
- Aronhime teaching style implemented
- CLI interface ready

⚠️ **Known Issues:**
- 17 additional files failed upload (metadata format issue)
- These can be fixed and re-uploaded if needed

---

## 🔮 Future Enhancements

Potential improvements:
1. **Web Interface** - Deploy as web app
2. **Voice Mode** - Add speech-to-text/text-to-speech
3. **Session Memory** - Remember previous conversations
4. **Adaptive Learning** - Adjust based on user level
5. **Framework Visualizations** - Generate diagrams
6. **Multi-Modal** - Add image/video support
7. **Real-Time Examples** - Pull current case studies from web

---

## 🤝 Contributing

Want to improve Larry?
- Add more PWS content to Neo4j
- Enhance the Aronhime response templates
- Build a web UI
- Add more persona types
- Improve question classification

---

## 📝 License & Credits

**Created by**: Claude Code + You
**Based on**: Lawrence Aronhime's Problems Worth Solving (PWS) methodology
**Powered by**: Google Gemini API + Neo4j + Pinecone

---

## 🙏 Special Thanks

To **Professor Lawrence Aronhime** for developing the PWS methodology and teaching innovation in a way that transforms passive learners into active thinkers.

*"The best teachers don't give you the answers. They give you better questions."* - Larry

---

## 💡 Pro Tips

1. **Ask follow-up questions** - Larry loves deep dives!
2. **Challenge Larry** - He's designed to handle tough questions
3. **Be specific** - Mention your context (student, entrepreneur, etc.)
4. **Request examples** - Larry has tons of case studies
5. **Ask "Why?"** - Get to the underlying principles

---

**Ready to navigate uncertainty?** Type `./larry` and start exploring!

🎯 **Larry awaits your first question...**
