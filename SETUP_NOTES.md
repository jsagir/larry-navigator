# 🔧 Setup Notes

## Important: First-Time Setup

Before running the web interface, you need to generate the `larry_store_info.json` file:

### Steps:

1. **Set up Neo4j connection** (if you have the PWS database)
   - Edit `extract_pws_content.py` with your Neo4j credentials
   - Run: `python3 extract_pws_content.py`

2. **Build the File Search store**
   - Run: `python3 build_larry_navigator.py`
   - This creates `larry_store_info.json`

3. **Run the app**
   - CLI: `python3 larry_chatbot.py`
   - Web: `streamlit run app.py`

### Alternative: Skip File Search

If you don't have access to the Neo4j database with PWS content, Larry will still work but without the File Search capability. The chatbot uses Google's Gemini 2.0 Flash model which has general knowledge about innovation and problem-solving.

## Current Status

**Note**: The `larry_store_info.json` file is not included in the repository. You'll need to:
- Generate it yourself using the steps above, OR
- Contact the repository owner for a pre-built version

## File Structure

```
larry-navigator/
├── app.py                        # ✅ Streamlit web interface
├── larry_chatbot.py              # ✅ Core chatbot logic
├── build_larry_navigator.py      # Builds larry_store_info.json
├── extract_pws_content.py        # Extracts from Neo4j
├── larry_store_info.json         # ⚠️ NEEDS TO BE GENERATED
└── ...
```
