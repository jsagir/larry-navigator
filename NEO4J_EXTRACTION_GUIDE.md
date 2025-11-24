# Neo4j to File Search Extraction Guide

## Overview

This guide explains how to extract content from your Neo4j database and upload it to Google File Search for Larry Navigator.

---

## 📋 Prerequisites

1. **Neo4j Database** with PWS content
2. **Google AI API Key** ([Get one](https://aistudio.google.com/apikey))
3. **Python 3.12+** with dependencies

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd larry-navigator
pip install neo4j google-genai
```

### Step 2: Set Environment Variables

```bash
export NEO4J_URI="neo4j+s://5b8df33f.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password-here"
export GOOGLE_AI_API_KEY="your-google-ai-key-here"
```

Or create a `.env` file:
```bash
NEO4J_URI=neo4j+s://5b8df33f.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
GOOGLE_AI_API_KEY=your-google-ai-key-here
```

###  Step 3: Inspect Your Database (Optional)

```bash
python3 inspect_neo4j.py
```

This will show you:
- What node types exist
- How many of each type
- Sample data
- Database statistics

### Step 4: Run the Extraction

```bash
python3 neo4j_to_filesearch.py
```

Expected output:
```
================================================================================
NEO4J TO FILE SEARCH EXPORTER
================================================================================

Step 1: Extracting content from Neo4j...
────────────────────────────────────────────────────────────────────────────────

1.1: Extracting DocumentChunk nodes...
  ✓ Extracted 2,988 document chunks

1.2: Extracting Framework nodes...
  ✓ Extracted 10 framework chunks

1.3: Extracting CaseStudy nodes...
  ✓ Extracted 15 case study chunks

✓ Total chunks extracted: 3,013

================================================================================
Step 2: Saving chunks to file...
────────────────────────────────────────────────────────────────────────────────

Saving 3,013 chunks to neo4j_chunks.json...
✓ Saved to neo4j_chunks.json

================================================================================
Step 3: Uploading to Google File Search...
────────────────────────────────────────────────────────────────────────────────

Uploading 3,013 chunks to File Search...
Creating new File Search store...
✓ Created store: files/abc123/stores/def456

Uploading chunks...
  ✓ Uploaded batch 1 (50 chunks)
  ✓ Uploaded batch 2 (50 chunks)
  ...
  ✓ Uploaded batch 61 (13 chunks)

✓ Uploaded 61 files to File Search store

✓ Store info saved to larry_store_info.json

================================================================================
EXPORT COMPLETE!
================================================================================

📊 Summary:
  • Total chunks: 3,013
  • Saved to: neo4j_chunks.json
  • File Search store: files/abc123/stores/def456
  • Store info: larry_store_info.json

✓ Larry Navigator is now ready to use this knowledge base!

Next: Run larry_app.py or larry_chatbot.py to test it.
```

---

## 📊 What Gets Extracted

### 1. DocumentChunk Nodes
All content chunks with metadata:
- Content text
- Source file
- Document type
- Chunk position
- Problem types
- Frameworks mentioned
- Tools and methods
- Key concepts
- Personas
- Difficulty level
- Prior art metadata (book, author, year)
- Relationship metadata
- Connected concepts/frameworks/problem types

### 2. Framework Nodes
Innovation frameworks formatted as chunks:
- Name and description
- Difficulty level
- Time required
- Team size
- Problem types addressed
- Personas who use it
- Authors who created it

### 3. CaseStudy Nodes
Real-world examples:
- Title and description
- Industry and companies
- Outcome and success level
- Frameworks demonstrated

---

## 📁 Output Files

### `neo4j_chunks.json`
All extracted chunks in JSON format:
```json
[
  {
    "chunk_id": "chunk_001",
    "content": "...",
    "metadata": {
      "source_file": "N01_Introduction.txt",
      "document_type": "lecture",
      "frameworks": ["Design Thinking"],
      "problem_types": ["ill-defined"],
      ...
    }
  }
]
```

### `larry_store_info.json`
File Search store information:
```json
{
  "store_name": "files/abc123/stores/def456",
  "total_chunks": 3013,
  "total_files": 61,
  "created_at": "2025-01-24T..."
}
```

---

## 🔧 Customization

### Extract Only Specific Node Types

Edit `neo4j_to_filesearch.py` and comment out unwanted extractions:

```python
# all_chunks.extend(doc_chunks)  # Skip document chunks
all_chunks.extend(fw_chunks)     # Keep frameworks
all_chunks.extend(case_chunks)   # Keep case studies
```

### Add Custom Node Types

Add a new extraction method:

```python
def extract_custom_nodes(self) -> List[Dict[str, Any]]:
    query = """
    MATCH (n:YourCustomNode)
    RETURN n.property AS property
    """

    chunks = []
    with self.driver.session() as session:
        results = session.run(query)
        for record in results:
            chunk = {
                "chunk_id": f"custom_{record['property']}",
                "content": record['property'],
                "metadata": {...}
            }
            chunks.append(chunk)
    return chunks
```

Then call it in `run_full_export()`:
```python
custom_chunks = self.extract_custom_nodes()
all_chunks.extend(custom_chunks)
```

---

## 🎯 Neo4j Schema Requirements

For best results, your Neo4j database should have:

### Required Node Types:
- `DocumentChunk` - Main content chunks
- Properties: `chunk_id`, `content`, `source_file`, `document_type`

### Optional Node Types:
- `Framework` - Innovation frameworks
- `CaseStudy` - Real-world examples
- `Concept` - Key concepts
- `ProblemType` - Problem classifications
- `Persona` - User personas
- `Author` - Thought leaders
- `Company` - Organizations in case studies

### Recommended Relationships:
- `(:DocumentChunk)-[:DISCUSSES]->(:Concept)`
- `(:DocumentChunk)-[:REFERENCES]->(:Framework)`
- `(:Framework)-[:ADDRESSES]->(:ProblemType)`
- `(:Persona)-[:USES]->(:Framework)`
- `(:CaseStudy)-[:DEMONSTRATES]->(:Framework)`

---

## ⚠️ Troubleshooting

### "Connection refused" Error
- Check that Neo4j URI is correct
- Verify Neo4j instance is running
- Ensure firewall allows connection

### "Authentication failed" Error
- Double-check username and password
- Verify credentials haven't expired

### "Module not found" Error
```bash
pip install neo4j google-genai
```

### "API key invalid" Error
- Get a new key from https://aistudio.google.com/apikey
- Make sure it's the NEW key (not leaked one)

### File Search Upload Fails
- Check internet connection
- Verify Google AI API key has File Search permissions
- Try smaller batch sizes (reduce `batch_size` in code)

---

## 📈 Performance Notes

- **Extraction Speed:** ~1000 chunks/minute from Neo4j
- **Upload Speed:** ~50 chunks/file, ~2 files/second
- **Total Time:** ~5-10 minutes for 3000 chunks

---

## 🔒 Security Best Practices

1. **Never commit credentials** to git
2. **Use environment variables** or `.env` file
3. **Add `.env` to `.gitignore`**
4. **Rotate API keys** periodically
5. **Use different keys** for dev/production

---

## 🔄 Updating the Knowledge Base

To add new content:

1. Add content to Neo4j
2. Run extraction again:
   ```bash
   python3 neo4j_to_filesearch.py
   ```
3. It will create a NEW File Search store
4. Update `larry_store_info.json` with new store name
5. Restart Larry Navigator

---

## 📞 Support

If you encounter issues:
1. Run `inspect_neo4j.py` to verify database structure
2. Check the error message carefully
3. Verify all environment variables are set
4. Ensure dependencies are installed

---

**Ready to extract?** Run `python3 neo4j_to_filesearch.py`!
