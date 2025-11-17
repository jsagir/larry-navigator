#!/usr/bin/env python3
"""Monitor upload progress"""
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def check_process_running():
    """Check if upload process is still running"""
    result = subprocess.run(
        ["pgrep", "-f", "upload_full_knowledge.py"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def get_store_stats():
    """Get current store statistics"""
    store_path = Path("/home/jsagi/larry_store_info.json")
    if store_path.exists():
        with open(store_path) as f:
            return json.load(f)
    return {}

def count_temp_files():
    """Count temporary chunk files"""
    return len(list(Path("/tmp").glob("larry_chunk_*.txt")))

def main():
    print("=" * 60)
    print("📊 LARRY UPLOAD PROGRESS MONITOR")
    print("=" * 60)
    print()

    iteration = 0
    while check_process_running():
        temp_count = count_temp_files()
        current_time = datetime.now().strftime("%H:%M:%S")

        print(f"[{current_time}] 🔄 Uploading... (temp files: {temp_count})")

        iteration += 1
        if iteration % 6 == 0:  # Every minute
            stats = get_store_stats()
            print(f"  Store info: {stats.get('total_chunks', 0)} chunks, last updated: {stats.get('last_updated', 'N/A')}")

        time.sleep(10)

    print()
    print("✅ Upload process completed!")
    print()

    # Show final stats
    stats = get_store_stats()
    print("📈 FINAL STATISTICS:")
    print(f"  Total chunks in store: {stats.get('total_chunks', 0):,}")
    print(f"  Last updated: {stats.get('last_updated', 'N/A')}")
    print()

    # Show log if available
    log_path = Path("full_knowledge_upload.log")
    if log_path.exists() and log_path.stat().st_size > 0:
        print("📝 Upload log (last 20 lines):")
        with open(log_path) as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(f"  {line.rstrip()}")

    print("=" * 60)

if __name__ == "__main__":
    main()
