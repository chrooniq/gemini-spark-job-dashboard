import requests
import json

queries = ["gohighlevel", "highlevel", "ghl"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

all_found = []

for q in queries:
    url = f"https://jobs.workable.com/api/v1/jobs?query={q}&location=Remote"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for j in data.get("jobs", []):
                title = j.get("title", "")
                company = j.get("company", {}).get("title", "")
                link = j.get("url") or j.get("applicationUrl") or f"https://jobs.workable.com/view/{j.get('shortcode')}"
                all_found.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "shortcode": j.get("shortcode"),
                    "location": j.get("location", {}).get("city") or "Remote"
                })
    except Exception as e:
        print(f"Error querying {q}: {e}")

print(f"Total Workable jobs found: {len(all_found)}")
for item in all_found[:15]:
    print(f" - {item['title']} @ {item['company']} -> {item['link']}")
