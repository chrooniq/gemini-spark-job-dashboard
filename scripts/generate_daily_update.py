#!/usr/bin/env python3
"""
Gemini Spark — Daily Autonomous Job Intelligence Update Engine
Executes complete data normalization, report creation, JSON updates, and email rendering.
"""

import os
import sys
import json
import datetime
import subprocess

def run_daily_update(date_str=None, scored_jobs_data=None):
    if not date_str:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    history_dir = os.path.join(data_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    latest_file = os.path.join(data_dir, "latest.json")
    history_file = os.path.join(history_dir, f"{date_str}.json")

    # Load existing or new dataset
    if scored_jobs_data:
        current_data = scored_jobs_data
    elif os.path.exists(latest_file):
        with open(latest_file, "r", encoding="utf-8") as f:
            current_data = json.load(f)
    else:
        print("Error: No data available to update.")
        return False

    # Update metadata dates
    current_data["metadata"]["search_date"] = date_str
    
    # Update available_dates history list
    existing_history = [f.replace(".json", "") for f in os.listdir(history_dir) if f.endswith(".json")]
    all_dates = sorted(list(set(existing_history + [date_str])), reverse=True)
    current_data["metadata"]["available_dates"] = all_dates

    # 1. Write historical JSON
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2)
    print(f"✓ Saved historical snapshot to {history_file}")

    # 2. Write latest.json
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2)
    print(f"✓ Updated {latest_file}")

    # 3. Rebuild index.html with new embedded fallback
    build_script = os.path.join(base_dir, "build_index.py")
    if os.path.exists(build_script):
        subprocess.run([sys.executable, build_script], check=True)
        print("✓ Rebuilt index.html with latest fallback data")

    # 4. Generate redesigned email template
    email_script = os.path.join(base_dir, "scripts", "generate_email_template.py")
    if os.path.exists(email_script):
        subprocess.run([sys.executable, email_script], check=True)
        print("✓ Generated updated email_template.html")

    # 5. Git commit if repository is initialized
    try:
        subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
        commit_res = subprocess.run(
            ["git", "commit", "-m", f"Auto: Update daily job intelligence dataset for {date_str}"],
            cwd=base_dir,
            capture_output=True,
            text=True
        )
        print(f"✓ Git commit status: {commit_res.stdout.strip() or 'Working tree clean'}")
    except Exception as e:
        print(f"ℹ Git operation note: {e}")

    print(f"\n✨ Daily update for {date_str} completed successfully!")
    return True

if __name__ == "__main__":
    run_daily_update()
