#!/usr/bin/env python3
"""
Gemini Spark — Multi-Page SaaS Career Intelligence Portal Builder
Compiles the complete Phase 3 web application with 7 dedicated pages:
1. Dashboard (/ or #dashboard)
2. All Jobs (/jobs or #jobs)
3. New Matches (/matches or #matches)
4. Saved Jobs (/saved or #saved)
5. Applied Jobs / Application Tracker (/applied or #applied)
6. My Resume (/resume or #resume)
7. Portfolio (/portfolio or #portfolio)

Includes vector SVG icons, embedded CSS for instant 100% styling on GitHub Pages,
Chart.js visualization, Compare Jobs modal, and slide-over AI detail drawer.
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
  <title>jobi | Gemini Spark GoHighLevel Job Intelligence Portal</title>
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

  <!-- Fullscreen App Shell -->
  <div class="app-shell">

    <!-- Global Left Sidebar -->
    <aside class="sidebar" aria-label="Portal Navigation">
      <div>
        <!-- Brand Logo -->
        <div class="sidebar-brand-row">
          <div class="brand-dot-logo"></div>
          <div class="brand-title-text">jobi</div>
        </div>

        <!-- Candidate Profile Header -->
        <div class="sidebar-user-box">
          <div class="sidebar-avatar">SM</div>
          <div class="sidebar-user-name">
            <span>Sohaib Mahmood</span>
            <svg class="svg-icon" style="width: 12px; height: 12px;" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </div>
          <div class="sidebar-user-role">GoHighLevel Developer</div>
        </div>

        <!-- Primary Navigation Menu (Phase 3 Spec) -->
        <nav class="sidebar-nav-group">
          <!-- 1. Dashboard -->
          <button class="nav-link-btn active" data-route="dashboard">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
            <span>Dashboard</span>
          </button>

          <!-- 2. All Jobs -->
          <button class="nav-link-btn" data-route="jobs">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            <span>All Jobs</span>
            <span class="nav-counter-pill" id="cntSidebarAllJobs">11</span>
          </button>

          <!-- 3. New Matches -->
          <button class="nav-link-btn" data-route="matches">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>New Matches</span>
            <span class="nav-counter-pill" id="cntSidebarNewMatches">11</span>
          </button>

          <!-- 4. Saved Jobs -->
          <button class="nav-link-btn" data-route="saved">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            <span>Saved Jobs</span>
            <span class="nav-counter-pill" id="cntSidebarSaved">0</span>
          </button>

          <!-- 5. Applied Jobs (Application Tracker) -->
          <button class="nav-link-btn" data-route="applied">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>Applied Jobs</span>
            <span class="nav-counter-pill" id="cntSidebarApplied">0</span>
          </button>

          <!-- 6. My Resume -->
          <button class="nav-link-btn" data-route="resume">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            <span>My Resume</span>
          </button>

          <!-- 7. Portfolio -->
          <button class="nav-link-btn" data-route="portfolio">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
            <span>Portfolio</span>
          </button>
        </nav>
      </div>

      <!-- Sidebar Bottom -->
      <div class="sidebar-footer">
        <div class="fit-progress-box">
          <div class="fit-progress-header">
            <span>Profile Match Fit</span>
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

    <!-- Main Viewport (Multi-Page Content Area) -->
    <main class="main-viewport">

      <!-- Global Top Navbar -->
      <header class="top-navbar">
        <div class="top-nav-links">
          <a href="#dashboard" class="top-nav-link active" data-route="dashboard">Dashboard</a>
          <a href="#jobs" class="top-nav-link" data-route="jobs">All Jobs</a>
          <a href="#matches" class="top-nav-link" data-route="matches">New Matches</a>
          <a href="#applied" class="top-nav-link" data-route="applied">Tracker</a>
          <a href="#resume" class="top-nav-link" data-route="resume">Resume</a>
          <a href="#portfolio" class="top-nav-link" data-route="portfolio">Portfolio</a>
        </div>

        <div class="top-right-group">
          <!-- Global Search Pill -->
          <div class="search-pill-wrap">
            <svg class="search-svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" id="globalSearchInput" class="search-pill-input" placeholder="Search GHL jobs, skills...">
          </div>

          <!-- History snapshot selector -->
          <select id="dateSelect" class="date-select-pill" title="History Snapshots">
            <option value="latest">Today</option>
          </select>

          <!-- ⚡ Scrape New Jobs Button -->
          <button id="btnScrapeJobs" class="btn-scrape-cta" title="Scrape & refresh GoHighLevel jobs in real-time">
            <svg class="svg-icon" style="width: 14px; height: 14px; stroke: #ffffff; fill: none;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>Scrape New Jobs</span>
          </button>
        </div>
      </header>

      <!-- ====================================================================
           PAGE 1: DASHBOARD (Intelligence Overview)
           ==================================================================== -->
      <section class="view-content" id="page-dashboard">
        <!-- Dashboard Header -->
        <div class="view-heading-row">
          <div>
            <div style="font-size: 0.72rem; font-weight: 800; color: var(--forest-green); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px;">
              GEMINI SPARK • AI JOB INTELLIGENCE
            </div>
            <h1 class="view-main-title">Dashboard</h1>
            <p class="view-subtitle">
              Candidate: <strong>Sohaib Mahmood</strong> • Focus: <strong>GoHighLevel & CRM Automation</strong>
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="live-badge-box" id="dashLiveBadge">
              <span class="live-dot-pulse"></span> LIVE 3H REFRESH
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">
              Next: <span id="dashCountdown" style="font-weight: 800; font-family: monospace; color: var(--forest-green);">--:--:--</span>
            </div>
          </div>
        </div>

        <!-- 4 Metric Cards -->
        <div class="stat-cards-container" aria-label="Key Search Metrics">
          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="dashFreshJobs">07</div>
              <div class="stat-sub-label">Fresh GHL Jobs (0–7D)</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
          </div>

          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="dashNewJobs">03</div>
              <div class="stat-sub-label">New Discovered</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
          </div>

          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="dashTotalJobs">11</div>
              <div class="stat-sub-label">Active Opportunities</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            </div>
          </div>

          <div class="jobi-stat-card">
            <div class="stat-left-text">
              <div class="stat-large-num" id="dashTopMatch">98%</div>
              <div class="stat-sub-label">Top Fit Score</div>
            </div>
            <div class="stat-lime-circle">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
          </div>
        </div>

        <!-- Middle Section: Chart & Top Matches -->
        <div class="analytics-two-col">
          <!-- Left: Match Velocity Chart -->
          <div class="white-panel-box">
            <div class="panel-title-bar">
              <div>
                <div class="panel-heading">Job Match Velocity</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">
                  GHL opportunity frequency & match concentration
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
              <canvas id="dashViewsChart"></canvas>
            </div>
          </div>

          <!-- Right: Top Strategic GHL Focus -->
          <div class="white-panel-box">
            <div class="panel-title-bar">
              <div class="panel-heading">Top GHL Focus</div>
              <span style="font-size: 0.72rem; font-weight: 700; color: var(--forest-green);">PRIORITY 1</span>
            </div>

            <div class="mini-top-list" id="dashTopMatchesList">
              <!-- Populated dynamically -->
            </div>
          </div>
        </div>

        <!-- Freshest Opportunities Preview with CTA to All Jobs -->
        <div class="white-panel-box">
          <div class="panel-title-bar">
            <div>
              <div class="panel-heading">Freshest GHL Discoveries</div>
              <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">
                Top 4 highest priority fresh listings (0–3 days old)
              </div>
            </div>
            <button class="btn-scrape-cta" onclick="navigateTo('jobs')">
              <span>View All Jobs →</span>
            </button>
          </div>

          <div class="job-cards-grid" id="dashFreshGrid">
            <!-- Populated dynamically -->
          </div>
        </div>
      </section>

      <!-- ====================================================================
           PAGE 2: ALL JOBS (Main Database with Comprehensive Filter Toolbar)
           ==================================================================== -->
      <section class="view-content" id="page-jobs" style="display: none;">
        <!-- Header -->
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">All GoHighLevel Jobs</h1>
            <p class="view-subtitle">
              Fresh opportunities discovered across public job sources • Strict 0–7 Day Window
            </p>
          </div>

          <div id="compareBarActive" class="compare-bar-cta" style="display: none;">
            <span>Comparing <b id="compareSelectedCount">0</b> jobs</span>
            <button class="btn-launch-compare" id="btnOpenCompareModal">Compare Now →</button>
          </div>
        </div>

        <!-- Full Filter & Sort Toolbar -->
        <div class="all-jobs-toolbar">
          <div class="toolbar-upper-row">
            <div class="toolbar-controls-group">
              <!-- Freshness Filter -->
              <select id="filterFreshness" class="filter-select">
                <option value="all">Freshness: All (0–7D)</option>
                <option value="today">Today (0D)</option>
                <option value="1-3-days">1–3 Days Ago</option>
                <option value="4-7-days">4–7 Days Ago</option>
              </select>

              <!-- Match Score Filter -->
              <select id="filterMatch" class="filter-select">
                <option value="all">Match: All Scores</option>
                <option value="90">90%+ Match</option>
                <option value="80">80%+ Match</option>
                <option value="70">70%+ Match</option>
              </select>

              <!-- Work Mode Filter -->
              <select id="filterWorkMode" class="filter-select">
                <option value="all">Work Mode: All</option>
                <option value="remote">100% Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">Onsite</option>
              </select>

              <!-- Sorting -->
              <select id="sortJobsSelect" class="filter-select">
                <option value="newest">Sort: Newest First</option>
                <option value="match-desc">Sort: Highest Match</option>
                <option value="salary-desc">Sort: Highest Salary</option>
                <option value="company-az">Sort: Company A-Z</option>
              </select>
            </div>

            <!-- View Layout Toggle (Grid vs List) -->
            <div class="view-toggle-wrap">
              <button class="view-toggle-btn active" id="btnViewGrid" title="Grid View">
                <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              </button>
              <button class="view-toggle-btn" id="btnViewList" title="List View">
                <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- All Jobs Grid / List -->
        <div class="job-cards-grid" id="allJobsGrid">
          <!-- Populated dynamically -->
        </div>

        <!-- Empty State -->
        <div class="empty-state" id="allJobsEmpty" style="display: none;">
          <div class="empty-icon-wrap">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          <h3>No matching GoHighLevel jobs found</h3>
          <p>Try adjusting your search criteria or trigger a live scrape across public feeds.</p>
        </div>
      </section>

      <!-- ====================================================================
           PAGE 3: NEW MATCHES (Timeline Feed)
           ==================================================================== -->
      <section class="view-content" id="page-matches" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">New Matches</h1>
            <p class="view-subtitle">Newly discovered GoHighLevel opportunities from recent automated scans</p>
          </div>
        </div>

        <!-- Timeline Feeds -->
        <div id="matchesTimelineContainer">
          <!-- Populated dynamically -->
        </div>
      </section>

      <!-- ====================================================================
           PAGE 4: SAVED JOBS (Saved Opportunity Management)
           ==================================================================== -->
      <section class="view-content" id="page-saved" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">Saved Jobs</h1>
            <p class="view-subtitle">Personal shortlist of bookmarked GoHighLevel roles</p>
          </div>
        </div>

        <div class="job-cards-grid" id="savedJobsGrid">
          <!-- Populated dynamically -->
        </div>

        <div class="empty-state" id="savedJobsEmpty" style="display: none;">
          <div class="empty-icon-wrap">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </div>
          <h3>No saved opportunities yet</h3>
          <p>Click the bookmark icon or "☆ Save" button on any job card in All Jobs to pin it here.</p>
          <button class="btn-scrape-cta" style="margin: 0 auto; display: inline-flex;" onclick="navigateTo('jobs')">
            <span>Explore All Jobs →</span>
          </button>
        </div>
      </section>

      <!-- ====================================================================
           PAGE 5: APPLIED JOBS (Application Tracker — Kanban & Table)
           ==================================================================== -->
      <section class="view-content" id="page-applied" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">Application Tracker</h1>
            <p class="view-subtitle">Track submission stages, interviews, and offers in one unified pipeline</p>
          </div>

          <div class="view-toggle-wrap">
            <button class="view-toggle-btn active" id="btnTrackerKanban">Kanban</button>
            <button class="view-toggle-btn" id="btnTrackerTable">Table</button>
          </div>
        </div>

        <!-- Kanban Board View -->
        <div class="kanban-board-grid" id="trackerKanbanView">
          <!-- Column 1: Applied -->
          <div class="kanban-column">
            <div class="kanban-column-header">
              <div class="kanban-column-title">
                <span>Applied</span>
              </div>
              <span class="kanban-counter-badge" id="kanbanCntApplied">0</span>
            </div>
            <div class="kanban-cards-stack" id="kanbanColApplied"></div>
          </div>

          <!-- Column 2: Interview Scheduled / Active -->
          <div class="kanban-column">
            <div class="kanban-column-header">
              <div class="kanban-column-title">
                <span>Interview</span>
              </div>
              <span class="kanban-counter-badge" id="kanbanCntInterview">0</span>
            </div>
            <div class="kanban-cards-stack" id="kanbanColInterview"></div>
          </div>

          <!-- Column 3: Offer -->
          <div class="kanban-column">
            <div class="kanban-column-header">
              <div class="kanban-column-title">
                <span>Offer</span>
              </div>
              <span class="kanban-counter-badge" id="kanbanCntOffer">0</span>
            </div>
            <div class="kanban-cards-stack" id="kanbanColOffer"></div>
          </div>

          <!-- Column 4: Rejected / Closed -->
          <div class="kanban-column">
            <div class="kanban-column-header">
              <div class="kanban-column-title">
                <span>Rejected / Closed</span>
              </div>
              <span class="kanban-counter-badge" id="kanbanCntRejected">0</span>
            </div>
            <div class="kanban-cards-stack" id="kanbanColRejected"></div>
          </div>
        </div>

        <!-- Table View -->
        <div class="tracker-table-container" id="trackerTableView" style="display: none;">
          <table class="tracker-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Match Score</th>
                <th>Applied Date</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="trackerTableBody">
              <!-- Populated dynamically -->
            </tbody>
          </table>
        </div>
      </section>

      <!-- ====================================================================
           PAGE 6: MY RESUME (Resume Intelligence Center)
           ==================================================================== -->
      <section class="view-content" id="page-resume" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">My Resume Intelligence</h1>
            <p class="view-subtitle">ATS readiness score, GHL keyword density, and market alignment</p>
          </div>

          <div style="display: flex; gap: 10px;">
            <button class="btn-scrape-cta" id="btnAnalyzeResumeAgainstFeed">
              <svg class="svg-icon" style="width: 14px; height: 14px; stroke: #ffffff; fill: none;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              <span>Analyze Against Current Jobs</span>
            </button>
            <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="btn-card-save" style="padding: 9px 16px;">
              Download PDF Resume
            </a>
          </div>
        </div>

        <div class="resume-grid-two-col">
          <!-- Left: Profile & Expertise -->
          <div style="display: flex; flex-direction: column; gap: 18px;">
            <!-- Candidate Summary Box -->
            <div class="white-panel-box">
              <div class="panel-heading" style="margin-bottom: 10px;">Executive Positioning</div>
              <p style="font-size: 0.84rem; color: var(--text-main); line-height: 1.55;">
                Senior GoHighLevel Developer and Marketing Automation Specialist with 4+ years of hands-on experience engineering high-converting sales funnels, bespoke CRM snapshot architectures, SaaS mode client sub-accounts, and complex multi-step n8n / REST API integrations.
              </p>
            </div>

            <!-- Technical Skills Matrix -->
            <div class="white-panel-box">
              <div class="panel-heading">GoHighLevel & CRM Skills Matrix</div>
              <div class="skills-matrix-grid">
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">GHL SaaS Mode & Snapshots</div>
                  <div class="skill-matrix-level">Expert • 4 Years (50+ Builds)</div>
                </div>
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">n8n & Zapier Automation</div>
                  <div class="skill-matrix-level">Expert • Complex Webhooks</div>
                </div>
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">Speed-to-Lead Workflows</div>
                  <div class="skill-matrix-level">Advanced • LC Phone & Twilio</div>
                </div>
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">Sales Funnel Architecture</div>
                  <div class="skill-matrix-level">Expert • High-Converting</div>
                </div>
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">OpenAI & AI Automation</div>
                  <div class="skill-matrix-level">Advanced • Prompt Agents</div>
                </div>
                <div class="skill-matrix-item">
                  <div class="skill-matrix-title">REST APIs & Custom Code</div>
                  <div class="skill-matrix-level">Advanced • React / Node</div>
                </div>
              </div>
            </div>

            <!-- Experience Highlights -->
            <div class="white-panel-box">
              <div class="panel-heading" style="margin-bottom: 12px;">Verified Experience Timeline</div>
              <div style="display: flex; flex-direction: column; gap: 14px;">
                <div style="border-left: 2px solid var(--forest-green); padding-left: 14px;">
                  <div style="font-size: 0.86rem; font-weight: 800; color: var(--text-main);">Lead GoHighLevel & CRM Engineer • Remote</div>
                  <div style="font-size: 0.74rem; color: var(--forest-green); font-weight: 700;">2022 — Present</div>
                  <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">Architected 50+ production client sub-accounts, custom snapshots, speed-to-lead SMS/voice cadences, and n8n webhook pipelines.</p>
                </div>
                <div style="border-left: 2px solid #cbd5e1; padding-left: 14px;">
                  <div style="font-size: 0.86rem; font-weight: 800; color: var(--text-main);">Marketing Automation & Funnel Builder • Remote</div>
                  <div style="font-size: 0.74rem; color: var(--text-muted); font-weight: 700;">2020 — 2022</div>
                  <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">Designed end-to-end client onboarding funnels, automated billing triggers, and integrated Twilio/Stripe webhooks.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: ATS Health & Alignment Card -->
          <div style="display: flex; flex-direction: column; gap: 18px;">
            <div class="resume-health-card">
              <div>
                <div style="font-size: 0.76rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.9;">
                  ATS Resume Readiness
                </div>
                <div class="resume-metric-row">
                  <div class="resume-score-huge">94%</div>
                  <div style="font-size: 0.78rem; line-height: 1.4; opacity: 0.9;">
                    High ATS Parse Rate<br><b>Tier 1 GoHighLevel Alignment</b>
                  </div>
                </div>
              </div>

              <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 14px;">
                <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 6px;">Keyword Density in Discovered Jobs:</div>
                <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                  <span style="background: rgba(203, 243, 47, 0.2); color: var(--neon-lime); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 4px;">GoHighLevel (100%)</span>
                  <span style="background: rgba(203, 243, 47, 0.2); color: var(--neon-lime); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 4px;">Automation (95%)</span>
                  <span style="background: rgba(203, 243, 47, 0.2); color: var(--neon-lime); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 4px;">Snapshots (90%)</span>
                  <span style="background: rgba(203, 243, 47, 0.2); color: var(--neon-lime); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 4px;">n8n (88%)</span>
                </div>
              </div>
            </div>

            <!-- Links Card -->
            <div class="white-panel-box">
              <div class="panel-heading" style="margin-bottom: 10px;">Portfolio Artifacts</div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="sidebar-sub-btn" style="color: var(--forest-green); font-weight: 700;">
                  🌐 Live Portfolio Website →
                </a>
                <a href="https://drive.google.com/file/d/1TH4CMzXFOfup2liGESZmmA7QFM8GcfqP/view?usp=sharing" target="_blank" class="sidebar-sub-btn" style="color: var(--forest-green); font-weight: 700;">
                  🎥 Video Introduction (Google Drive) →
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ====================================================================
           PAGE 7: PORTFOLIO (Visual Project Showcase)
           ==================================================================== -->
      <section class="view-content" id="page-portfolio" style="display: none;">
        <div class="view-heading-row">
          <div>
            <h1 class="view-main-title">Project Portfolio</h1>
            <p class="view-subtitle">Live GoHighLevel snapshot builds, automated CRM systems, and AI workflows</p>
          </div>

          <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="btn-scrape-cta">
            <span>Visit Full Portfolio →</span>
          </a>
        </div>

        <div class="portfolio-grid-deck">
          <!-- Project 1 -->
          <article class="portfolio-card-item">
            <div class="portfolio-banner-preview">
              <span class="portfolio-badge-pill">GHL SaaS Mode</span>
              <div style="font-size: 1.1rem; font-weight: 800;">Real Estate Agency Snapshot</div>
              <div style="font-size: 0.74rem; opacity: 0.9;">End-to-end multi-agent sub-account architecture</div>
            </div>
            <div class="portfolio-card-body">
              <p class="portfolio-project-desc">
                Engineered a comprehensive real estate snapshot featuring automated buyer/seller intake funnels, 5-minute speed-to-lead SMS followup cadences, and automated calendar booking.
              </p>
              <div class="portfolio-tools-row">
                <span class="skill-tag-pill">GoHighLevel</span>
                <span class="skill-tag-pill">LC Phone</span>
                <span class="skill-tag-pill">Funnels</span>
                <span class="skill-tag-pill">Calendars</span>
              </div>
              <div style="display: flex; gap: 8px;">
                <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="btn-card-apply" style="flex: 1; text-align: center;">Live Demo</a>
              </div>
            </div>
          </article>

          <!-- Project 2 -->
          <article class="portfolio-card-item">
            <div class="portfolio-banner-preview" style="background: linear-gradient(135deg, #1e3a8a, #1e40af);">
              <span class="portfolio-badge-pill">n8n + OpenAI</span>
              <div style="font-size: 1.1rem; font-weight: 800;">AI Lead Qualification Agent</div>
              <div style="font-size: 0.74rem; opacity: 0.9;">Autonomous WhatsApp & SMS conversion bot</div>
            </div>
            <div class="portfolio-card-body">
              <p class="portfolio-project-desc">
                Developed an autonomous AI agent integrated into GHL sub-accounts that qualifies incoming leads via conversational SMS, updates custom fields, and triggers calendar links.
              </p>
              <div class="portfolio-tools-row">
                <span class="skill-tag-pill">n8n</span>
                <span class="skill-tag-pill">OpenAI API</span>
                <span class="skill-tag-pill">GHL Webhooks</span>
                <span class="skill-tag-pill">Twilio</span>
              </div>
              <div style="display: flex; gap: 8px;">
                <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="btn-card-apply" style="flex: 1; text-align: center;">Live Demo</a>
              </div>
            </div>
          </article>

          <!-- Project 3 -->
          <article class="portfolio-card-item">
            <div class="portfolio-banner-preview" style="background: linear-gradient(135deg, #701a75, #86198f);">
              <span class="portfolio-badge-pill">Clinic & Healthcare</span>
              <div style="font-size: 1.1rem; font-weight: 800;">MedSpa Automated Booking System</div>
              <div style="font-size: 0.74rem; opacity: 0.9;">Patient scheduling, reminders & payment triggers</div>
            </div>
            <div class="portfolio-card-body">
              <p class="portfolio-project-desc">
                Built an HIPAA-compliant patient acquisition engine with deposit payment collection via Stripe, two-way SMS confirmation reminders, and automated review generation.
              </p>
              <div class="portfolio-tools-row">
                <span class="skill-tag-pill">GHL Funnels</span>
                <span class="skill-tag-pill">Stripe</span>
                <span class="skill-tag-pill">Workflows</span>
                <span class="skill-tag-pill">Review Engine</span>
              </div>
              <div style="display: flex; gap: 8px;">
                <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="btn-card-apply" style="flex: 1; text-align: center;">Live Demo</a>
              </div>
            </div>
          </article>
        </div>
      </section>

    </main>

  </div>

  <!-- ====================================================================
       AI JOB COMPARISON MODAL
       ==================================================================== -->
  <div class="modal-backdrop" id="compareModalBackdrop"></div>
  <div class="compare-modal-box" id="compareModalBox" role="dialog" aria-label="Compare Jobs">
    <div class="compare-modal-header">
      <div>
        <div style="font-size: 0.74rem; font-weight: 800; color: var(--forest-green); text-transform: uppercase;">
          AI JOB COMPARISON
        </div>
        <h3 style="font-size: 1.15rem; font-weight: 800; color: var(--text-main);">Side-by-Side Evaluation</h3>
      </div>
      <button class="drawer-close-btn" id="compareCloseBtn">✕</button>
    </div>
    <div class="compare-modal-body" id="compareModalBody">
      <!-- Populated dynamically -->
    </div>
  </div>

  <!-- ====================================================================
       SLIDE-OVER JOB DETAIL DRAWER (With AI Match Analysis)
       ==================================================================== -->
  <div class="drawer-backdrop" id="drawerBackdrop"></div>
  <aside class="job-drawer" id="jobDrawer" aria-label="Job Detail Drawer">
    <div class="drawer-header">
      <div style="font-size: 0.78rem; font-weight: 800; color: var(--forest-green); text-transform: uppercase; letter-spacing: 0.06em;">
        AI MATCH ANALYSIS
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

      <div class="drawer-section-title">APPLICATION STRATEGY & CONSIDERATIONS</div>
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

print("✓ index.html successfully compiled with Phase 3 Multi-Page Architecture.")
