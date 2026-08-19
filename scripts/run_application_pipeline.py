#!/usr/bin/env python3
"""
Gemini Spark — Phase 6 Controlled Application Pipeline CLI
Usage:
  python scripts/run_application_pipeline.py --prepare     # Populate review queue for high-match jobs
  python scripts/run_application_pipeline.py --list        # View applications in review queue
  python scripts/run_application_pipeline.py --dry-run     # Test form extraction and answers (no submit)
  python scripts/run_application_pipeline.py --approve ID  # Grant human approval (READY_FOR_REVIEW ➔ APPROVED_TO_APPLY)
  python scripts/run_application_pipeline.py --apply ID    # Execute controlled live submission for approved job
"""

import os
import sys
import json
import argparse
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

from agent.approval_manager import ApplicationApprovalManager, MIN_MATCH_SCORE
from agent.browser_agent import AutonomousApplicationAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_JOBS_FILE = os.path.join(BASE_DIR, "..", "data", "latest.json")

def load_latest_jobs():
    if os.path.exists(LATEST_JOBS_FILE):
        with open(LATEST_JOBS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("jobs", [])
    return []

def cmd_prepare():
    jobs = load_latest_jobs()
    mgr = ApplicationApprovalManager()
    
    print(f"\n[*] Evaluating {len(jobs)} verified GHL jobs for application readiness (Threshold >= {MIN_MATCH_SCORE}%)...")
    prepared_count = 0

    for j in jobs:
        score = float(j.get("score", 0))
        if score >= MIN_MATCH_SCORE:
            res, msg = mgr.prepare_job_for_review(j)
            if res:
                prepared_count += 1
                print(f"  ✓ [{res.get('match_score')}%] Queued for Review: '{res.get('job_title')}' @ {res.get('company')} (ID: {res.get('job_id')})")
            else:
                print(f"  [-] Skipped: '{j.get('title')}' @ {j.get('company')} — {msg}")

    print(f"\n✨ Successfully prepared {prepared_count} high-match applications in review queue.")

def cmd_list():
    mgr = ApplicationApprovalManager()
    queue = mgr.load_review_queue()
    submitted_today = mgr.get_applications_submitted_today()

    print("\n" + "=" * 80)
    print(f"📋 GEMINI SPARK APPLICATION REVIEW QUEUE ({len(queue)} items | {submitted_today}/10 applied today)")
    print("=" * 80)

    if not queue:
        print("Review queue is empty. Run --prepare to populate high-match opportunities.")
        return

    for idx, item in enumerate(queue, 1):
        status_icon = "🟢" if item.get("status") == "APPROVED_TO_APPLY" else ("✓" if item.get("status") == "APPLIED" else "⏳")
        print(f"\n{idx}. [{item.get('status')}] {status_icon} ID: {item.get('job_id')}")
        print(f"   Role:      {item.get('job_title')} @ {item.get('company')}")
        print(f"   Score:     {item.get('match_score')}% | Confidence: {item.get('confidence')}%")
        print(f"   Resume:    {item.get('selected_resume')}")
        print(f"   Portfolio: {item.get('selected_portfolio')}")
        print(f"   URL:       {item.get('application_url')}")

def cmd_approve(job_id, notes):
    mgr = ApplicationApprovalManager()
    success, msg = mgr.approve_application(job_id, notes)
    if success:
        print(f"\n✓ {msg}")
        print("Now you may execute: python scripts/run_application_pipeline.py --apply " + job_id)
    else:
        print(f"\n[-] {msg}")

async def cmd_dry_run(target_id=None):
    jobs = load_latest_jobs()
    if not jobs:
        print("[-] No jobs found in data/latest.json")
        return

    target = next((j for j in jobs if j.get("id") == target_id), jobs[0] if not target_id else None)
    if not target:
        print(f"[-] Job with ID {target_id} not found.")
        return

    agent = AutonomousApplicationAgent(dry_run=True)
    res = await agent.inspect_and_prepare_application(target, force_live=False)

    print("\n" + "=" * 60)
    print("📊 DRY RUN APPLICATION REPORT:")
    print("=" * 60)
    print(f"Status:       {res.get('status')}")
    print(f"Job:          {res.get('job_title')} @ {res.get('company')}")
    print(f"Fields Found: {len(res.get('form_fields_extracted', []))}")
    print(f"Screenshot:   {res.get('screenshot_path')}")

async def cmd_apply(job_id):
    jobs = load_latest_jobs()
    target = next((j for j in jobs if j.get("id") == job_id), None)
    if not target:
        print(f"[-] Job with ID {job_id} not found in latest.json.")
        return

    mgr = ApplicationApprovalManager()
    queue = mgr.load_review_queue()
    item = next((q for q in queue if q.get("job_id") == job_id), None)

    if not item or item.get("status") != "APPROVED_TO_APPLY":
        print(f"[-] Safety Gate: Job '{job_id}' is not APPROVED_TO_APPLY (Current Status: {item.get('status') if item else 'Not in queue'}).")
        print(f"Run: python scripts/run_application_pipeline.py --approve {job_id}")
        return

    print(f"\n⚠️ EXECUTING CONTROLLED LIVE APPLICATION for '{target.get('title')}' @ {target.get('company')}...")
    agent = AutonomousApplicationAgent(dry_run=False)
    res = await agent.inspect_and_prepare_application(target, force_live=True)

    print("\n" + "=" * 60)
    print("📊 LIVE SUBMISSION RESULT:")
    print("=" * 60)
    print(f"Status:       {res.get('status')}")
    print(f"Confirmation: {res.get('confirmation', 'N/A')}")
    print(f"Audit Image:  {res.get('screenshot_path')}")

def main():
    parser = argparse.ArgumentParser(description="Gemini Spark Autonomous Application Controller")
    parser.add_argument("--prepare", action="store_true", help="Prepare review queue for high-match jobs")
    parser.add_argument("--list", action="store_true", help="List review queue")
    parser.add_argument("--dry-run", nargs="?", const="default", help="Execute dry-run inspection on a job")
    parser.add_argument("--approve", metavar="JOB_ID", help="Approve job for submission")
    parser.add_argument("--notes", default="Approved by user", help="Optional approval notes")
    parser.add_argument("--apply", metavar="JOB_ID", help="Execute real application submission for approved job")

    args = parser.parse_args()

    if args.prepare:
        cmd_prepare()
    elif args.list:
        cmd_list()
    elif args.approve:
        cmd_approve(args.approve, args.notes)
    elif args.dry_run:
        target_id = None if args.dry_run == "default" else args.dry_run
        asyncio.run(cmd_dry_run(target_id))
    elif args.apply:
        asyncio.run(cmd_apply(args.apply))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
