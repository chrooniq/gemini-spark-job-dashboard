#!/usr/bin/env python3
"""
Gemini Spark — Data Builder Utility
Generates and normalizes GoHighLevel candidate dataset fixtures for local testing and CI.
Uses portable relative paths.
"""

import os
import sys
import json
import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir) if "scripts" in script_dir else script_dir

if os.path.join(base_dir, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(base_dir, "scripts"))

from job_discovery import discover_ghl_opportunities, get_pkt_now

def build_data():
    pkt_now = get_pkt_now()
    date_str = pkt_now.strftime("%Y-%m-%d")
    
    data_dir = os.path.join(base_dir, "data")
    history_dir = os.path.join(data_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    jobs = discover_ghl_opportunities()
    active_jobs = [j for j in jobs if j.get("is_active", True)]
    today_jobs = [j for j in active_jobs if j.get("posted_days_ago") == 0]
    three_day_jobs = [j for j in active_jobs if 1 <= j.get("posted_days_ago", 99) <= 3]
    seven_day_jobs = [j for j in active_jobs if 4 <= j.get("posted_days_ago", 99) <= 7]

    payload = {
        "metadata": {
            "search_date": date_str,
            "search_time": pkt_now.strftime("%H:%M PKT"),
            "search_time_slug": pkt_now.strftime("%H-%M"),
            "last_updated": pkt_now.strftime("%d %b %Y, %I:%M %p PKT"),
            "next_update": (pkt_now + datetime.timedelta(hours=3)).strftime("%d %b %Y, %I:%M %p PKT"),
            "next_update_iso": (pkt_now + datetime.timedelta(hours=3)).isoformat(),
            "schedule_interval_hours": 3,
            "schedule_times_pkt": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
            "filter_scope": "GOHIGHLEVEL_ONLY",
            "freshness_max_days": 7,
            "refresh_status": "LIVE",
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
                "total_discovered": len(jobs),
                "new_jobs_count": len(active_jobs),
                "active_jobs_count": len(active_jobs),
                "fresh_jobs_count": len(active_jobs),
                "today_count": len(today_jobs),
                "three_days_count": len(three_day_jobs),
                "seven_days_count": len(seven_day_jobs),
                "applied_count": 0,
                "interviews_count": 0,
                "offers_count": 0,
                "saved_count": 0,
                "top_match_score": active_jobs[0]["score"] if active_jobs else 0,
                "avg_match_score": round(sum(j["score"] for j in active_jobs) / len(active_jobs), 1) if active_jobs else 0,
                "top_5_count": min(5, len(active_jobs)),
                "priority_1_apply_count": len([j for j in active_jobs if "Priority 1" in j.get("priority", "")]),
                "remote_worldwide_percentage": 100
            },
            "reports": {
                "excel_url": "https://drive.google.com/file/d/12mjATUvsDO6KQS20w_1MOAevmG41T0vV/view?usp=drivesdk",
                "drive_folder_url": "https://drive.google.com/drive/folders/16V6BN5Dx6RytoCkpnpMvDvn5GshxEO_p",
                "dashboard_drive_url": "https://drive.google.com/file/d/1SRe5umuG0DnI-mYpshNjV8Rn5REBeDoA/view?usp=drivesdk"
            },
            "available_dates": [date_str]
        },
        "jobs": jobs
    }

    latest_file = os.path.join(data_dir, "latest.json")
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    history_file = os.path.join(history_dir, f"{date_str}.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"✓ latest.json and history/{date_str}.json written successfully.")

if __name__ == "__main__":
    build_data()
