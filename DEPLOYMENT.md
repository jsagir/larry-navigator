# 🚀 Deploying Larry to Streamlit Cloud

## Quick Deploy Guide

### 1. Prerequisites
- GitHub account
- Streamlit Community Cloud account (free - sign up at https://streamlit.io/cloud)
- Google AI API Key (from https://aistudio.google.com/apikey)

### 2. Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud**: https://share.streamlit.io/

2. **Click "New app"**

3. **Connect your GitHub repository**:
   - Repository: `jsagir/larry-navigator`
   - Branch: `main`
   - Main file path: `larry_app.py`

4. **Add your API key as a secret**:
   - Click "Advanced settings"
   - In the "Secrets" section, add:
   ```toml
   GOOGLE_AI_API_KEY = "your-api-key-here"
   ```

5. **Click "Deploy"**

6. **Wait 2-3 minutes** for deployment to complete

7. **Access Larry** at your public URL: `https://your-app-name.streamlit.app`

---

## 🔐 Security Notes

- ✅ API key is stored as a secret in Streamlit Cloud (encrypted)
- ✅ Never commit `.env` files to GitHub
- ✅ Users can also enter their own API key via the sidebar
- ✅ All sensitive files are in `.gitignore`

---

## 🎨 Streamlit Cloud Features

- **Automatic updates**: Every push to GitHub triggers redeployment
- **Free hosting**: Community Cloud is free for public repos
- **Custom domain**: You can add a custom domain (optional)
- **Analytics**: Built-in usage analytics
- **Resource limits**: 1GB RAM, shared CPU (sufficient for Larry)

---

## 📝 Local Development

To run locally:
```bash
./run_larry.sh
```

Or:
```bash
uvx --from streamlit streamlit run larry_app.py
```

---

## 🔄 Updating the Deployment

1. Make changes to `larry_app.py`
2. Commit and push to GitHub:
   ```bash
   git add larry_app.py
   git commit -m "Update Larry chatbot"
   git push origin main
   ```
3. Streamlit Cloud automatically redeploys (takes 1-2 minutes)

---

## 🆘 Troubleshooting

**Issue**: API key not working
- **Solution**: Check that secrets are configured in Streamlit Cloud settings

**Issue**: File Search not found
- **Solution**: Ensure `larry_store_info.json` is committed to the repo

**Issue**: Deployment fails
- **Solution**: Check `requirements.txt` has all dependencies

---

## 📊 Current Configuration

- **Model**: Gemini 2.5 Flash
- **File Search**: Active (1,136 PWS chunks)
- **Theme**: Mondrian style (Red, Blue, Yellow primary colors)
- **Framework**: Streamlit 1.31+

---

**Need help?** Open an issue on GitHub: https://github.com/jsagir/larry-navigator/issues
