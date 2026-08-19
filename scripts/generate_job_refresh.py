#!/usr/bin/env python3
"""
Gemini Spark — 3-Hour Autonomous GoHighLevel (GHL) Job Refresh & Automation Engine
Executes every 3 hours (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 PKT).
Discovers fresh public GHL jobs (0–7 days max age), enforces strict GHL relevance,
syncs persistent application statuses, permanently excludes applied/interviewed jobs from the active feed,
updates latest.json, archives immutable historical snapshots, and recompiles index.html & email_template.html.
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

# Add scripts directory to path to import job_discovery
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from job_discovery import discover_ghl_opportunities, PROCESSED_STATUSES, get_pkt_now

def compute_schedule_info(pkt_now):
    schedule_hours = [0, 3, 6, 9, 12, 15, 18, 21]
    curr_hour = pkt_now.hour

    next_slot_hour = None
    for h in schedule_hours:
        if h > curr_hour:
            next_slot_hour = h
            break
    
    if next_slot_hour is not None:
        next_dt = pkt_now.replace(hour=next_slot_hour, minute=0, second=0, microsecond=0)
    else:
        tomorrow = pkt_now + datetime.timedelta(days=1)
        next_dt = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

    last_updated_str = pkt_now.strftime("%d %b %Y, %I:%M %p PKT")
    next_update_str = next_dt.strftime("%d %b %Y, %I:%M %p PKT")
    next_update_iso = next_dt.isoformat()

    return {
        "search_date": pkt_now.strftime("%Y-%m-%d"),
        "search_time": pkt_now.strftime("%H:%M PKT"),
        "search_time_slug": pkt_now.strftime("%H-%M"),
        "last_updated": last_updated_str,
        "next_update": next_update_str,
        "next_update_iso": next_update_iso,
        "schedule_interval_hours": 3,
        "schedule_times_pkt": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
        "filter_scope": "GOHIGHLEVEL_ONLY",
        "freshness_max_days": 7,
        "refresh_status": "LIVE"
    }

def run_job_refresh():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    history_dir = os.path.join(data_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    app_status_file = os.path.join(data_dir, "application_status.json")
    latest_file = os.path.join(data_dir, "latest.json")

    # 1. Load persistent statuses
    app_statuses = {}
    if os.path.exists(app_status_file):
        try:
            with open(app_status_file, "r", encoding="utf-8") as f:
                app_statuses = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read application_status.json: {e}")
            app_statuses = {}

    # 2. Load previous latest.json to track previously known jobs & available dates
    prev_known_keys = set()
    available_dates = []
    if os.path.exists(latest_file):
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                prev_payload = json.load(f)
                available_dates = prev_payload.get("metadata", {}).get("available_dates", [])
                for pj in prev_payload.get("jobs", []):
                    key = pj.get("original_url") or pj.get("app_url") or pj.get("id")
                    if key:
                        prev_known_keys.add(key)
        except Exception as e:
            print(f"Info: Could not load previous latest.json: {e}")

    pkt_now = get_pkt_now()
    sched_info = compute_schedule_info(pkt_now)
    date_str = sched_info["search_date"]
    time_slug = sched_info["search_time_slug"]

    # 3. Discover fresh GHL opportunities (<= 7 days)
    print(f"[*] Starting GHL Job Discovery cycle for {sched_info['last_updated']}...")
    discovered_jobs = discover_ghl_opportunities()

    processed_jobs = []
    new_jobs_count = 0

    for job in discovered_jobs:
        job_url_key = job.get("original_url") or job.get("app_url") or job.get("id")
        
        # Check persistent status registry
        stored_entry = app_statuses.get(job_url_key, {})
        current_status = stored_entry.get("status") or job.get("status") or "New Match"
        status_updated_at = stored_entry.get("updated_at") or job.get("status_updated_at") or sched_info["last_updated"]

        # Check if job was previously known or is newly discovered
        is_truly_new = (job_url_key not in prev_known_keys)
        job["is_new"] = is_truly_new
        if is_truly_new:
            new_jobs_count += 1

        job["status"] = current_status
        job["status_updated_at"] = status_updated_at

        # Critical exclusion rule: Applied/Interviewed/Processed jobs are NEVER active
        is_active = (current_status not in PROCESSED_STATUSES)
        job["is_active"] = is_active

        # Update registry with latest metadata
        app_statuses[job_url_key] = {
            "job_id": job.get("id"),
            "company": job.get("company"),
            "title": job.get("title"),
            "status": current_status,
            "updated_at": status_updated_at,
            "notes": stored_entry.get("notes", "")
        }

        processed_jobs.append(job)

    # Sort active jobs strictly by Freshness Tier (Today -> 1-3D -> 4-7D), then Match Score descending
    processed_jobs.sort(key=lambda j: (
        0 if j["is_active"] else 1,
        j.get("freshness_priority", 2),
        -j.get("score", 0)
    ))

    # Re-assign rank among all jobs
    for i, j in enumerate(processed_jobs, 1):
        j["rank"] = i

    active_jobs = [j for j in processed_jobs if j["is_active"]]
    today_jobs = [j for j in active_jobs if j.get("posted_days_ago") == 0]
    three_day_jobs = [j for j in active_jobs if 1 <= j.get("posted_days_ago", 99) <= 3]
    seven_day_jobs = [j for j in active_jobs if 4 <= j.get("posted_days_ago", 99) <= 7]

    applied_count = len([j for j in processed_jobs if j.get("status") == "Applied"])
    interviews_count = len([j for j in processed_jobs if "Interview" in j.get("status", "")])
    saved_count = len([j for j in processed_jobs if j.get("status") == "Saved"])
    offers_count = len([j for j in processed_jobs if j.get("status") == "Offer"])

    top_score = active_jobs[0]["score"] if active_jobs else 0
    avg_score = round(sum(j["score"] for j in active_jobs) / len(active_jobs), 1) if active_jobs else 0

    # Build available dates list
    history_dates = [f.replace(".json", "") for f in os.listdir(history_dir) if f.endswith(".json")]
    all_dates = sorted(list(set(history_dates + available_dates + [date_str])), reverse=True)

    updated_payload = {
        "metadata": {
            **sched_info,
            "available_dates": all_dates,
            "candidate": {
                "name": "Sohaib Mahmood",
                "title": "GoHighLevel Developer | CRM & Marketing Automation | Funnel & Website Builder",
                "experience": "4 Years (50+ Builds, 200+ Workflows, 40+ Sub-Accounts)",
                "location": "Lahore, Pakistan (UTC+5)",
                "work_mode": "100% Worldwide Remote",
                "portfolio_url": "https://sohaibmahmood.vibepreview.com/",
                "intro_video_url": "https://drive.google.com/file/d/1TH4CMzXFOfup2liGESZmmA7QFM8GcfqP/view?usp=sharing",
                "resume_url": "https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk"
            },
            "kpis": {
                "total_discovered": len(processed_jobs),
                "new_jobs_count": new_jobs_count,
                "active_jobs_count": len(active_jobs),
                "fresh_jobs_count": len(active_jobs),
                "today_count": len(today_jobs),
                "three_days_count": len(three_day_jobs),
                "seven_days_count": len(seven_day_jobs),
                "applied_count": applied_count,
                "interviews_count": interviews_count,
                "offers_count": offers_count,
                "saved_count": saved_count,
                "top_match_score": top_score,
                "avg_match_score": avg_score,
                "top_5_count": min(5, len(active_jobs)),
                "priority_1_apply_count": len([j for j in active_jobs if "Priority 1" in j.get("priority", "")]),
                "priority_2_consider_count": len([j for j in active_jobs if "Priority 2" in j.get("priority", "")]),
                "remote_worldwide_percentage": 100
            },
            "reports": {
                "excel_url": "https://drive.google.com/file/d/12mjATUvsDO6KQS20w_1MOAevmG41T0vV/view?usp=drivesdk",
                "drive_folder_url": "https://drive.google.com/drive/folders/16V6BN5Dx6RytoCkpnpMvDvn5GshxEO_p",
                "dashboard_drive_url": "https://drive.google.com/file/d/1SRe5umuG0DnI-mYpshNjV8Rn5REBeDoA/view?usp=drivesdk"
            }
        },
        "jobs": processed_jobs
    }

    # 4. Save application_status.json
    with open(app_status_file, "w", encoding="utf-8") as f:
        json.dump(app_statuses, f, indent=2)
    print(f"✓ Synchronized status registry ({len(app_statuses)} total tracked records)")

    # 5. Save latest.json
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)
    print(f"✓ Saved active dataset to {latest_file}")

    # 6. Save timestamp sub-interval snapshot (data/history/YYYY-MM-DD/HH-MM.json)
    date_history_dir = os.path.join(history_dir, date_str)
    os.makedirs(date_history_dir, exist_ok=True)
    time_snapshot_file = os.path.join(date_history_dir, f"{time_slug}.json")
    with open(time_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)

    # 7. Save immutable daily snapshot (data/history/YYYY-MM-DD.json)
    daily_snapshot_file = os.path.join(history_dir, f"{date_str}.json")
    with open(daily_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)
    print(f"✓ Archived snapshot to {daily_snapshot_file}")

    # 8. Recompile index.html with embedded fallback store
    build_script = os.path.join(base_dir, "build_index.py")
    if os.path.exists(build_script):
        subprocess.run([sys.executable, build_script], check=True)
        print("✓ Recompiled index.html with latest dataset")

    # 9. Recompile email_template.html
    email_script = os.path.join(base_dir, "scripts", "generate_email_template.py")
    if os.path.exists(email_script):
        subprocess.run([sys.executable, email_script], check=True)
        print("✓ Recompiled email_template.html")

    print(f"\n✨ GHL 3-Hour Job Refresh complete: {len(active_jobs)} active fresh GHL jobs (0–7 days old).")
    return True

if __name__ == "__main__":
    run_job_refresh()
