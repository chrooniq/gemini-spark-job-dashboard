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

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from generate_job_refresh import run_job_refresh

def run_daily_update():
    print("⚡ Executing Gemini Spark Daily Update Cycle...")
    success = run_job_refresh()
    if success:
        print("✨ Daily job intelligence update completed successfully.")
    else:
        print("❌ Daily update encountered an issue.")
    return success

if __name__ == "__main__":
    run_daily_update()
