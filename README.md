# Gemini Spark — GoHighLevel AI Job Intelligence & Real-Time Match Portal

A specialized, autonomous daily job discovery, matching, and career intelligence dashboard specifically engineered for **Sohaib Mahmood** (GoHighLevel Developer, CRM & Marketing Automation Specialist, Funnel & Website Builder, n8n Automation Developer).

---

## 🌟 Key Features & Phase 2 Architecture

1. **Strict GoHighLevel Career Focus:**
   - 100% focused on GoHighLevel, GHL, CRM Automation, Funnel Building, Snapshot Architecture, SaaS Mode, and Workflow Engineering.
   - Generic AI, Data Science, or generic software development jobs without explicit GHL requirements are strictly excluded.

2. **0–7 Day Strict Freshness Engine:**
   - **0–3 Days:** ★★★★★ Highest Priority (`TODAY` / `1–3D AGO`)
   - **4–7 Days:** ★★★★ High Priority (`4–7D AGO`)
   - **8+ Days:** Strictly excluded from the active fresh job feed.

3. **Multi-Source Public Job Discovery:**
   - Queries public ATS endpoints and remote job APIs (Workable Direct ATS, Remotive, Jobicy, Himalayas, Employment Hero, JobLeads, etc.).
   - Multi-channel deduplication and date parsing.

4. **Permanent Exclusion of Applied Roles:**
   - When a job is marked `Applied`, `Interview Scheduled`, `Interview Completed`, `Offer`, or `Closed`, it is permanently archived in `data/application_status.json` and client-side `localStorage`.
   - Applied jobs **never** reappear in active job discovery feeds across refreshes, reloads, or CI runs.

5. **3-Hour Autonomous Automation:**
   - Runs automatically every 3 hours via GitHub Actions (`0 1,4,7,10,13,16,19,22 * * *` UTC / `00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 PKT`).
   - Supports manual execution anytime via the dashboard's **⚡ Scrape New Jobs** button or `workflow_dispatch`.

6. **Premium Production SaaS Dashboard:**
   - Linear/Vercel-inspired UI with dark charcoal aesthetics, status pipeline tabs, multi-metric filtering, sort controls, and a slide-over job detail drawer.

---

## 📁 Repository Structure

```
gemini-spark-job-dashboard/
├── .github/
│   └── workflows/
│       └── daily-update.yml       # 3-Hour autonomous discovery & deploy workflow
├── assets/
│   ├── css/
│   │   └── style.css              # Premium SaaS dark interface design system
│   └── js/
│       └── app.js                 # Reactive frontend controller & localStorage sync
├── data/
│   ├── latest.json                # Active verified dataset
│   ├── application_status.json    # Authoritative persistent status registry
│   └── history/                   # Immutable historical snapshots (YYYY-MM-DD.json)
├── scripts/
│   ├── job_discovery.py           # Real multi-source public GHL discovery engine
│   ├── generate_job_refresh.py    # End-to-end 3-hour refresh & compilation engine
│   ├── generate_daily_update.py   # Daily automation runner
│   └── generate_email_template.py # Inline-CSS email report compiler
├── build_index.py                 # Index HTML generator with embedded fallback store
├── email_template.html            # Compiled daily HTML email template
├── index.html                     # Live dashboard web application
└── README.md                      # System documentation
```

---

## 🚀 Live Deployment

- **Permanent Live Dashboard URL:** `https://chrooniq.github.io/gemini-spark-job-dashboard/`
- **Candidate Live Portfolio:** `https://sohaibmahmood.vibepreview.com/`

---

## 🛠 Local Execution & Testing

To run the job refresh cycle locally:

```bash
python scripts/generate_job_refresh.py
```

To regenerate the index page:

```bash
python build_index.py
```

To compile the daily email template:

```bash
python scripts/generate_email_template.py
```
