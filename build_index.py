#!/usr/bin/env python3
"""
Gemini Spark — HTML Index Builder
Compiles the "Jobi" styled Dashboard matching the reference design layout:
Soft Sage Canvas, Crisp White Panels, Forest Green Accents, and Neon Lime Badges.
Embeds full CSS directly in <style> to prevent any unstyled flash on GitHub Pages.
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
  <title>jobi | Gemini Spark GHL Job Intelligence Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="./assets/css/style.css">
  <style>
{embedded_css}
  </style>
  <script>
    // Embedded fallback store for direct file:// and static server viewing
    window.FALLBACK_DATA = {latest_json_str};
  </script>
</head>
<body>

  <!-- Outer Dashboard Frame (Jobi Style) -->
  <div class="dashboard-wrapper">

    <!-- Left Sidebar -->
    <aside class="app-sidebar">
      <div class="sidebar-top">
        <!-- Logo -->
        <div class="brand-header">
          <div class="brand-dot-icon"></div>
          <div class="brand-name">jobi</div>
        </div>

        <!-- Candidate Profile -->
        <div class="user-profile-widget">
          <div class="user-avatar-circle">SM</div>
          <div class="user-name-box">
            <span>Sohaib Mahmood</span>
            <span>▾</span>
          </div>
          <div class="user-role-sub">GHL & CRM Developer</div>
        </div>

        <!-- Navigation Menu -->
        <nav class="sidebar-menu" aria-label="Sidebar Navigation">
          <button class="nav-item-btn active" data-nav-target="all-active">
            <span class="nav-icon">📊</span>
            <span>Dashboard</span>
            <span class="nav-badge-pill" id="cntSidebarActive">11</span>
          </button>
          <button class="nav-item-btn" data-nav-target="New Match">
            <span class="nav-icon">⚡</span>
            <span>New Matches</span>
            <span class="nav-badge-pill" id="cntSidebarNew">11</span>
          </button>
          <button class="nav-item-btn" data-nav-target="Saved">
            <span class="nav-icon">★</span>
            <span>Saved Jobs</span>
            <span class="nav-badge-pill" id="cntSidebarSaved">0</span>
          </button>
          <button class="nav-item-btn" data-nav-target="Applied">
            <span class="nav-icon">✓</span>
            <span>Applied Jobs</span>
            <span class="nav-badge-pill" id="cntSidebarApplied">0</span>
          </button>
          <button class="nav-item-btn" data-nav-target="Interview Scheduled">
            <span class="nav-icon">💬</span>
            <span>Interviews</span>
            <span class="nav-badge-pill" id="cntSidebarInterview">0</span>
          </button>
          <button class="nav-item-btn" data-nav-target="all">
            <span class="nav-icon">📁</span>
            <span>All Records</span>
            <span class="nav-badge-pill" id="cntSidebarAll">11</span>
          </button>
        </nav>
      </div>

      <!-- Sidebar Bottom Completion Box -->
      <div class="sidebar-bottom">
        <div class="profile-completion-box">
          <div class="completion-header">
            <span>Profile Fit</span>
            <span class="completion-pct">87%</span>
          </div>
          <div class="completion-track">
            <div class="completion-fill" style="width: 87%;"></div>
          </div>
        </div>

        <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="sidebar-exit-btn">
          <span>🌐</span> View Portfolio
        </a>
      </div>
    </aside>

    <!-- Main Viewport -->
    <main class="app-main-content">

      <!-- Top Nav Bar -->
      <header class="main-top-navbar">
        <div class="main-nav-links">
          <a href="#" class="main-nav-link active">Home</a>
          <a href="#" class="main-nav-link">GHL Jobs</a>
          <a href="#" class="main-nav-link">Pipeline</a>
          <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="main-nav-link">Resume</a>
          <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="main-nav-link">Portfolio</a>
        </div>

        <div class="top-right-actions">
          <div class="top-search-wrap">
            <span class="top-search-icon">🔍</span>
            <input type="text" id="topSearchField" class="top-search-input" placeholder="Search GHL jobs...">
          </div>

          <div class="icon-circle-btn" title="Snapshot History Date">
            <select id="dateSelect" style="border: none; background: transparent; font-size: 0.72rem; font-weight: 700; color: var(--forest-green); cursor: pointer;" title="History snapshots">
              <option value="latest">Today</option>
            </select>
          </div>

          <button id="btnScrapeJobs" class="btn-post-job" title="Scrape & refresh GoHighLevel jobs in real-time">
            <span>⚡</span> Scrape New Jobs
          </button>
        </div>
      </header>

      <!-- Dashboard Body -->
      <div class="dashboard-content-body">

        <!-- Title & Status Row -->
        <div class="dashboard-title-row">
          <div>
            <h1 class="dashboard-title">Dashboard</h1>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
              GoHighLevel & CRM Automation Intelligence • Candidate: <strong>Sohaib Mahmood</strong>
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="live-status-pill" id="headerStatusBadge">
              <span class="status-dot"></span> LIVE 3H REFRESH
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">
              Next: <span id="nextUpdateCountdown" style="font-weight: 800; font-family: monospace; color: var(--forest-green);">--:--:--</span>
            </div>
          </div>
        </div>

        <!-- 4 Top Stat Cards (Exact Jobi Layout) -->
        <section class="stat-cards-grid" aria-label="Key Performance Indicators">
          <!-- Card 1: Fresh Jobs -->
          <div class="stat-card-jobi">
            <div class="stat-card-left">
              <div class="stat-num" id="statFreshJobs">07</div>
              <div class="stat-lbl">Fresh GHL Jobs (0–7D)</div>
            </div>
            <div class="stat-lime-badge">👤</div>
          </div>

          <!-- Card 2: New Matches -->
          <div class="stat-card-jobi">
            <div class="stat-card-left">
              <div class="stat-num" id="statNewJobs">03</div>
              <div class="stat-lbl">New Discovered</div>
            </div>
            <div class="stat-lime-badge">🔖</div>
          </div>

          <!-- Card 3: Total Discoveries -->
          <div class="stat-card-jobi">
            <div class="stat-card-left">
              <div class="stat-num" id="statTotalJobs">11</div>
              <div class="stat-lbl">GHL Opportunities</div>
            </div>
            <div class="stat-lime-badge">🌐</div>
          </div>

          <!-- Card 4: Top Match Score -->
          <div class="stat-card-jobi">
            <div class="stat-card-left">
              <div class="stat-num" id="statTopMatch">98%</div>
              <div class="stat-lbl">Highest Match Fit</div>
            </div>
            <div class="stat-lime-badge">⚡</div>
          </div>
        </section>

        <!-- Middle Section: Chart & Recent Matches List -->
        <section class="analytics-middle-grid">
          <!-- Left: Job Views & Match Velocity Chart -->
          <div class="panel-card">
            <div class="panel-header">
              <div>
                <div class="panel-title">Job Match Intelligence</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">
                  GoHighLevel CRM & Automation Match Trajectory
                </div>
              </div>
              <div class="time-pill-group">
                <button class="time-pill" data-time-tab="day">Day</button>
                <button class="time-pill active" data-time-tab="week">Week</button>
                <button class="time-pill" data-time-tab="month">Month</button>
                <button class="time-pill" data-time-tab="all">All</button>
              </div>
            </div>

            <div class="chart-container-box">
              <canvas id="jobViewsChart"></canvas>
            </div>
          </div>

          <!-- Right: Posted / Top Strategic Matches -->
          <div class="panel-card">
            <div class="panel-header">
              <div class="panel-title">Top GHL Focus</div>
              <span style="font-size: 0.72rem; font-weight: 700; color: var(--forest-green);">★ PRIORITY 1</span>
            </div>

            <div class="recent-jobs-list" id="miniTopMatchesList">
              <!-- Dynamically populated by app.js -->
            </div>
          </div>
        </section>

        <!-- Bottom Feed Section: All Ranked GHL Opportunities -->
        <section>
          <div class="feed-section-header">
            <div>
              <h2 class="feed-heading">GoHighLevel Opportunities Feed</h2>
              <span style="font-size: 0.76rem; color: var(--text-muted);" id="feedCountBadge">11 Opportunities Available</span>
            </div>

            <!-- Filter Pills -->
            <div class="filter-pills-bar">
              <button class="filter-btn-pill active" data-filter-type="freshness" data-filter="all">All (0–7D)</button>
              <button class="filter-btn-pill" data-filter-type="freshness" data-filter="today">🔥 Today</button>
              <button class="filter-btn-pill" data-filter-type="freshness" data-filter="1-3-days">1–3 Days</button>
              <button class="filter-btn-pill" data-filter-type="freshness" data-filter="4-7-days">4–7 Days</button>
              <button class="filter-btn-pill" data-filter-type="match" data-filter="90">90%+</button>
              <button class="filter-btn-pill" data-filter-type="workmode" data-filter="remote">100% Remote</button>
            </div>
          </div>

          <!-- Job Cards Grid -->
          <div class="job-cards-deck" id="jobsGridContainer">
            <!-- Dynamically populated by app.js -->
          </div>

          <!-- Clean Empty State -->
          <div class="empty-state" id="emptyState" style="display: none;">
            <div class="empty-icon">⚡</div>
            <h3>No GoHighLevel opportunities found</h3>
            <p>
              No active roles match your current filter criteria or all listed opportunities have been processed.
            </p>
            <button id="btnEmptyScrape" class="btn-post-job" style="margin: 0 auto; display: inline-flex;">
              <span>⚡</span> Scrape New Jobs
            </button>
          </div>
        </section>

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
          <div class="stat-num" id="drawerScoreNum" style="font-size: 1.2rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: var(--forest-green);">--%</div>
          <span style="font-size: 0.8rem; font-weight: 700; background: var(--neon-lime-subtle); color: var(--forest-green); padding: 2px 8px; border-radius: var(--radius-xs); border: 1px solid var(--neon-lime-border);" id="drawerScoreCat">Match</span>
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
      <p style="font-size: 0.84rem; color: #374151; line-height: 1.5; margin-bottom: 18px;" id="drawerWhy"></p>

      <div class="drawer-section-title">7-DIMENSION MATCH BREAKDOWN</div>
      <div class="drawer-breakdown-box" id="drawerScoreBreakdown"></div>

      <div class="drawer-section-title">VERIFIED MATCHING SKILLS</div>
      <div class="jobi-skill-tags" id="drawerMatchedSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">MISSING / BONUS QUALIFICATIONS</div>
      <div class="jobi-skill-tags" id="drawerMissingSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">ADVANTAGE HIGHLIGHTS</div>
      <div class="jobi-skill-tags" id="drawerAdvSkills" style="margin-bottom: 16px;"></div>

      <div class="drawer-section-title">POTENTIAL CONSIDERATIONS</div>
      <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.45; margin-bottom: 20px;" id="drawerConcerns"></p>
    </div>

    <div class="drawer-footer">
      <div>
        <select class="jobi-status-select" id="drawerStatusSelect" style="height: 38px; padding: 0 10px; font-size: 0.78rem;">
          <option value="New Match">New Match</option>
          <option value="Saved">Saved</option>
          <option value="Applied">Applied</option>
          <option value="Interview Scheduled">Interview Scheduled</option>
          <option value="Offer">Offer</option>
          <option value="Closed">Closed</option>
        </select>
      </div>

      <div style="display: flex; gap: 8px;">
        <button id="drawerMarkAppliedBtn" class="jobi-save-btn" style="padding: 8px 14px;">
          ✓ Mark Applied
        </button>
        <a id="drawerApplyBtn" href="#" target="_blank" class="jobi-apply-btn" style="padding: 8px 18px; font-size: 0.82rem;">
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

print("✓ index.html successfully compiled with embedded CSS and Jobi layout.")
