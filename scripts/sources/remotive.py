"""
Gemini Spark — Remotive API Source Adapter (Strict GHL Verified)
"""

import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GeminiSpark/2.0",
    "Accept": "application/json"
}

GHL_REGEX = re.compile(r"\b(gohighlevel|go\s+high\s+level|highlevel|ghl)\b", re.IGNORECASE)

def query_remotive():
    jobs = []
    queries = ["gohighlevel", "highlevel", "ghl"]
    for q in queries:
        try:
            url = f"https://remotive.com/api/remote-jobs?search={q}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    title = item.get("title", "")
                    desc = item.get("description", "")
                    # STRICT check: Must explicitly mention GHL in title or description
                    if GHL_REGEX.search(title) or GHL_REGEX.search(desc):
                        jobs.append({
                            "raw_id": str(item.get("id")),
                            "title": title,
                            "company": item.get("company_name", "Remote Employer"),
                            "company_logo": item.get("company_logo"),
                            "location": item.get("candidate_required_location") or "Worldwide Remote",
                            "remote_eligibility": "Open Globally",
                            "work_mode": "100% Remote",
                            "salary": item.get("salary") or "Competitive / Disclosed on Application",
                            "employment_type": item.get("job_type", "Full-Time Remote").replace("_", " ").title(),
                            "experience_req": "3+ years",
                            "description": desc,
                            "posted_date_raw": item.get("publication_date"),
                            "source": "Remotive",
                            "app_url": item.get("url"),
                            "original_url": item.get("url"),
                            "source_type": "remotive_api"
                        })
        except Exception as e:
            pass
    return jobs
