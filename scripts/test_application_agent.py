"""
Gemini Spark — Test Runner for RAG Autonomous Job Application Agent (DRY RUN)
Executes end-to-end form inspection, RAG retrieval, answer generation, and screenshot verification.
"""

import os
import sys
import json
import asyncio

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from agent.browser_agent import AutonomousApplicationAgent

async def run_test():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    latest_file = os.path.join(base_dir, "..", "data", "latest.json")
    
    if not os.path.exists(latest_file):
        print(f"[-] latest.json not found at {latest_file}")
        return

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    if not jobs:
        print("[-] No jobs in latest.json")
        return

    # Select the highest-scoring verified GHL job
    target_job = jobs[0]
    print(f"============================================================")
    print(f"🎯 TARGET JOB FOR APPLICATION DRY RUN:")
    print(f"Title:   {target_job.get('title')}")
    print(f"Company: {target_job.get('company')}")
    print(f"Score:   {target_job.get('score')}%")
    print(f"URL:     {target_job.get('app_url')}")
    print(f"============================================================\n")

    agent = AutonomousApplicationAgent(dry_run=True)
    result = await agent.inspect_and_prepare_application(target_job)

    print("\n" + "=" * 60)
    print("📊 APPLICATION PREPARATION REPORT (DRY RUN):")
    print("=" * 60)
    print(f"Application ID:      {result.get('application_id')}")
    print(f"Status:              {result.get('status')}")
    print(f"Selected Resume:     {result.get('resume_used')}")
    print(f"Selected Portfolio:  {result.get('portfolio_used')}")
    print(f"Overall Confidence:  {result.get('overall_confidence')}%")
    print(f"Audit Screenshot:    {result.get('screenshot_path')}")
    print(f"\nExtracted Fields ({len(result.get('form_fields_extracted', []))} fields):")
    for f in result.get("form_fields_extracted", []):
        print(f"  • [{f.get('classified_category')}] '{f.get('field_identifier')}': {f.get('generated_answer')[:60]}... (Conf: {f.get('confidence')}%)")

if __name__ == "__main__":
    asyncio.run(run_test())
