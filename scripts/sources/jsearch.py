"""
Gemini Spark — RapidAPI JSearch Source Adapter
Searches live postings across LinkedIn, Indeed, Glassdoor, ZipRecruiter, and ATS portals.
"""

import os
import requests
from urllib.parse import quote_plus

def get_env_var(key):
    val = os.getenv(key)
    if val:
        return val.strip()
    # Check .env in parent directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def query_jsearch():
    """Queries JSearch API for fresh GoHighLevel opportunities."""
    rapidapi_key = get_env_var("RAPIDAPI_KEY")
    if not rapidapi_key:
        print("[-] RapidAPI JSearch: No RAPIDAPI_KEY configured. Skipping.")
        return []

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    search_queries = [
        "GoHighLevel",
        "Go High Level",
        "GHL Developer",
        "GHL Automation",
        "GHL Funnel",
        "GoHighLevel CRM",
        "HighLevel CRM Automation"
    ]

    discovered_jobs = []
    seen_ids = set()

    for q in search_queries:
        try:
            url = f"https://jsearch.p.rapidapi.com/search?query={quote_plus(q)}&page=1&num_pages=1&date_posted=all"
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                print(f"[+] JSearch '{q}': Found {len(results)} raw postings")

                for item in results:
                    job_id = item.get("job_id")
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = item.get("job_title", "")
                    desc = item.get("job_description", "")
                    company = item.get("employer_name", "Remote Company")
                    company_logo = item.get("employer_logo")
                    company_website = item.get("employer_website")

                    # Location & Remote
                    is_remote = item.get("job_is_remote", True)
                    city = item.get("job_city") or ""
                    state = item.get("job_state") or ""
                    country = item.get("job_country") or ""
                    loc_parts = [p for p in [city, state, country] if p]
                    loc_str = ", ".join(loc_parts) if loc_parts else "Worldwide Remote"
                    if is_remote and "remote" not in loc_str.lower():
                        loc_str = f"{loc_str} (Remote)" if loc_str != "Worldwide Remote" else "Worldwide Remote"

                    # Salary
                    min_sal = item.get("job_min_salary")
                    max_sal = item.get("job_max_salary")
                    currency = item.get("job_salary_currency", "USD")
                    period = item.get("job_salary_period", "year")
                    if min_sal and max_sal:
                        sal_str = f"{currency} {min_sal:,.0f} – {max_sal:,.0f}/{period}"
                    elif min_sal:
                        sal_str = f"{currency} {min_sal:,.0f}/{period}"
                    else:
                        sal_str = "Competitive / Disclosed on Application"

                    # Dates
                    posted_date_raw = item.get("job_posted_at_datetime_utc") or item.get("job_posted_at_timestamp") or item.get("job_offer_expiration_datetime_utc")
                    app_url = item.get("job_apply_link") or item.get("job_google_link")
                    publisher = item.get("job_publisher") or "Direct ATS"

                    # Qualifications / highlights
                    highlights = item.get("job_highlights", {})
                    qualifications = highlights.get("Qualifications", [])
                    responsibilities = highlights.get("Responsibilities", [])
                    skills_sample = qualifications[:5] if qualifications else ["GoHighLevel CRM", "Workflow Automation"]

                    discovered_jobs.append({
                        "raw_id": job_id,
                        "title": title,
                        "company": company,
                        "company_logo": company_logo,
                        "company_domain": company_website,
                        "location": loc_str,
                        "remote_eligibility": "Open Globally" if is_remote else loc_str,
                        "work_mode": "100% Remote" if is_remote else "Hybrid / Onsite",
                        "salary": sal_str,
                        "employment_type": (item.get("job_employment_type") or "FULLTIME").replace("_", " ").title(),
                        "experience_req": "3+ years",
                        "description": desc,
                        "posted_date_raw": posted_date_raw,
                        "source": f"JSearch ({publisher})",
                        "app_url": app_url,
                        "original_url": app_url,
                        "matched_skills": skills_sample,
                        "source_type": "rapidapi_jsearch"
                    })
            else:
                print(f"[-] JSearch query '{q}' returned status code {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"[-] JSearch error on query '{q}': {e}")

    return discovered_jobs
