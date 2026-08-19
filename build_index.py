#!/usr/bin/env python3
"""
Gemini Spark — HTML Index Builder
Compiles the production SaaS dashboard HTML application with embedded fallback store,
clean semantic structure, and zero obsolete marketing/career quadrant sections.
"""

import os
import sys
import json

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

base_dir = os.path.dirname(os.path.abspath(__file__))
latest_json_path = os.path.join(base_dir, "data", "latest.json")
index_html_path = os.path.join(base_dir, "index.html")

if os.path.exists(latest_json_path):
    with open(latest_json_path, "r", encoding="utf-8") as f:
        latest_json_str = f.read()
else:
    latest_json_str = '{"metadata": {}, "jobs": []}'

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Spark | GoHighLevel Job Intelligence Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./assets/css/style.css">
  <script>
    // Embedded fallback store for direct file:// or static server viewing
    window.FALLBACK_DATA = {latest_json_str};
  </script>
</head>
<body>

  <!-- Top Header & Navigation -->
  <header class="top-header">
    <div class="app-container header-inner">
      <div class="brand-wrap">
        <div class="brand-icon">⚡</div>
        <div>
          <div class="brand-title">
            Gemini Spark
            <span class="brand-tag">GHL INTELLIGENCE</span>
          </div>
          <div class="brand-sub">GoHighLevel & CRM Automation Portal • Sohaib Mahmood</div>
        </div>
      </div>

      <div class="header-status-group">
        <div class="live-badge" id="headerStatusBadge">
          <span class="live-dot"></span> LIVE
        </div>

        <div class="countdown-box" title="Next Autonomous Refresh (PKT UTC+5)">
          <span>Next Refresh:</span>
          <span class="countdown-val" id="nextUpdateCountdown">--:--:--</span>
        </div>

        <button id="btnScrapeJobs" class="btn-scrape-main" title="Trigger real-time GHL job discovery scan">
          <span>⚡</span> Scrape New Jobs
        </button>

        <div class="header-links">
          <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="header-link-btn" title="View Portfolio">
            <span>🌐</span> Portfolio
          </a>
          <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="header-link-btn" title="View Resume">
            <span>📄</span> Resume
          </a>
        </div>
      </div>
    </div>
  </header>

  <main class="app-container">
    
    <!-- Candidate Hero Section -->
    <section class="hero-wrapper">
      <div class="candidate-banner">
        <div class="candidate-left">
          <div class="candidate-avatar">SM</div>
          <div class="candidate-info">
            <h2>Sohaib Mahmood</h2>
            <p>GoHighLevel Developer • CRM & Marketing Automation Specialist • Funnel & Website Builder</p>
          </div>
        </div>

        <div class="candidate-pills">
          <span class="meta-pill highlight"><span class="live-dot"></span> 100% Worldwide Remote</span>
          <span class="meta-pill">📍 Lahore, Pakistan (UTC+5)</span>
          <span class="meta-pill">⏱ 4 Years Experience (50+ Builds)</span>
          <span class="meta-pill" id="searchDateBadge">Current Feed</span>
          <div class="date-selector-wrap" style="display: inline-block;">
            <select id="dateSelect" class="custom-select" style="height: 28px; padding: 0 8px; font-size: 0.72rem;" title="Switch historical snapshots">
              <option value="latest">Today</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Real-Time KPI Grid -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">New Jobs</span>
            <span class="kpi-icon">⚡</span>
          </div>
          <div class="kpi-value" id="kpiNewJobs" style="color: #38bdf8;">--</div>
          <div class="kpi-sub">Since Last Scan</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Fresh Jobs</span>
            <span class="kpi-icon">🎯</span>
          </div>
          <div class="kpi-value" id="kpiFreshJobs">--</div>
          <div class="kpi-sub">0–7 Days Active</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Top Match</span>
            <span class="kpi-icon">🔥</span>
          </div>
          <div class="kpi-value" id="kpiTopMatch" style="color: #34d399;">--%</div>
          <div class="kpi-sub">Highest Fit Score</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Saved</span>
            <span class="kpi-icon">★</span>
          </div>
          <div class="kpi-value" id="kpiSaved" style="color: #fbbf24;">--</div>
          <div class="kpi-sub">Shortlisted Roles</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Applied</span>
            <span class="kpi-icon">✓</span>
          </div>
          <div class="kpi-value" id="kpiApplied" style="color: #60a5fa;">--</div>
          <div class="kpi-sub">Excluded from Active</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Interviews</span>
            <span class="kpi-icon">💼</span>
          </div>
          <div class="kpi-value" id="kpiInterviews" style="color: #c084fc;">--</div>
          <div class="kpi-sub">Active Discussions</div>
        </div>
      </div>
    </section>

    <!-- Redesigned Status Pipeline Overview Tabs -->
    <nav class="pipeline-bar" aria-label="Status Pipeline Filter">
      <button class="pipeline-tab active" data-status-tab="all-active">
        <span>⚡ All Active (0–7D)</span>
        <span class="pipeline-count" id="cntActive">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="New Match">
        <span>✨ New Matches</span>
        <span class="pipeline-count" id="cntNew">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="Saved">
        <span>★ Saved</span>
        <span class="pipeline-count" id="cntSaved">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="Applied">
        <span>✓ Applied</span>
        <span class="pipeline-count" id="cntApplied">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="Interview Scheduled">
        <span>💬 Interview</span>
        <span class="pipeline-count" id="cntInterviews">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="Offer">
        <span>🎉 Offer</span>
        <span class="pipeline-count" id="cntOffers">0</span>
      </button>
      <button class="pipeline-tab" data-status-tab="all">
        <span>📁 All Records</span>
        <span class="pipeline-count" id="cntAll">0</span>
      </button>
    </nav>

    <!-- Search & Multi-Tier Filter Hub -->
    <section class="control-hub">
      <div class="search-row">
        <div class="search-box-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchField" class="search-input" placeholder="Search GoHighLevel roles by title, company, skills, or platform...">
        </div>

        <select id="sortSelect" class="custom-select" aria-label="Sort Feed">
          <option value="fresh-score-desc">Freshest + Highest Match (Default)</option>
          <option value="score-desc">Match Score (Highest First)</option>
          <option value="rank-asc">Rank (1 to N)</option>
          <option value="title-asc">Job Title (A–Z)</option>
          <option value="company-asc">Company (A–Z)</option>
        </select>
      </div>

      <div class="filters-row">
        <!-- Freshness Filter -->
        <div class="filter-group">
          <span class="filter-label">Freshness:</span>
          <button class="chip active" data-filter-type="freshness" data-filter="all">All (0–7D)</button>
          <button class="chip fresh-today" data-filter-type="freshness" data-filter="today">🔥 Today</button>
          <button class="chip" data-filter-type="freshness" data-filter="1-3-days">1–3 Days</button>
          <button class="chip" data-filter-type="freshness" data-filter="4-7-days">4–7 Days</button>
        </div>

        <!-- Match Score Filter -->
        <div class="filter-group">
          <span class="filter-label">Match:</span>
          <button class="chip active" data-filter-type="match" data-filter="all">All Scores</button>
          <button class="chip" data-filter-type="match" data-filter="90">90%+</button>
          <button class="chip" data-filter-type="match" data-filter="80">80%+</button>
          <button class="chip" data-filter-type="match" data-filter="70">70%+</button>
        </div>

        <!-- Work Mode Filter -->
        <div class="filter-group">
          <span class="filter-label">Mode:</span>
          <button class="chip active" data-filter-type="workmode" data-filter="all">All Modes</button>
          <button class="chip" data-filter-type="workmode" data-filter="remote">100% Remote</button>
        </div>

        <!-- Priority Filter -->
        <div class="filter-group">
          <span class="filter-label">Priority:</span>
          <button class="chip active" data-filter-type="priority" data-filter="all">All Priorities</button>
          <button class="chip" data-filter-type="priority" data-filter="prio-apply">🔥 P1 Apply</button>
          <button class="chip" data-filter-type="priority" data-filter="prio-consider">🟢 P2 Consider</button>
        </div>
      </div>
    </section>

    <!-- Job Feed Grid Header -->
    <div class="feed-header">
      <h3 class="feed-title">
        <span>GoHighLevel Opportunities</span>
        <span class="feed-count-badge" id="feedCountBadge">Loading...</span>
      </h3>
      <div style="font-size: 0.76rem; color: var(--text-muted);">
        Last Refreshed: <span id="lastUpdatedBadge" style="color: var(--text-secondary); font-weight: 600;">--</span>
      </div>
    </div>

    <!-- Job Cards Feed Container -->
    <section class="jobs-grid" id="jobsGridContainer"></section>

    <!-- Clean Empty State -->
    <section class="empty-state" id="emptyState" style="display: none;">
      <div class="empty-icon">⚡</div>
      <h3>No new GoHighLevel opportunities found</h3>
      <p>
        No active roles match your current filter criteria or all listed opportunities have been processed.
      </p>
      <div style="margin-bottom: 18px; font-size: 0.8rem; color: var(--text-muted);">
        Next automatic scan: <span id="emptyCountdown" style="color: #38bdf8; font-weight: 700; font-family: monospace;">--:--:--</span>
      </div>
      <button id="btnEmptyScrape" class="btn-scrape-main" style="margin: 0 auto; display: inline-flex;">
        <span>⚡</span> Scrape New Jobs
      </button>
    </section>

  </main>

  <!-- Slide-Over Right Job Detail Drawer -->
  <div class="drawer-backdrop" id="drawerBackdrop"></div>
  <aside class="job-drawer" id="jobDrawer" aria-label="Job Detail Drawer">
    <div class="drawer-header">
      <div style="font-size: 0.76rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em;">
        GHL OPPORTUNITY BREAKDOWN
      </div>
      <button class="drawer-close-btn" id="drawerCloseBtn" aria-label="Close Drawer">✕</button>
    </div>

    <div class="drawer-body">
      <div class="drawer-title-box">
        <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;" id="drawerCompany">Company</div>
        <h3 id="drawerJobTitle">Job Title</h3>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
          <div class="score-badge excellent" id="drawerScoreNum" style="font-size: 1.1rem; padding: 5px 10px;">--%</div>
          <span style="font-size: 0.82rem; font-weight: 700; color: #34d399;" id="drawerScoreCat">Match</span>
        </div>
      </div>

      <div class="drawer-meta-grid">
        <div class="drawer-meta-item">
          <div class="meta-k">📍 Location</div>
          <div class="meta-v" id="drawerLocation">Worldwide Remote</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">💼 Work Mode</div>
          <div class="meta-v" id="drawerWorkMode">100% Remote</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">💰 Compensation</div>
          <div class="meta-v" id="drawerSalary">Competitive</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">⏱ Experience</div>
          <div class="meta-v" id="drawerExp">3+ Years</div>
        </div>
        <div class="drawer-meta-item" style="grid-column: span 2;">
          <div class="meta-k">📅 Published Date</div>
          <div class="meta-v" id="drawerPosted">Recent</div>
        </div>
      </div>

      <div class="drawer-section-title">WHY THIS MATCHES SOHAIB'S PROFILE</div>
      <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 18px;" id="drawerWhy"></p>

      <div class="drawer-section-title">7-DIMENSION MATCH BREAKDOWN</div>
      <div class="drawer-breakdown-box" id="drawerScoreBreakdown"></div>

      <div class="drawer-section-title">VERIFIED MATCHING SKILLS</div>
      <div class="skills-tags" id="drawerMatchedSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">MISSING / BONUS QUALIFICATIONS</div>
      <div class="skills-tags" id="drawerMissingSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">ADVANTAGE HIGHLIGHTS</div>
      <div class="skills-tags" id="drawerAdvSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">POTENTIAL CONSIDERATIONS</div>
      <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.45; margin-bottom: 20px;" id="drawerConcerns"></p>
    </div>

    <div class="drawer-footer">
      <div>
        <select class="card-status-select" id="drawerStatusSelect" style="height: 38px; padding: 0 10px; font-size: 0.78rem;">
          <option value="New Match">New Match</option>
          <option value="Saved">Saved</option>
          <option value="Applied">Applied</option>
          <option value="Interview Scheduled">Interview Scheduled</option>
          <option value="Offer">Offer</option>
          <option value="Closed">Closed</option>
        </select>
      </div>

      <div style="display: flex; gap: 8px;">
        <button id="drawerMarkAppliedBtn" class="btn-save-card" style="padding: 8px 14px;">
          ✓ Mark Applied
        </button>
        <a id="drawerApplyBtn" href="#" target="_blank" class="btn-apply-card" style="padding: 8px 18px; font-size: 0.82rem;">
          Apply Directly →
        </a>
      </div>
    </div>
  </aside>

  <!-- Footer -->
  <footer class="app-footer">
    <div class="app-container">
      <p><strong>Gemini Spark AI Job Intelligence</strong> • Autonomous GoHighLevel Job Matching Engine</p>
      <p style="margin-top: 4px; color: var(--text-dim);">
        Tailored for Sohaib Mahmood • Lahore, Pakistan (UTC+5) • 100% Worldwide Remote Career Hub
      </p>
    </div>
  </footer>

  <script src="./assets/js/app.js"></script>
</body>
</html>
"""

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(index_html)

print("✓ index.html successfully compiled with Phase 2 GHL architecture.")
