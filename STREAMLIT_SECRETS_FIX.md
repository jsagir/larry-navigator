# 🔧 Fix Streamlit Cloud Secrets Error

## Error Message
```
Error parsing secrets file at /mount/src/larry-navigator/.streamlit/secrets.toml
```

## Problem
The secrets.toml file on Streamlit Cloud has a **syntax error**. Common causes:
- Missing quotes around API key values
- Extra spaces or special characters
- Incorrect TOML format

## Solution: Fix Secrets in Streamlit Cloud UI

### Step 1: Go to Streamlit Cloud
1. Open your app on Streamlit Cloud
2. Click "Manage app" (bottom right)
3. Click "Settings" → "Secrets"

### Step 2: Delete Current Content
- Select all text in the Secrets editor
- Delete everything

### Step 3: Paste Correct Format

**Copy and paste this EXACT text:**

```toml
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
```

**That's it!** Just one line for now.

### Step 4: Save
1. Click "Save"
2. Wait for app to reboot (~30 seconds)
3. App should now work!

## Adding Optional Keys (Later)

Once the app is working, you can add optional keys:

```toml
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
TAVILY_API_KEY = "tvly-your-key-here"
```

## Common TOML Syntax Errors

### ❌ Wrong Format
```toml
GOOGLE_AI_API_KEY: AIzaSy...          # Wrong: colon instead of =
GOOGLE_AI_API_KEY = AIzaSy...         # Wrong: missing quotes
GOOGLE_AI_API_KEY = 'AIzaSy...'       # Wrong: single quotes
GOOGLE_AI_API_KEY = "AIzaSy..."extra  # Wrong: text after closing quote
```

### ✅ Correct Format
```toml
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
```

**Rules:**
1. Use `=` not `:`
2. Use double quotes `"` not single quotes `'`
3. No extra text after closing quote
4. One variable per line
5. No comments on same line as variable (put comments on separate lines)

## Verification

After fixing secrets:
1. App should reload automatically
2. You should see the Larry Navigator interface
3. Try asking: "What is Jobs to be Done framework?"
4. Response should stream in real-time

## Still Not Working?

### Check App Logs
1. In Streamlit Cloud, click "Manage app"
2. Look at the logs (bottom section)
3. Look for specific error messages

### Common Issues

**Issue: "GOOGLE_AI_API_KEY not found"**
- Make sure variable name is exactly `GOOGLE_AI_API_KEY`
- Check for typos

**Issue: "Invalid API key"**
- Verify the API key is correct
- Check for extra spaces at beginning or end

**Issue: Import errors in logs**
- These are expected (Neo4j, LangChain are optional)
- As long as "Chat handler loaded successfully" appears, it's working

## Quick Test After Fix

Once secrets are saved:
1. Wait for app to reboot
2. Clear browser cache (Ctrl+Shift+R)
3. Try a simple query: "Hello"
4. Should see Larry's response streaming

## Template for Reference

Keep this template handy for Streamlit Cloud Secrets:

```toml
# Required
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"

# Optional (add later if needed)
TAVILY_API_KEY = "tvly-your-key-here"
```

**Important:**
- Don't include the `# Required` and `# Optional` comments in Streamlit Cloud
- Just the variable lines

## Minimal Working Example

The absolute minimum to get Larry working:

```toml
GOOGLE_AI_API_KEY = "YOUR_GOOGLE_AI_API_KEY_HERE"
```

Copy that single line into Streamlit Cloud Secrets and save. Done!
