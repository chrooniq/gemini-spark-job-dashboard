# Gemini Spark — AI Career Intelligence & Live Job Match Portal

A decoupled, automated daily job discovery, matching, and career intelligence dashboard specifically tailored for **Sohaib Mahmood** (GoHighLevel Developer, CRM & Marketing Automation Specialist, Funnel & Website Builder, n8n Automation Developer).

---

## 🌟 Architecture & Key Features

1. **Decoupled Data Architecture:**
   - Frontend (`index.html`, `assets/css/style.css`, `assets/js/app.js`) is completely decoupled from data.
   - Dynamic JSON data feed loaded via `./data/latest.json`.
   - Immutable daily historical snapshots stored under `./data/history/YYYY-MM-DD.json`.
   - Embedded client-side fallback ensures immediate rendering even when opened directly as a local file.

2. **Interactive SaaS Dashboard UI:**
   - Real-time search across job titles, companies, tech stacks, and locations.
   - Dynamic filtering by Role category (*GoHighLevel/CRM*, *n8n Automation*, *AI Systems*, *Funnels/Web*), Application Priority (*Priority 1 — Apply*, *Priority 2 — Consider*), and Application Status (*New Match*, *Saved*, *Applied*, *Interview*).
   - Multi-metric sorting (*Match Score*, *Rank*, *Job Title*, *Company*).
   - Browser `localStorage` application status persistence.
   - Market Demand & Career Quadrant Strategy matrix (*Keep Doing*, *Improve*, *Learn*, *Watch*).

3. **Production Email Reporting:**
   - Table-based, 100% inline CSS email template (`email_template.html`).
   - Clean SaaS aesthetics adhering to the `#111827` / `#2563EB` / `#16A34A` design system.
   - Full compatibility with Gmail, Apple Mail, and Outlook.

---

## 📁 Repository Structure

```
gemini-spark-job-dashboard/
├── index.html                   # Main dashboard web app
├── email_template.html          # Redesigned daily HTML email template
├── assets/
│   ├── css/
│   │   └── style.css            # Clean, modern SaaS responsive styles
│   └── js/
│       └── app.js               # Dynamic data loader, filters, sorting & localStorage
├── data/
│   ├── latest.json              # Current active daily dataset (dynamically fetched)
│   └── history/
│       └── 2026-08-19.json      # Historical daily snapshots (never overwritten)
├── scripts/
│   ├── generate_daily_update.py # End-to-end daily update automation script
│   └── generate_email_template.py # Daily email HTML compiler
├── build_index.py               # Standalone fallback builder
└── README.md                    # System documentation & deployment guide
```

---

## 🚀 One-Time Deployment Guide

### Option 1: GitHub Pages (Recommended)
1. Create a new GitHub repository named `gemini-spark-job-dashboard` under your GitHub account (`sohaibmahmood`).
2. Push this repository:
   ```bash
   git remote add origin https://github.com/sohaibmahmood/gemini-spark-job-dashboard.git
   git branch -M main
   git push -u origin main
   ```
3. In your GitHub repo settings: Navigate to **Settings → Pages → Build and deployment → Source → Deploy from a branch (`main` / root)**.
4. Your permanent live URL will be: `https://sohaibmahmood.github.io/gemini-spark-job-dashboard/` (or custom domain `https://jobs.sohaibmahmood.com` / `https://dashboard.sohaibmahmood.com`).

### Option 2: Netlify / Vercel
- Simply link your GitHub repository to Netlify or Vercel with zero build step required (publish directory: `.`).
