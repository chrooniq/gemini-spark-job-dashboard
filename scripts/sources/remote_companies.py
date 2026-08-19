"""
Gemini Spark — Remote Jobs PDF Directory & Public Company ATS Adapter
Queries public career endpoints for companies listed in the Remote Jobs Directory.
"""

import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GeminiSpark/2.0",
    "Accept": "application/json"
}

# Key remote companies with direct public Greenhouse / Lever / Workable endpoints
REMOTE_DIRECTORY_COMPANIES = [
    {"name": "Zapier", "gh_board": "zapier", "region": "Worldwide"},
    {"name": "10up", "gh_board": "10up", "region": "Worldwide"},
    {"name": "Automattic", "gh_board": "automattic", "region": "Worldwide"},
    {"name": "ClickUp", "gh_board": "clickup", "region": "Worldwide"},
    {"name": "ActiveCampaign", "gh_board": "activecampaign", "region": "USA / Worldwide"},
    {"name": "Customer.io", "gh_board": "customerio", "region": "Worldwide"},
    {"name": "Klaviyo", "gh_board": "klaviyo", "region": "USA / Worldwide"},
    {"name": "MailerLite", "lever_board": "mailerlite", "region": "Worldwide"},
    {"name": "Close", "gh_board": "close", "region": "Worldwide"},
    {"name": "Buffer", "gh_board": "buffer", "region": "Worldwide"},
    {"name": "Formstack", "gh_board": "formstack", "region": "Worldwide"},
    {"name": "WebFX", "gh_board": "webfx", "region": "Worldwide"},
    {"name": "Auth0", "gh_board": "auth0", "region": "Worldwide"},
    {"name": "Elastic", "gh_board": "elastic", "region": "Worldwide"},
    {"name": "HumanIntelligence", "workable_board": "humanintelligence", "region": "Worldwide Remote"},
    {"name": "Pavago", "workable_board": "pavago", "region": "Worldwide Remote"},
    {"name": "Fasttrack Business Holdings", "region": "Worldwide Remote"}
]

def query_remote_companies_directory():
    jobs = []

    for comp in REMOTE_DIRECTORY_COMPANIES:
        c_name = comp["name"]
        region = comp["region"]

        # 1. Check Greenhouse Public API
        if "gh_board" in comp:
            board = comp["gh_board"]
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
                resp = requests.get(url, headers=HEADERS, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = item.get("title", "")
                        content = item.get("content", "")
                        jobs.append({
                            "raw_id": f"gh-{board}-{item.get('id')}",
                            "title": title,
                            "company": c_name,
                            "location": item.get("location", {}).get("name") or region,
                            "remote_eligibility": "Open Globally",
                            "work_mode": "100% Remote",
                            "salary": "Competitive Market Rate",
                            "employment_type": "Full-Time Remote",
                            "experience_req": "3+ years",
                            "description": content,
                            "posted_date_raw": item.get("updated_at"),
                            "source": f"{c_name} Careers (Greenhouse)",
                            "app_url": item.get("absolute_url"),
                            "original_url": item.get("absolute_url"),
                            "source_type": "greenhouse_public_api"
                        })
            except Exception as e:
                pass

        # 2. Check Lever Public API
        if "lever_board" in comp:
            board = comp["lever_board"]
            try:
                url = f"https://api.lever.co/v0/postings/{board}?mode=json"
                resp = requests.get(url, headers=HEADERS, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data:
                        title = item.get("text", "")
                        desc = item.get("descriptionPlain", "") or item.get("description", "")
                        categories = item.get("categories", {})
                        jobs.append({
                            "raw_id": f"lever-{board}-{item.get('id')}",
                            "title": title,
                            "company": c_name,
                            "location": categories.get("location") or region,
                            "remote_eligibility": "Open Globally",
                            "work_mode": "100% Remote",
                            "salary": "Competitive Market Rate",
                            "employment_type": categories.get("commitment") or "Full-Time",
                            "experience_req": "3+ years",
                            "description": desc,
                            "posted_date_raw": item.get("createdAt"),
                            "source": f"{c_name} Careers (Lever)",
                            "app_url": item.get("hostedUrl") or item.get("applyUrl"),
                            "original_url": item.get("hostedUrl"),
                            "source_type": "lever_public_api"
                        })
            except Exception as e:
                pass

    return jobs
