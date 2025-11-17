#!/bin/bash
# Larry Navigator - Streamlit Launcher

echo "🎯 Starting Larry - Your Personal Uncertainty Navigator"
echo "=================================================="
echo ""
echo "Mondrian-style web interface starting..."
echo ""
echo "Access Larry at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

cd /home/jsagi
uvx --from streamlit streamlit run larry_app.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false \
    --theme.base=light \
    --theme.primaryColor="#DE1B1B" \
    --theme.backgroundColor="#FFFFFF" \
    --theme.secondaryBackgroundColor="#F5F5F5" \
    --theme.textColor="#000000"
