#!/usr/bin/env python3
"""Quick upload status check"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

print("📊 LARRY UPLOAD STATUS CHECK")
print("=" * 60)
print()

# Check process
result = subprocess.run(["pgrep", "-f", "upload_full_knowledge.py"], capture_output=True)
if result.returncode == 0:
    print("🔄 Process Status: ✅ RUNNING")
else:
    print("🔄 Process Status: ⏹️  STOPPED")

print()

# Count temp files
temp_count = len(list(Path("/tmp").glob("larry_chunk_*.txt")))
print(f"📁 Temp Files: {temp_count} (actively uploading)")
print()

# Store stats
store_path = Path("/home/jsagi/larry_store_info.json")
if store_path.exists():
    with open(store_path) as f:
        info = json.load(f)
    print("📦 File Search Store:")
    print(f"  Total chunks: {info.get('total_chunks', 0):,}")
    print(f"  Last updated: {info.get('last_updated', 'N/A')}")

print()
print("⏱️ Estimated time: 1-2 hours for 2,988 chunks")
print("  (Uploading ~30-50 chunks/minute with rate limiting)")
print()
print("=" * 60)
