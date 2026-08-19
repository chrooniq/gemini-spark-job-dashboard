"""
Gemini Spark — Remotive API Source Adapter
"""

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GeminiSpark/2.0",
    "Accept": "application/json"
}

def query_remotive():
    jobs = []
    queries = ["gohighlevel", "highlevel", "crm", "marketing automation", "funnel"]
    for q in queries:
        try:
            url = f"https://remotive.com/api/remote-jobs?search={q}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    jobs.append({
                        "raw_id": str(item.get("id")),
                        "title": item.get("title", ""),
                        "company": item.get("company_name", "Remote Employer"),
                        "company_logo": item.get("company_logo"),
                        "location": item.get("candidate_required_location") or "Worldwide Remote",
                        "remote_eligibility": "Open Globally",
                        "work_mode": "100% Remote",
                        "salary": item.get("salary") or "Competitive / Disclosed on Application",
                        "employment_type": item.get("job_type", "Full-Time Remote").replace("_", " ").title(),
                        "experience_req": "3+ years",
                        "description": item.get("description", ""),
                        "posted_date_raw": item.get("publication_date"),
                        "source": "Remotive",
                        "app_url": item.get("url"),
                        "original_url": item.get("url"),
                        "source_type": "remotive_api"
                    })
        except Exception as e:
            print(f"[-] Remotive query '{q}' error: {e}")
    return jobs
