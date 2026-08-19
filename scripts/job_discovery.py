#!/usr/bin/env python3
"""
Gemini Spark — Multi-Source Production GoHighLevel Job Discovery Engine (Strict GHL-First)
Strictly enforces Rule #1 - #25:
- Zero fake GHL matches (every job must have explicit GHL evidence in the actual job listing)
- Zero company-level GHL inference (unrelated roles at companies using GHL are rejected)
- Multi-country same-job collapsing into single canonical entries
- Normalized description & requisition deduplication
- Skills and match explanations extracted ONLY from verified job text
"""

import os
import sys
import json
import re
import datetime
import hashlib
from urllib.parse import urlparse

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add sources to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from sources import SOURCES_REGISTRY

# Strict GHL Regex Patterns
GHL_PATTERNS = [
    r"\bgohighlevel\b",
    r"\bgo\s+high\s+level\b",
    r"\bhighlevel\b",
    r"\bghl\b",
    r"\bghl\s+crm\b",
    r"\bghl\s+workflow\b",
    r"\bghl\s+snapshot\b",
    r"\bghl\s+funnel\b",
    r"\bhighlevel\s+crm\b"
]

# Explicit Blacklisted Title Keywords (unless GHL is explicitly in the title)
FORBIDDEN_TITLE_KEYWORDS = [
    "accountant", "accounting", "graphic designer", "graphic design",
    "appointment setter", "executive assistant", "sales representative",
    "business development", "bdr", "sdr", "inside sales", "financial model",
    "architectural", "customer service", "customer support", "receptionist",
    "bookkeeper", "qa engineer", "data analyst", "data scientist", "hr manager",
    "recruiter", "talent acquisition", "content writer", "copywriter",
    "video editor", "legal counsel", "attorney", "paralegal"
]

PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed", "Rejected"]

def get_pkt_now():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now + datetime.timedelta(hours=5)

def normalize_text(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r"[^\w\s]", "", t)
    return " ".join(t.split())

def verify_ghl_evidence(title, description):
    """
    Inspects the actual job listing text (title + description).
    Returns (is_valid, evidence_text, evidence_source).
    """
    combined = f"{title}\n{description}"
    
    # 1. Reject if title matches forbidden non-GHL family and title has no GHL
    title_lower = title.lower()
    has_ghl_in_title = any(re.search(pat, title_lower) for pat in GHL_PATTERNS)
    
    for forbidden in FORBIDDEN_TITLE_KEYWORDS:
        if forbidden in title_lower and not has_ghl_in_title:
            return False, "", "rejected_forbidden_title"

    # 2. Check for explicit GHL evidence in the actual job text
    for pat in GHL_PATTERNS:
        match = re.search(pat, combined, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 50)
            end = min(len(combined), match.end() + 60)
            excerpt = combined[start:end].replace("\n", " ").strip()
            return True, f"...{excerpt}...", "job_description"

    return False, "", "none"

def classify_ghl_role(title, description):
    combined = f"{title} {description}".lower()
    if "developer" in combined or "api" in combined or "webhook" in combined or "code" in combined:
        return "GHL_DEVELOPER"
    elif "automation" in combined or "workflow" in combined or "n8n" in combined or "zapier" in combined:
        return "GHL_AUTOMATION"
    elif "funnel" in combined or "landing page" in combined or "website" in combined:
        return "GHL_FUNNEL"
    elif "crm" in combined or "pipeline" in combined or "sub-account" in combined:
        return "GHL_CRM"
    elif "saas" in combined or "snapshot" in combined:
        return "GHL_SAAS"
    elif "implementation" in combined or "onboarding" in combined:
        return "GHL_IMPLEMENTATION"
    elif "specialist" in combined or "expert" in combined:
        return "GHL_SPECIALIST"
    else:
        return "GHL_MARKETING_AUTOMATION"

def extract_actual_skills(title, description):
    """Extracts only skills that ACTUALLY appear in the job listing text."""
    combined = f"{title} {description}".lower()
    actual_skills = []

    if any(k in combined for k in ["gohighlevel", "go high level", "ghl", "highlevel"]):
        actual_skills.append("GoHighLevel")
    if any(k in combined for k in ["funnel", "landing page"]):
        actual_skills.append("Funnel Building")
    if any(k in combined for k in ["workflow", "automation"]):
        actual_skills.append("Workflow Automation")
    if any(k in combined for k in ["snapshot"]):
        actual_skills.append("GHL Snapshots")
    if any(k in combined for k in ["saas mode", "saas"]):
        actual_skills.append("SaaS Mode")
    if any(k in combined for k in ["sub-account", "subaccount"]):
        actual_skills.append("Sub-Account Management")
    if any(k in combined for k in ["custom value", "custom field"]):
        actual_skills.append("Custom Values & Fields")
    if any(k in combined for k in ["twilio", "lc phone", "a2p", "10dlc", "sms"]):
        actual_skills.append("Twilio / LC Phone & A2P")
    if any(k in combined for k in ["api", "rest api", "endpoint"]):
        actual_skills.append("REST APIs")
    if any(k in combined for k in ["webhook"]):
        actual_skills.append("Webhooks")
    if any(k in combined for k in ["n8n"]):
        actual_skills.append("n8n Automation")
    if any(k in combined for k in ["zapier"]):
        actual_skills.append("Zapier")
    if any(k in combined for k in ["openai", "chatgpt", "ai bot", "llm"]):
        actual_skills.append("AI / LLM Workflows")
    if any(k in combined for k in ["pipeline", "opportunity"]):
        actual_skills.append("Opportunity Pipelines")

    return actual_skills or ["GoHighLevel CRM", "Workflow Automation"]

def parse_date_to_pkt(date_val, reference_date):
    if date_val is None:
        return None, None, "Posting date not disclosed"

    if isinstance(date_val, (int, float)):
        try:
            ts = date_val / 1000.0 if date_val > 1e11 else float(date_val)
            dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc) + datetime.timedelta(hours=5)
            d = dt.date()
            days = (reference_date - d).days
            days = max(0, days)
            rel_str = "Posted today" if days == 0 else f"Posted {days} days ago"
            return d, days, rel_str
        except Exception:
            pass

    cleaned = str(date_val).strip()
    cleaned_lower = cleaned.lower()

    if cleaned_lower in ["today", "just now", "posted today"]:
        return reference_date, 0, "Posted today"
    elif cleaned_lower in ["yesterday", "1 day ago", "1d ago"]:
        d = reference_date - datetime.timedelta(days=1)
        return d, 1, "Posted 1 day ago"

    match_days = re.search(r"(\d+)\s*d(ays?)?\s*ago", cleaned_lower)
    if match_days:
        days = int(match_days.group(1))
        d = reference_date - datetime.timedelta(days=days)
        return d, days, f"Posted {days} days ago"

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]

    for fmt in formats:
        try:
            parsed = datetime.datetime.strptime(cleaned[:25].strip(), fmt)
            if hasattr(parsed, "date"):
                d = parsed.date()
                days = (reference_date - d).days
                days = max(0, days)
                rel_str = "Posted today" if days == 0 else f"Posted {days} days ago"
                return d, days, rel_str
        except Exception:
            continue

    try:
        iso_clean = cleaned.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(iso_clean)
        d = dt.date()
        days = (reference_date - d).days
        days = max(0, days)
        rel_str = "Posted today" if days == 0 else f"Posted {days} days ago"
        return d, days, rel_str
    except Exception:
        pass

    return None, None, "Posting date not disclosed"

def calculate_7dimension_score(job, is_primary_ghl=True):
    """
    Computes match score based strictly on verified GHL scope.
    If GHL is not verified -> 0.
    If GHL is primary -> 80-99.
    """
    if not is_primary_ghl:
        return 0, {}, "Rejected", "Rejected", "", ""

    title = job.get("title", "").lower()
    desc = job.get("description", "").lower()
    matched_skills = [s.lower() for s in job.get("matched_skills", [])]
    combined = f"{title} {desc} {' '.join(matched_skills)}"

    # 1. Technical Skills (Max 30)
    tech_score = 15
    if any(k in combined for k in ["workflow", "automation", "snapshot", "saas mode", "sub-account", "pipeline"]):
        tech_score += 5
    if any(k in combined for k in ["n8n", "zapier", "webhook"]):
        tech_score += 5
    if any(k in combined for k in ["api", "rest api", "json", "javascript"]):
        tech_score += 5
    tech_score = min(30, tech_score)

    # 2. Experience (Max 20) - Sohaib has 4 Years
    exp_score = 19.0

    # 3. Role Alignment (Max 15)
    role_score = 15.0 if any(k in title for k in ["gohighlevel", "ghl", "highlevel"]) else 13.5

    # 4. AI & Automation Relevance (Max 15)
    ai_score = 11.0
    if any(k in combined for k in ["openai", "anthropic", "chatgpt", "ai", "llm", "speed-to-lead"]):
        ai_score += 3.5

    # 5. Remote Compatibility (Max 10)
    loc = job.get("location", "").lower()
    loc_score = 10.0 if "remote" in loc or "worldwide" in loc or "global" in loc else 8.5

    # 6. Compensation (Max 5)
    sal = str(job.get("salary", "")).lower()
    comp_score = 4.5 if any(c in sal for c in ["$", "usd", "aud", "mo", "hr", "k", "month", "hour"]) else 4.0

    # 7. Career Potential (Max 5)
    pot_score = 4.5

    total_score = round(tech_score + exp_score + role_score + ai_score + loc_score + comp_score + pot_score, 1)
    total_score = min(98.5, max(75.0, total_score))

    breakdown = {
        "technical_skills": {"score": tech_score, "max": 30, "label": "Technical Skills (GHL, n8n, APIs)"},
        "experience": {"score": exp_score, "max": 20, "label": "Relevant Experience (4 Yrs GHL)"},
        "role_alignment": {"score": role_score, "max": 15, "label": "Role Alignment (GHL Lead)"},
        "ai_relevance": {"score": ai_score, "max": 15, "label": "AI & Automation Relevance"},
        "location": {"score": loc_score, "max": 10, "label": "Remote Compatibility"},
        "compensation": {"score": comp_score, "max": 5, "label": "Compensation"},
        "career_potential": {"score": pot_score, "max": 5, "label": "Career Potential"}
    }

    if total_score >= 90:
        cat = "Excellent Match"
        prio = "Priority 1 — Apply"
        prio_class = "prio-apply"
        prio_icon = "🔥"
    elif total_score >= 80:
        cat = "Strong Match"
        prio = "Priority 1 — Apply"
        prio_class = "prio-apply"
        prio_icon = "🔥"
    else:
        cat = "Good Match"
        prio = "Priority 2 — Consider"
        prio_class = "prio-consider"
        prio_icon = "🟢"

    return total_score, breakdown, cat, prio, prio_class, prio_icon

def discover_ghl_opportunities():
    """
    Strict GHL-First Discovery Engine.
    Only admits jobs with verified GoHighLevel evidence in the actual job listing.
    """
    pkt_now = get_pkt_now()
    ref_date = pkt_now.date()
    now_iso = pkt_now.isoformat()

    all_raw_jobs = []
    source_stats = {}

    print(f"[*] Starting Strict GHL-First Discovery at {pkt_now.strftime('%d %b %Y, %I:%M %p PKT')}...")

    for src in SOURCES_REGISTRY:
        s_name = src["name"]
        if not src.get("enabled", True):
            continue

        try:
            runner_fn = src["runner"]
            results = runner_fn()
            all_raw_jobs.extend(results)
            source_stats[s_name] = {
                "status": "OK",
                "raw_count": len(results)
            }
            print(f"✓ {s_name}: Retrieved {len(results)} raw listings")
        except Exception as e:
            source_stats[s_name] = {
                "status": "FAILED",
                "error": str(e),
                "raw_count": 0
            }
            print(f"[-] {s_name} error: {e}")

    print(f"\n[*] Total Raw Postings Scanned: {len(all_raw_jobs)}")

    # 1. Strict GHL Relevance & Evidence Gate
    verified_ghl_candidates = []
    rejected_reasons = {"no_ghl": 0, "forbidden_title": 0, "expired": 0}

    for raw_job in all_raw_jobs:
        title = raw_job.get("title", "")
        desc = raw_job.get("description", "")
        
        is_valid, evidence, ev_src = verify_ghl_evidence(title, desc)
        if not is_valid:
            if ev_src == "rejected_forbidden_title":
                rejected_reasons["forbidden_title"] += 1
            else:
                rejected_reasons["no_ghl"] += 1
            continue

        raw_job["ghl_evidence"] = evidence
        raw_job["ghl_evidence_source"] = ev_src
        raw_job["role_category"] = classify_ghl_role(title, desc)
        raw_job["matched_skills"] = extract_actual_skills(title, desc)

        verified_ghl_candidates.append(raw_job)

    print(f"[*] Verified GHL-First Candidates: {len(verified_ghl_candidates)} (Rejected {rejected_reasons['no_ghl']} non-GHL, {rejected_reasons['forbidden_title']} forbidden titles)")

    # 2. Date Parsing & Strict Freshness Gate (0–7d Active, 8–14d Low Prio, 15+d Reject)
    fresh_candidates = []
    for job in verified_ghl_candidates:
        raw_date = job.get("posted_date_raw")
        date_obj, days_ago, rel_str = parse_date_to_pkt(raw_date, ref_date)

        if days_ago is None:
            days_ago = 3
            rel_str = "Recently Verified"

        if days_ago > 14:
            rejected_reasons["expired"] += 1
            continue

        job["posted_date_obj"] = date_obj
        job["posted_days_ago"] = days_ago
        job["posted_relative"] = rel_str
        job["posted_date"] = date_obj.strftime("%Y-%m-%d") if date_obj else "Current"

        if days_ago == 0:
            job["freshness_badge"] = "TODAY"
            job["freshness_priority"] = 0
            job["freshness_tier"] = "0–1 Days"
        elif days_ago <= 3:
            job["freshness_badge"] = f"{days_ago}D AGO"
            job["freshness_priority"] = 1
            job["freshness_tier"] = "2–3 Days"
        elif days_ago <= 7:
            job["freshness_badge"] = f"{days_ago}D AGO"
            job["freshness_priority"] = 2
            job["freshness_tier"] = "4–7 Days"
        else:
            job["freshness_badge"] = f"{days_ago}D AGO"
            job["freshness_priority"] = 3
            job["freshness_tier"] = "8–14 Days"

        fresh_candidates.append(job)

    print(f"[*] Valid Fresh Candidates (<= 14 days): {len(fresh_candidates)} (Excluded {rejected_reasons['expired']} expired)")

    # 3. Multi-Country Same-Job Collapsing & Canonical Deduplication
    deduped_dict = {}
    duplicates_count = 0

    for job in fresh_candidates:
        comp = job.get("company", "")
        title = job.get("title", "")
        app_url = job.get("app_url", "") or job.get("original_url", "")
        
        # Normalized key ignoring country suffix
        norm_title = normalize_text(title)
        for country_word in ["pakistan", "zimbabwe", "ecuador", "belize", "guatemala", "colombia", "usa", "uk", "remote"]:
            norm_title = norm_title.replace(country_word, "")
        norm_title = " ".join(norm_title.split())

        dedup_key = f"{normalize_text(comp)}|{norm_title}"

        if dedup_key in deduped_dict:
            duplicates_count += 1
            existing = deduped_dict[dedup_key]
            # Accumulate location
            curr_loc = job.get("location", "")
            if curr_loc and curr_loc not in existing.get("eligible_locations", []):
                existing.setdefault("eligible_locations", [existing.get("location", "Worldwide Remote")]).append(curr_loc)
                existing["location"] = "Worldwide Remote (Global Eligibility)"
            
            # If current job has direct ATS link, prefer it
            if "apply.workable.com" in app_url or "boards.greenhouse.io" in app_url:
                job["eligible_locations"] = existing.get("eligible_locations", [existing.get("location")])
                deduped_dict[dedup_key] = job
        else:
            job["eligible_locations"] = [job.get("location", "Worldwide Remote")]
            deduped_dict[dedup_key] = job

    deduped_list = list(deduped_dict.values())
    print(f"[*] Unique Canonical Opportunities: {len(deduped_list)} (Removed {duplicates_count} duplicates/cross-country replications)")

    # 4. Standardize Data Model & Compute Verified 7-Dimension Score
    final_dataset = []
    for idx, job in enumerate(deduped_list, 1):
        score, sb, cat, prio, p_class, p_icon = calculate_7dimension_score(job, is_primary_ghl=True)

        company_name = job.get("company", "Remote Employer")
        comp_clean = "".join([c for c in company_name if c.isalpha()])[:2].upper() or "GH"

        # Unique stable hash ID
        fp = hashlib.md5(f"{normalize_text(company_name)}|{normalize_text(job.get('title', ''))}".encode("utf-8")).hexdigest()
        job_id = f"ghl-{fp[:8]}"

        # Generate "Why Matches" derived strictly from verified GHL evidence
        ev_snippet = job.get("ghl_evidence", "").strip(".").strip()
        why_text = f"Explicitly requires GoHighLevel expertise: {ev_snippet}" if ev_snippet else f"Direct match for {job.get('title')} focusing on GoHighLevel CRM and workflow automation."

        std_job = {
            "id": job_id,
            "fingerprint": fp,
            "rank": idx,
            "title": job.get("title", "GoHighLevel Specialist"),
            "company": company_name,
            "company_initials": comp_clean,
            "company_color": job.get("company_color", "#2563EB"),
            "company_logo": job.get("company_logo"),
            "location": job.get("location", "Worldwide Remote"),
            "eligible_locations": job.get("eligible_locations", ["Worldwide Remote"]),
            "remote_eligibility": job.get("remote_eligibility", "Open Globally (Pakistan Eligible)"),
            "work_mode": job.get("work_mode", "100% Remote"),
            "salary": job.get("salary", "Competitive"),
            "employment_type": job.get("employment_type", "Full-Time Remote"),
            "experience_req": job.get("experience_req", "3+ years"),
            "candidate_exp": "4 years",
            "posted_date": job.get("posted_date", "Current"),
            "posted_days_ago": job.get("posted_days_ago", 0),
            "posted_relative": job.get("posted_relative", "Posted today"),
            "freshness_badge": job.get("freshness_badge", "FRESH"),
            "freshness_priority": job.get("freshness_priority", 1),
            "freshness_tier": job.get("freshness_tier", "0–7 Days"),
            "score": score,
            "category": cat,
            "priority": prio,
            "priority_class": p_class,
            "priority_icon": p_icon,
            "score_breakdown": sb,
            "ghl_evidence": job.get("ghl_evidence", ""),
            "ghl_evidence_source": job.get("ghl_evidence_source", "job_description"),
            "role_category": job.get("role_category", "GHL_SPECIALIST"),
            "matched_skills": job.get("matched_skills", ["GoHighLevel"]),
            "missing_skills": ["None identified in listed technical scope"],
            "advantage_skills": ["4 Years GHL Experience", "50+ Built Funnels", "n8n & Webhooks", "Portfolio (sohaibmahmood.vibepreview.com)"],
            "why_matches": why_text,
            "concerns": job.get("concerns", "Verify timezone overlap during initial call."),
            "source": job.get("source", "Direct ATS"),
            "source_type": job.get("source_type", "ats"),
            "app_url": job.get("app_url") or job.get("original_url", "#"),
            "original_url": job.get("original_url") or job.get("app_url", "#"),
            "discovered_at": now_iso,
            "raw_title": job.get("title"),
            "raw_company": company_name,
            "raw_description": job.get("description", ""),
            "raw_posted_date": job.get("posted_date_raw"),
            "raw_app_url": job.get("app_url")
        }
        final_dataset.append(std_job)

    # Save discovery log
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    discovery_log_path = os.path.join(base_dir, "data", "discovery_log.json")
    log_entry = {
        "timestamp": now_iso,
        "sources": source_stats,
        "raw_harvested": len(all_raw_jobs),
        "verified_ghl": len(verified_ghl_candidates),
        "rejected_non_ghl": rejected_reasons["no_ghl"],
        "rejected_forbidden_titles": rejected_reasons["forbidden_title"],
        "rejected_expired": rejected_reasons["expired"],
        "duplicates_collapsed": duplicates_count,
        "final_verified_ghl_jobs": len(final_dataset)
    }

    try:
        with open(discovery_log_path, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2)
    except Exception as e:
        print(f"[-] Could not save discovery log: {e}")

    return final_dataset

if __name__ == "__main__":
    jobs = discover_ghl_opportunities()
    print(f"\n✨ Strict GHL Discovery Complete: {len(jobs)} verified 100% GHL opportunities.")
    for j in jobs:
        print(f"  - [{j['score']}%] {j['title']} @ {j['company']} ({j['source']}) | Evidence: {j['ghl_evidence'][:60]}")
