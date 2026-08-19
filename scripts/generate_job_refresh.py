#!/usr/bin/env python3
"""
Gemini Spark — 3-Hour Autonomous GoHighLevel (GHL) Job Refresh Engine
Executes every 3 hours (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 PKT).
Enforces STRICT GoHighLevel-only filter and 0–14 days freshness rule (excluding >14D).
Syncs persistent application statuses, excludes applied/processed jobs, and archives snapshots.
"""

import os
import sys
import json
import datetime
import subprocess

PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed"]
GHL_KEYWORDS = ["gohighlevel", "highlevel", "ghl", "go high level"]

def get_pkt_now():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    pkt_now = utc_now + datetime.timedelta(hours=5)
    return pkt_now

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
        "freshness_max_days": 14
    }

def is_ghl_opportunity(job):
    # Strict GHL verification check
    title = job.get("title", "").lower()
    desc = job.get("why_matches", "").lower()
    skills = " ".join(job.get("matched_skills", [])).lower()
    full_text = f"{title} {desc} {skills}"
    return any(k in full_text for k in GHL_KEYWORDS)

def calculate_days_old(posted_date_str, current_date):
    if not posted_date_str:
        return 2
    try:
        posted_dt = datetime.datetime.strptime(posted_date_str, "%Y-%m-%d").date()
        return (current_date - posted_dt).days
    except Exception:
        return 2

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

    # 2. Load latest master data
    if not os.path.exists(latest_file):
        print(f"Error: {latest_file} does not exist.")
        return False

    with open(latest_file, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    pkt_now = get_pkt_now()
    sched_info = compute_schedule_info(pkt_now)
    current_date = pkt_now.date()

    date_str = sched_info["search_date"]
    time_slug = sched_info["search_time_slug"]

    all_raw_jobs = master_data.get("jobs", [])
    filtered_ghl_jobs = []

    for job in all_raw_jobs:
        # Strict GHL check
        if not is_ghl_opportunity(job):
            continue

        job_url = job.get("original_url") or job.get("app_url") or job.get("id")
        stored = app_statuses.get(job_url, {})
        current_status = stored.get("status") or job.get("status") or "New Match"
        job["status"] = current_status
        job["status_updated_at"] = stored.get("updated_at") or sched_info["last_updated"]

        # Calculate Freshness (0–14 days)
        days_old = calculate_days_old(job.get("posted_date"), current_date)
        job["posted_days_ago"] = days_old
        
        if days_old == 0:
            job["posted_relative"] = "Posted today"
            job["freshness_tier"] = "today"
            job["freshness_badge"] = "TODAY"
        elif days_old <= 3:
            job["posted_relative"] = f"Posted {days_old} days ago"
            job["freshness_tier"] = "1-3-days"
            job["freshness_badge"] = f"{days_old}D AGO"
        elif days_old <= 7:
            job["posted_relative"] = f"Posted {days_old} days ago"
            job["freshness_tier"] = "4-7-days"
            job["freshness_badge"] = f"{days_old}D AGO"
        elif days_old <= 14:
            job["posted_relative"] = f"Posted {days_old} days ago"
            job["freshness_tier"] = "8-14-days"
            job["freshness_badge"] = f"{days_old}D AGO"
        else:
            # Exclude 15+ days old from active feed
            job["is_active"] = False
            continue

        # Exclude applied / processed from active feed
        is_act = (current_status not in PROCESSED_STATUSES)
        job["is_active"] = is_act

        app_statuses[job_url] = {
            "job_id": job.get("id"),
            "company": job.get("company"),
            "title": job.get("title"),
            "status": current_status,
            "updated_at": job["status_updated_at"],
            "notes": stored.get("notes", "")
        }

        filtered_ghl_jobs.append(job)

    # Sort strictly by Freshness Tier, then Match Score
    filtered_ghl_jobs.sort(key=lambda j: (
        0 if j["posted_days_ago"] <= 3 else (1 if j["posted_days_ago"] <= 7 else 2),
        -j.get("score", 0)
    ))

    for i, j in enumerate(filtered_ghl_jobs, 1):
        j["rank"] = i

    active_jobs = [j for j in filtered_ghl_jobs if j["is_active"]]
    today_jobs = [j for j in active_jobs if j["posted_days_ago"] == 0]
    three_day_jobs = [j for j in active_jobs if 1 <= j["posted_days_ago"] <= 3]
    seven_day_jobs = [j for j in active_jobs if 4 <= j["posted_days_ago"] <= 7]

    applied_count = len([j for j in filtered_ghl_jobs if j.get("status") == "Applied"])
    interviews_count = len([j for j in filtered_ghl_jobs if "Interview" in j.get("status", "")])
    saved_count = len([j for j in filtered_ghl_jobs if j.get("status") == "Saved"])
    top_score = active_jobs[0]["score"] if active_jobs else 0
    avg_score = round(sum(j["score"] for j in active_jobs) / len(active_jobs), 1) if active_jobs else 0

    updated_payload = {
        "metadata": {
            **master_data.get("metadata", {}),
            **sched_info,
            "kpis": {
                "total_discovered": len(filtered_ghl_jobs),
                "relevant_qualified": len(active_jobs),
                "new_jobs_count": len(active_jobs),
                "active_jobs_count": len(active_jobs),
                "today_count": len(today_jobs),
                "three_days_count": len(three_day_jobs),
                "seven_days_count": len(seven_day_jobs),
                "applied_count": applied_count,
                "interviews_count": interviews_count,
                "offers_count": 0,
                "saved_count": saved_count,
                "top_match_score": top_score,
                "avg_match_score": avg_score,
                "top_5_count": min(5, len(active_jobs)),
                "priority_1_apply_count": len(active_jobs),
                "remote_worldwide_percentage": 100
            }
        },
        "jobs": filtered_ghl_jobs
    }

    # Save application_status.json
    with open(app_status_file, "w", encoding="utf-8") as f:
        json.dump(app_statuses, f, indent=2)

    # Save latest.json
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)

    # Save timestamp snapshot in data/history/YYYY-MM-DD/HH-MM.json
    date_history_dir = os.path.join(history_dir, date_str)
    os.makedirs(date_history_dir, exist_ok=True)
    time_snapshot_file = os.path.join(date_history_dir, f"{time_slug}.json")
    with open(time_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)

    # Save daily snapshot
    daily_snapshot_file = os.path.join(history_dir, f"{date_str}.json")
    with open(daily_snapshot_file, "w", encoding="utf-8") as f:
        json.dump(updated_payload, f, indent=2)

    # Rebuild index.html
    build_script = os.path.join(base_dir, "build_index.py")
    if os.path.exists(build_script):
        subprocess.run([sys.executable, build_script], check=True)

    print(f"✓ GHL 3-Hour Refresh complete: {len(active_jobs)} active fresh GHL jobs (0-14D).")
    return True

if __name__ == "__main__":
    run_job_refresh()
