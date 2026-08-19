#!/usr/bin/env python3
"""
Gemini Spark — Production Transactional Email Dispatcher
Sends automated 3-hour GoHighLevel job intelligence emails via Resend API.
"""

import os
import sys
import json
import requests
import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_env_var(key):
    val = os.getenv(key)
    if val:
        return val.strip()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        if k.strip() == key:
                            return v.strip()
        except Exception:
            pass
    return None

def send_ghl_email_report():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    email_html_file = os.path.join(base_dir, "email_template.html")
    latest_json_file = os.path.join(base_dir, "data", "latest.json")

    resend_api_key = get_env_var("RESEND_API_KEY")
    recipient_email = get_env_var("NOTIFICATION_EMAIL") or "sohaibmahmood5911@gmail.com"

    if not resend_api_key:
        print("[-] Resend Email: RESEND_API_KEY not configured. Skipping email dispatch.")
        return False

    # Load latest metadata & dataset
    meta = {}
    jobs = []
    if os.path.exists(latest_json_file):
        try:
            with open(latest_json_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
                meta = payload.get("metadata", {})
                jobs = payload.get("jobs", [])
        except Exception as e:
            print(f"[-] Could not read latest.json: {e}")

    last_updated = meta.get("last_updated") or datetime.datetime.now().strftime("%d %b %Y, %I:%M %p PKT")
    new_jobs = [j for j in jobs if j.get("is_new") and j.get("is_active")]
    active_jobs = [j for j in jobs if j.get("is_active")]

    # Read HTML content
    email_html = ""
    if os.path.exists(email_html_file):
        with open(email_html_file, "r", encoding="utf-8") as f:
            email_html = f.read()

    # If zero new jobs, compile concise status email or send regular digest
    if len(new_jobs) == 0:
        subject = f"⚡ Gemini Spark — GHL Scan Status ({len(active_jobs)} Active Roles) | {last_updated}"
    else:
        subject = f"🚀 Gemini Spark — {len(new_jobs)} NEW Fresh GHL Jobs Discovered | {last_updated}"

    headers = {
        "Authorization": f"Bearer {resend_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "Gemini Spark <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "html": email_html
    }

    try:
        print(f"[*] Dispatching GHL job intelligence email to {recipient_email} via Resend...")
        resp = requests.post("https://api.resend.com/emails", headers=headers, json=payload, timeout=12)
        if resp.status_code in [200, 201]:
            resp_data = resp.json()
            email_id = resp_data.get("id")
            print(f"✓ Email successfully delivered to {recipient_email}! (Resend ID: {email_id})")
            return True
        else:
            print(f"[-] Resend API error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[-] Failed to send email via Resend: {e}")
        return False

if __name__ == "__main__":
    send_ghl_email_report()
