#!/usr/bin/env python3
"""
Gemini Spark — 3-Hour Autonomous Job Refresh & Application Tracking Engine
Executes every 3 hours (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 PKT).
Normalizes jobs, checks persistent application statuses, detects new opportunities,
filters out processed/applied jobs from active feeds, updates latest.json and historical snapshots.
"""

import os
import sys
import json
import datetime
import subprocess

PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed"]

def get_pkt_now():
    # Pakistan Standard Time is UTC + 5 hours
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    pkt_now = utc_now + datetime.timedelta(hours=5)
    return pkt_now

def compute_schedule_info(pkt_now):
    # Scheduled 3-hour slots in PKT: 0, 3, 6, 9, 12, 15, 18, 21
    schedule_hours = [0, 3, 6, 9, 12, 15, 18, 21]
    curr_hour = pkt_now.hour

    # Find the next slot
    next_slot_hour = None
    for h in schedule_hours:
        if h > curr_hour:
            next_slot_hour = h
            break
    
    if next_slot_hour is not None:
        next_dt = pkt_now.replace(hour=next_slot_hour, minute=0, second=0, microsecond=0)
    else:
        # Rolls over to 00:00 tomorrow
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
        "schedule_times_pkt": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    }

def run_job_refresh():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    history_dir = os.path.join(data_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    app_status_file = os.path.join(data_dir, "application_status.json")
    latest_file = os.path.join(data_dir, "latest.json")

    # 1. Load persistent application status
    app_statuses = {}
    if os.path.exists(app_status_file):
        try:
            with open(app_status_file, "r", encoding="utf-8") as f:
                app_statuses = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read application_status.json: {e}")
            app_statuses = {}

    # 2. Load latest dataset
    if not os.path.exists(latest_file):
        print(f"Error: {latest_file} does not exist.")
        return False

    with open(latest_file, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    pkt_now = get_pkt_now()
    sched_info = compute_schedule_info(pkt_now)

    date_str = sched_info["search_date"]
    time_slug = sched_info["search_time_slug"]

    # 3. Process jobs
    all_raw_jobs = master_data.get("jobs", [])
    processed_jobs = []
    active_jobs = []

    for job in all_raw_jobs:
        job_url = job.get("original_url") or job.get("app_url") or job.get("id")
        
        # Check persistent status
        stored = app_statuses.get(job_url, {})
        current_status = stored.get("status") or job.get("status") or "New Match"
        job["status"] = current_status
        job["status_updated_at"] = stored.get("updated_at") or sched_info["last_updated"]

        # Tag newness
        if "is_new" not in job:
            job["is_new"] = True

        # Sync back to application_status store
        app_statuses[job_url] = {
            "job_id": job.get("id"),
            "company": job.get("company"),
            "title": job.get("title"),
            "status": current_status,
            "updated_at": job["status_updated_at"],
            "notes": stored.get("notes", "")
        }

        # Filter Applied/Processed from active feed
        if current_status in PROCESSED_STATUSES:
            job["is_active"] = False
            processed_jobs.append(job)
        else:
            job["is_active"] = True
            active_jobs.append(job)

    # Sort active jobs by score descending
    active_jobs.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Re-rank active jobs
    for i, j in enumerate(active_jobs, 1):
        j["rank"] = i

    top5_active = active_jobs[:5]
    top25_active = active_jobs[:25]

    # 4. Compute KPIs
    new_jobs_count = len([j for j in active_jobs if j.get("is_new", False)])
    active_jobs_count = len(active_jobs)
    applied_count = len([j for j in all_raw_jobs if j.get("status") == "Applied"])
    interviews_count = len([j for j in all_raw_jobs if "Interview" in j.get("status", "")])
    offers_count = len([j for j in all_raw_jobs if j.get("status") == "Offer"])
    saved_count = len([j for j in active_jobs if j.get("status") == "Saved"])

    top_score = active_jobs[0]["score"] if active_jobs else 0
    avg_score = round(sum(j["score"] for j in active_jobs) / len(active_jobs), 1) if active_jobs else 0
    prio1_count = len([j for j in active_jobs if "prio-apply" in j.get("priority_class", "") or "Priority 1" in j.get("priority", "")])

    # 5. Build updated latest payload
    updated_payload = {
        "metadata": {
            **master_data.get("metadata", {}),
            **sched_info,
            "kpis": {
                "total_discovered": len(all_raw_jobs),
                "relevant_qualified": len(active_jobs),
                "new_jobs_count": new_jobs_count,
                "active_jobs_count": active_jobs_count,
                "applied_count": applied_count,
                "interviews_count": interviews_count,
                "offers_count": offers_count,
                "saved_count": saved_count,
                "top_match_score": top_score,
                "avg_match_score": avg_score,
                "top_5_count": len(top5_active),
                "priority_1_apply_count": prio1_count,
                "remote_worldwide_percentage": 100
            }
        },
        "jobs": all_raw_jobs,
        "active_jobs": active_jobs,
        "top5": top5_active,
        "top25": top25_active,
        "processed_jobs": processed_jobs,
        "market_insights": master_data.get("market_insights", {})
    }

    # 6. Save persistent application_status.json
    with open(app_status_file, "w", encoding="utf-8") as f:
        json.dump(app_statuses, f, indent=2)
    print(f"✓ Synchronized {len(app_statuses)} application statuses to {app_status_file}")

    # 7. Save latest.json
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)
    print(f"✓ Updated {latest_file} (Active: {len(active_jobs)}, Processed/Applied: {len(processed_jobs)})")

    # 8. Save timestamped execution snapshot in data/history/YYYY-MM-DD/HH-MM.json
    date_history_dir = os.path.join(history_dir, date_str)
    os.makedirs(date_history_dir, exist_ok=True)
    time_snapshot_file = os.path.join(date_history_dir, f"{time_slug}.json")
    with open(time_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)
    print(f"✓ Saved 3-hour execution snapshot: {time_snapshot_file}")

    # 9. Also maintain daily master snapshot data/history/YYYY-MM-DD.json
    daily_snapshot_file = os.path.join(history_dir, f"{date_str}.json")
    with open(daily_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)
    print(f"✓ Updated daily snapshot: {daily_snapshot_file}")

    # 10. Rebuild index.html
    build_script = os.path.join(base_dir, "build_index.py")
    if os.path.exists(build_script):
        subprocess.run([sys.executable, build_script], check=True)
        print("✓ Rebuilt index.html with latest fallback data")

    print(f"\n✨ 3-Hour Job Refresh for {sched_info['last_updated']} completed successfully!")
    return True

if __name__ == "__main__":
    run_job_refresh()
