"""
Gemini Spark — Jobicy & Himalayas API Source Adapters (Strict GHL Verified)
"""

import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GeminiSpark/2.0",
    "Accept": "application/json"
}

GHL_REGEX = re.compile(r"\b(gohighlevel|go\s+high\s+level|highlevel|ghl)\b", re.IGNORECASE)

def query_jobicy():
    jobs = []
    tags = ["gohighlevel", "highlevel", "ghl"]
    for tag in tags:
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={tag}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", []):
                    title = item.get("jobTitle", "")
                    desc = item.get("jobDescription", "")
                    if GHL_REGEX.search(title) or GHL_REGEX.search(desc):
                        sal_min = item.get("annualSalaryMin")
                        sal_max = item.get("annualSalaryMax")
                        currency = item.get("salaryCurrency", "USD")
                        sal_str = f"{currency} {sal_min:,.0f} – {sal_max:,.0f}/yr" if sal_min and sal_max else "Competitive Market Rate"
                        jobs.append({
                            "raw_id": str(item.get("id")),
                            "title": title,
                            "company": item.get("companyName", "Tech Employer"),
                            "company_logo": item.get("companyLogo"),
                            "location": item.get("jobGeo") or "Worldwide Remote",
                            "remote_eligibility": "Open Globally",
                            "work_mode": "100% Remote",
                            "salary": sal_str,
                            "employment_type": item.get("jobType", ["Full-Time"])[0] if isinstance(item.get("jobType"), list) else "Full-Time",
                            "experience_req": "3+ years",
                            "description": desc,
                            "posted_date_raw": item.get("pubDate"),
                            "source": "Jobicy",
                            "app_url": item.get("url"),
                            "original_url": item.get("url"),
                            "source_type": "jobicy_api"
                        })
        except Exception as e:
            pass
    return jobs

def query_himalayas():
    jobs = []
    try:
        url = "https://himalayas.app/jobs/api"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                desc = item.get("description", "")
                if GHL_REGEX.search(title) or GHL_REGEX.search(desc):
                    jobs.append({
                        "raw_id": str(item.get("id") or item.get("slug")),
                        "title": title,
                        "company": item.get("companyName", "Himalayas Employer"),
                        "company_logo": item.get("companyLogo"),
                        "location": item.get("location") or "Worldwide Remote",
                        "remote_eligibility": "Open Globally",
                        "work_mode": "100% Remote",
                        "salary": item.get("salary") or "Competitive / Disclosed on Application",
                        "employment_type": "Full-Time Remote",
                        "experience_req": "2–4 years",
                        "description": desc,
                        "posted_date_raw": item.get("pubDate") or item.get("publishedAt"),
                        "source": "Himalayas",
                        "app_url": item.get("applicationUrl") or f"https://himalayas.app/jobs/{item.get('slug', '')}",
                        "original_url": f"https://himalayas.app/jobs/{item.get('slug', '')}",
                        "source_type": "himalayas_api"
                    })
    except Exception as e:
        pass
    return jobs
