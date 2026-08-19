#!/usr/bin/env python3
"""
Gemini Spark — Full-Page "Jobi" SaaS Dashboard Builder
Builds the complete production web app with full-page layout, crisp vector SVG icons,
embedded CSS for instant 100% style fidelity on GitHub Pages, Chart.js graph,
and full-featured multi-page/tab interactive views.
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
css_path = os.path.join(base_dir, "assets", "css", "style.css")

if os.path.exists(latest_json_path):
    with open(latest_json_path, "r", encoding="utf-8") as f:
        latest_json_str = f.read()
else:
    latest_json_str = '{"metadata": {}, "jobs": []}'

if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        embedded_css = f.read()
else:
    embedded_css = ""

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>jobi | Gemini Spark GoHighLevel Job Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
{embedded_css}
  </style>
  <script>
    // Embedded fallback store for direct file:// and static server viewing
    window.FALLBACK_DATA = {latest_json_str};
  </script>
</head>
<body>

  <!-- Full-Page Layout Container -->
  <div class="app-shell">

    <!-- Left Sidebar (Full Viewport Height) -->
    <aside class="sidebar" aria-label="Main Navigation">
      <div>
        <!-- Brand / Logo -->
        <div class="sidebar-brand-row">
          <div class="brand-dot-logo"></div>
          <div class="brand-title-text">jobi</div>
        </div>

        <!-- User Profile Box -->
        <div class="sidebar-user-box">
          <div class="sidebar-avatar">SM</div>
          <div class="sidebar-user-name">
            <span>Sohaib Mahmood</span>
            <svg class="svg-icon" style="width: 12px; height: 12px;" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </div>
          <div class="sidebar-user-role">GHL & CRM Developer</div>
        </div>

        <!-- Navigation Links -->
        <nav class="sidebar-nav-group">
          <button class="nav-link-btn active" data-view="dashboard" data-filter="all-active">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
            <span>Dashboard</span>
            <span class="nav-counter-pill" id="cntSidebarActive">11</span>
          </button>

          <button class="nav-link-btn" data-view="profile">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span>My Profile</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="all-active">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            <span>My Jobs (GHL)</span>
            <span class="nav-counter-pill" id="cntSidebarJobs">11</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="New Match">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>New Matches</span>
            <span class="nav-counter-pill" id="cntSidebarNew">11</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="Saved">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            <span>Saved Jobs</span>
            <span class="nav-counter-pill" id="cntSidebarSaved">0</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="Applied">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>Applied Jobs</span>
            <span class="nav-counter-pill" id="cntSidebarApplied">0</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="Interview Scheduled">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span>Interviews</span>
            <span class="nav-counter-pill" id="cntSidebarInterview">0</span>
          </button>

          <button class="nav-link-btn" data-view="feed" data-filter="all">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            <span>All Records</span>
            <span class="nav-counter-pill" id="cntSidebarAll">11</span>
          </button>
        </nav>
      </div>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer">
        <div class="fit-progress-box">
          <div class="fit-progress-header">
            <span>Profile Match Strength</span>
            <span style="color: var(--forest-green); font-weight: 800;">87%</span>
          </div>
          <div class="fit-progress-track">
            <div class="fit-progress-fill" style="width: 87%;"></div>
          </div>
        </div>

        <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="sidebar-sub-btn">
          <svg class="svg-icon" style="width: 15px; height: 15px;" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          <span>Live Portfolio</span>
        </a>
      </div>
    </aside>

    <!-- Main Viewport (Scrollable Content Area) -->
    <main class="main-viewport">

      <!-- Top Navbar -->
      <header class="top-navbar">
        <div class="top-nav-links">
          <a href="#" class="top-nav-link active" data-view="dashboard">Home</a>
          <a href="#" class="top-nav-link" data-view="feed" data-filter="all-active">GHL Jobs</a>
          <a href="#" class="top-nav-link" data-view="profile">Profile</a>
          <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="top-nav-link">Resume</a>
          <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="top-nav-link">Portfolio</a>
        </div>

        <div class="top-right-group">
          <!-- Search input with vector SVG icon -->
          <div class="search-pill-wrap">
            <svg class="search-svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" id="topSearchInput" class="search-pill-input" placeholder="Search GHL jobs...">
          </div>

          <!-- History snapshot selector -->
          <select id="dateSelect" class="date-select-pill" title="History Snapshots">
            <option value="latest">Today</option>
          </select>

          <!-- Main CTA button -->
          <button id="btnScrapeJobs" class="btn-scrape-cta" title="Scrape & refresh GoHighLevel jobs in real-time">
            <svg class="svg-icon" style="width: 14px; height: 14px; stroke: #ffffff; fill: none;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>Scrape New Jobs</span>
          </button>
        </div>
      </header>

      <!-- View: Dashboard (Default Main Page) -->
      <div class="view-content" id="viewDashboard">

        <!-- Title & Status Row -->
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">Dashboard</h1>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
              GoHighLevel & CRM Automation Intelligence • Candidate: <strong>Sohaib Mahmood</strong>
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="live-badge-box" id="headerStatusBadge">
              <span class="live-dot-pulse"></span> LIVE 3H REFRESH
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">
              Next: <span id="nextUpdateCountdown" style="font-weight: 800; font-family: monospace; color: var(--forest-green);">--:--:--</span>
            </div>
          </div>
        </div>

        <!-- 4 Stat Metric Cards (Exact Jobi Specs with Neon Lime SVG Badges) -->
        <section class="stat-cards-container" aria-label="Key Performance Indicators">
          <!-- Stat 1: Fresh Jobs -->
          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="statFreshJobs">07</div>
              <div class="stat-sub-label">Fresh GHL Jobs (0–7D)</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
          </div>

          <!-- Stat 2: New Discovered -->
          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="statNewJobs">03</div>
              <div class="stat-sub-label">New Discovered</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            </div>
          </div>

          <!-- Stat 3: Total Discoveries -->
          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="statTotalJobs">11</div>
              <div class="stat-sub-label">GHL Opportunities</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            </div>
          </div>

          <!-- Stat 4: Top Match Score -->
          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="statTopMatch">98%</div>
              <div class="stat-sub-label">Top Fit Score</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
          </div>
        </section>

        <!-- Middle Section: Chart & Recent Matches List -->
        <section class="analytics-two-col">
          <!-- Left: Job Views & Match Velocity Chart -->
          <div class="white-panel-box">
            <div class="panel-title-bar">
              <div>
                <div class="panel-heading">Job Match Intelligence</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">
                  GoHighLevel CRM & Automation Match Trajectory
                </div>
              </div>
              <div class="time-tabs-bar">
                <button class="time-tab-btn" data-time-tab="day">Day</button>
                <button class="time-tab-btn active" data-time-tab="week">Week</button>
                <button class="time-tab-btn" data-time-tab="month">Month</button>
                <button class="time-tab-btn" data-time-tab="all">All</button>
              </div>
            </div>

            <div class="chart-wrapper-inner">
              <canvas id="jobViewsChart"></canvas>
            </div>
          </div>

          <!-- Right: Posted / Top Strategic Matches -->
          <div class="white-panel-box">
            <div class="panel-title-bar">
              <div class="panel-heading">Top GHL Focus</div>
              <span style="font-size: 0.72rem; font-weight: 700; color: var(--forest-green);">PRIORITY 1</span>
            </div>

            <div class="mini-top-list" id="miniTopMatchesList">
              <!-- Populated dynamically by app.js -->
            </div>
          </div>
        </section>

        <!-- Bottom Feed Section: All Ranked GHL Opportunities -->
        <section>
          <div class="feed-header-bar">
            <div>
              <h2 class="feed-header-title">Live GoHighLevel Opportunities</h2>
              <span style="font-size: 0.76rem; color: var(--text-muted);" id="feedCountBadge">11 Opportunities Available</span>
            </div>

            <!-- Filter Chips -->
            <div class="filter-chips-row">
              <button class="filter-chip-btn active" data-filter-type="freshness" data-filter="all">All (0–7D)</button>
              <button class="filter-chip-btn" data-filter-type="freshness" data-filter="today">Today</button>
              <button class="filter-chip-btn" data-filter-type="freshness" data-filter="1-3-days">1–3 Days</button>
              <button class="filter-chip-btn" data-filter-type="freshness" data-filter="4-7-days">4–7 Days</button>
              <button class="filter-chip-btn" data-filter-type="match" data-filter="90">90%+</button>
              <button class="filter-chip-btn" data-filter-type="workmode" data-filter="remote">100% Remote</button>
            </div>
          </div>

          <!-- Job Cards Grid Deck -->
          <div class="job-cards-grid" id="jobsGridContainer">
            <!-- Populated dynamically by app.js -->
          </div>

          <!-- Empty State -->
          <div class="empty-state" id="emptyState" style="display: none;">
            <div class="empty-icon-wrap">
              <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
            <h3>No GoHighLevel opportunities found</h3>
            <p>
              No active roles match your current filter criteria or all listed opportunities have been processed.
            </p>
            <button id="btnEmptyScrape" class="btn-scrape-cta" style="margin: 0 auto; display: inline-flex;">
              <svg class="svg-icon" style="width: 14px; height: 14px; stroke: #ffffff; fill: none;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              <span>Scrape New Jobs</span>
            </button>
          </div>
        </section>

      </div>

      <!-- View: Candidate Profile -->
      <div class="view-content" id="viewProfile" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">Candidate Profile</h1>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
              Sohaib Mahmood • GoHighLevel & CRM Automation Specialist
            </p>
          </div>
        </div>

        <div class="white-panel-box" style="margin-top: 10px;">
          <div style="display: flex; gap: 24px; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 20px; margin-bottom: 20px;">
            <div class="sidebar-avatar" style="width: 72px; height: 72px; font-size: 1.5rem;">SM</div>
            <div>
              <h2 style="font-size: 1.3rem; font-weight: 800; color: var(--text-main);">Sohaib Mahmood</h2>
              <p style="font-size: 0.84rem; color: var(--forest-green); font-weight: 700; margin-top: 2px;">
                GoHighLevel Developer | CRM & Marketing Automation | Funnel & Website Builder
              </p>
              <div style="display: flex; gap: 12px; margin-top: 8px; font-size: 0.78rem; color: var(--text-muted);">
                <span>📍 Lahore, Pakistan (UTC+5)</span>
                <span>⏱ 4 Years Experience (50+ Builds)</span>
                <span>🌍 100% Worldwide Remote</span>
              </div>
            </div>
          </div>

          <h3 style="font-size: 1rem; font-weight: 700; color: var(--text-main); margin-bottom: 10px;">Core Expertise & Verified Skills</h3>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">GoHighLevel SaaS Mode</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">Sub-Accounts & Snapshots</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">n8n Workflow Automation</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">Speed-to-Lead Workflows</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">Sales Funnel Architecture</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">REST APIs & Webhooks</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">Twilio & LC Phone</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">OpenAI / Anthropic APIs</span>
            <span class="skill-tag-pill" style="font-size: 0.76rem; padding: 4px 10px;">React.js & Tailwind CSS</span>
          </div>

          <h3 style="font-size: 1rem; font-weight: 700; color: var(--text-main); margin-bottom: 10px;">Portfolio & Artifacts</h3>
          <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="btn-card-apply" style="padding: 9px 18px;">
              🌐 View Live Portfolio
            </a>
            <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="btn-card-save" style="padding: 9px 18px;">
              📄 Download Resume
            </a>
            <a href="https://drive.google.com/file/d/1TH4CMzXFOfup2liGESZmmA7QFM8GcfqP/view?usp=sharing" target="_blank" class="btn-card-save" style="padding: 9px 18px;">
              🎥 Intro Video
            </a>
          </div>
        </div>
      </div>

    </main>

  </div>

  <!-- Slide-Over Job Drawer -->
  <div class="drawer-backdrop" id="drawerBackdrop"></div>
  <aside class="job-drawer" id="jobDrawer" aria-label="Job Detail Drawer">
    <div class="drawer-header">
      <div style="font-size: 0.78rem; font-weight: 800; color: var(--forest-green); text-transform: uppercase; letter-spacing: 0.06em;">
        GHL OPPORTUNITY BREAKDOWN
      </div>
      <button class="drawer-close-btn" id="drawerCloseBtn" aria-label="Close Drawer">✕</button>
    </div>

    <div class="drawer-body">
      <div class="drawer-title-box">
        <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;" id="drawerCompany">Company</div>
        <h3 id="drawerJobTitle">Job Title</h3>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
          <div class="stat-large-num" id="drawerScoreNum" style="font-size: 1.25rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: var(--forest-green);">--%</div>
          <span style="font-size: 0.8rem; font-weight: 700; background: var(--neon-lime-subtle); color: var(--forest-green); padding: 2px 8px; border-radius: var(--radius-xs); border: 1px solid var(--neon-lime-border);" id="drawerScoreCat">Match</span>
        </div>
      </div>

      <div class="drawer-meta-grid">
        <div class="drawer-meta-item">
          <div class="meta-k">Location</div>
          <div class="meta-v" id="drawerLocation">Worldwide Remote</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">Work Mode</div>
          <div class="meta-v" id="drawerWorkMode">100% Remote</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">Compensation</div>
          <div class="meta-v" id="drawerSalary">Competitive</div>
        </div>
        <div class="drawer-meta-item">
          <div class="meta-k">Experience</div>
          <div class="meta-v" id="drawerExp">3+ Years</div>
        </div>
        <div class="drawer-meta-item" style="grid-column: span 2;">
          <div class="meta-k">Published Date</div>
          <div class="meta-v" id="drawerPosted">Recent</div>
        </div>
      </div>

      <div class="drawer-section-title">WHY THIS MATCHES SOHAIB'S PROFILE</div>
      <p style="font-size: 0.84rem; color: #374151; line-height: 1.5; margin-bottom: 18px;" id="drawerWhy"></p>

      <div class="drawer-section-title">7-DIMENSION MATCH BREAKDOWN</div>
      <div class="drawer-breakdown-box" id="drawerScoreBreakdown"></div>

      <div class="drawer-section-title">VERIFIED MATCHING SKILLS</div>
      <div class="card-skills-row" id="drawerMatchedSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">MISSING / BONUS QUALIFICATIONS</div>
      <div class="card-skills-row" id="drawerMissingSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">ADVANTAGE HIGHLIGHTS</div>
      <div class="card-skills-row" id="drawerAdvSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">POTENTIAL CONSIDERATIONS</div>
      <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.45; margin-bottom: 20px;" id="drawerConcerns"></p>
    </div>

    <div class="drawer-footer">
      <div>
        <select class="card-status-dropdown" id="drawerStatusSelect" style="height: 38px; padding: 0 10px; font-size: 0.78rem;">
          <option value="New Match">New Match</option>
          <option value="Saved">Saved</option>
          <option value="Applied">Applied</option>
          <option value="Interview Scheduled">Interview Scheduled</option>
          <option value="Offer">Offer</option>
          <option value="Closed">Closed</option>
        </select>
      </div>

      <div style="display: flex; gap: 8px;">
        <button id="drawerMarkAppliedBtn" class="btn-card-save" style="padding: 8px 14px;">
          ✓ Mark Applied
        </button>
        <a id="drawerApplyBtn" href="#" target="_blank" class="btn-card-apply" style="padding: 8px 18px; font-size: 0.82rem;">
          Apply Directly →
        </a>
      </div>
    </div>
  </aside>

  <script src="./assets/js/app.js"></script>
</body>
</html>
"""

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(index_html)

print("✓ index.html successfully compiled with full-page Jobi SaaS architecture and vector SVG icons.")
