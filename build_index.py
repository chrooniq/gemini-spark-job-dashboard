import json

with open("/working_dir/c_f852dfa8ed7d66d6/gemini-spark-job-dashboard/data/latest.json", "r", encoding="utf-8") as f:
    latest_json_str = f.read()

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Spark | Live Job Intelligence Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./assets/css/style.css">
  <script>
    // Embedded fallback store for direct file:// browser viewing
    window.FALLBACK_DATA = {latest_json_str};
  </script>
</head>
<body>

  <!-- Top Navigation Bar -->
  <nav class="navbar">
    <div class="app-container nav-wrapper">
      <div class="brand-section">
        <div class="brand-logo">⚡</div>
        <div class="brand-text">
          <h1>Gemini Spark</h1>
          <p>AI Career Intelligence & Live Job Match Portal</p>
        </div>
      </div>

      <div class="nav-actions">
        <!-- Date Selector for History -->
        <div class="date-selector-wrap">
          <span class="date-selector-label">Date:</span>
          <select id="dateSelect" class="date-select" title="Switch Report Date">
            <option value="latest">Today (2026-08-19)</option>
          </select>
        </div>

        <a href="https://sohaibmahmood.vibepreview.com/" target="_blank" class="nav-btn primary">
          <span>🌐 Portfolio</span>
        </a>
        <a href="https://drive.google.com/file/d/1TH4CMzXFOfup2liGESZmmA7QFM8GcfqP/view?usp=sharing" target="_blank" class="nav-btn">
          <span>🎥 Video</span>
        </a>
        <a href="https://drive.google.com/file/d/1wCat1irNe710A_9gWgVQ0h0ljtbX_c2k/view?usp=drivesdk" target="_blank" class="nav-btn">
          <span>📄 Resume</span>
        </a>
        <a href="https://drive.google.com/file/d/12mjATUvsDO6KQS20w_1MOAevmG41T0vV/view?usp=drivesdk" target="_blank" class="nav-btn">
          <span>📊 Excel</span>
        </a>
      </div>
    </div>
  </nav>

  <main class="app-container">
    
    <!-- Hero Profile Section -->
    <section class="hero-section">
      <div class="candidate-card">
        <div class="candidate-profile">
          <div class="avatar">SM</div>
          <div class="candidate-info">
            <h2>Sohaib Mahmood</h2>
            <p id="candidateTitle">GoHighLevel Developer | CRM & Marketing Automation | Funnel & Website Builder</p>
          </div>
        </div>

        <div class="candidate-pills">
          <span class="c-pill live-badge"><span class="live-dot"></span> 100% Worldwide Remote</span>
          <span class="c-pill">📍 Lahore, Pakistan (UTC+5)</span>
          <span class="c-pill">⏱ 4 Years Experience (50+ Builds)</span>
          <span class="c-pill" id="searchDateBadge">2026-08-19</span>
        </div>
      </div>

      <!-- KPI Metrics Row -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Qualified Jobs</span>
            <div class="kpi-icon icon-blue">🎯</div>
          </div>
          <div class="kpi-value" id="kpiDiscovered">14</div>
          <div class="kpi-foot">✓ Verified Active</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Highest Match</span>
            <div class="kpi-icon icon-green">🔥</div>
          </div>
          <div class="kpi-value" id="kpiTopMatch" style="color: var(--emerald);">98%</div>
          <div class="kpi-foot">Top Fit Score</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Average Match</span>
            <div class="kpi-icon icon-blue">📈</div>
          </div>
          <div class="kpi-value" id="kpiAvgMatch">89.1%</div>
          <div class="kpi-foot">Weighted Average</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Priority 1 (Apply)</span>
            <div class="kpi-icon icon-green">⚡</div>
          </div>
          <div class="kpi-value" id="kpiPriority1" style="color: #991b1b;">13</div>
          <div class="kpi-foot">Immediate Action</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Remote Eligible</span>
            <div class="kpi-icon icon-purple">🌍</div>
          </div>
          <div class="kpi-value" id="kpiRemotePct">100%</div>
          <div class="kpi-foot">Pakistan Compatible</div>
        </div>
      </div>
    </section>

    <!-- Navigation Tabs -->
    <div class="dashboard-tabs">
      <button class="tab-btn active" data-tab="all">
        All Ranked Opportunities <span class="tab-badge" id="visibleCount">14</span>
      </button>
      <button class="tab-btn" data-tab="top5">
        Top 5 Strategic Focus <span class="tab-badge" style="background: var(--emerald-subtle); color: var(--emerald);">5</span>
      </button>
      <button class="tab-btn" data-tab="intelligence">
        Market & Skill Intelligence <span>🧠</span>
      </button>
    </div>

    <!-- Section: Jobs List & Filters -->
    <section id="jobsSection">
      <!-- Search & Filter Controls -->
      <div class="control-hub">
        <div class="search-bar-row">
          <div class="search-box-wrap">
            <span class="search-box-icon">🔍</span>
            <input type="text" id="searchBox" class="search-box" placeholder="Search by job title, company, skills, or platform...">
          </div>

          <div class="sort-select-wrap">
            <select id="sortSelect" class="custom-select" aria-label="Sort Order">
              <option value="score-desc">Match Score (Highest First)</option>
              <option value="score-asc">Match Score (Lowest First)</option>
              <option value="rank-asc">Rank (1 to 14)</option>
              <option value="title-asc">Job Title (A–Z)</option>
              <option value="company-asc">Company (A–Z)</option>
            </select>
          </div>
        </div>

        <!-- Filter Chips: Role Focus -->
        <div class="filter-chips-row">
          <span class="filter-group-label">Role Focus:</span>
          <button class="chip active" data-filter-type="role" data-filter="all">All Roles</button>
          <button class="chip" data-filter-type="role" data-filter="ghl">GoHighLevel / CRM (8)</button>
          <button class="chip" data-filter-type="role" data-filter="automation">n8n & Workflows (4)</button>
          <button class="chip" data-filter-type="role" data-filter="ai">AI Systems (2)</button>
          <button class="chip" data-filter-type="role" data-filter="funnels">Funnels & Web</button>
        </div>

        <!-- Filter Chips: Priority -->
        <div class="filter-chips-row" style="margin-top: 10px;">
          <span class="filter-group-label">Priority:</span>
          <button class="chip active" data-filter-type="prio" data-filter="all">All Priorities</button>
          <button class="chip" data-filter-type="prio" data-filter="prio-apply">🔥 Priority 1 — Apply (13)</button>
          <button class="chip" data-filter-type="prio" data-filter="prio-consider">🟢 Priority 2 — Consider (1)</button>
        </div>

        <!-- Filter Chips: Status -->
        <div class="filter-chips-row" style="margin-top: 10px;">
          <span class="filter-group-label">Application Status:</span>
          <button class="chip active" data-filter-type="status" data-filter="all">All</button>
          <button class="chip" data-filter-type="status" data-filter="New Match">New Match</button>
          <button class="chip" data-filter-type="status" data-filter="Saved">Saved</button>
          <button class="chip" data-filter-type="status" data-filter="Applied">Applied</button>
          <button class="chip" data-filter-type="status" data-filter="Interview Scheduled">Interview Scheduled</button>
        </div>
      </div>

      <!-- Job Cards Container -->
      <div class="jobs-container" id="jobsContainer"></div>

      <div id="emptyState" style="display: none; text-align: center; padding: 48px 24px; background: #ffffff; border-radius: 12px; border: 1px dashed var(--border-light);">
        <h4 style="color: var(--navy); font-size: 1.1rem; margin-bottom: 6px;">No matching opportunities found</h4>
        <p style="color: var(--text-muted); font-size: 0.88rem;">Try clearing your search query or resetting the filter options.</p>
      </div>
    </section>

    <!-- Section: Market & Skill Intelligence -->
    <section id="intelligenceSection" style="display: none;">
      <div class="intelligence-grid">
        <!-- Most in-demand skills -->
        <div class="intel-card">
          <div class="intel-card-header">🔥 Most In-Demand Skills Today</div>
          <div id="demandSkillsContainer"></div>
        </div>

        <!-- Career Quadrants -->
        <div class="intel-card">
          <div class="intel-card-header">🧭 Career Strategy Matrix</div>
          <div class="quadrant-grid">
            <div class="quadrant-box keep">
              <div class="quadrant-title">✅ Keep Doing</div>
              <ul class="quadrant-list">
                <li>GHL SaaS & Snapshots</li>
                <li>n8n Workflow Design</li>
                <li>Speed-to-lead Workflows</li>
                <li>50+ Funnel Portfolio</li>
              </ul>
            </div>
            <div class="quadrant-box improve">
              <div class="quadrant-title">🔧 Improve</div>
              <ul class="quadrant-list">
                <li>Webhook retry SOPs</li>
                <li>React Dashboard demo</li>
                <li>Affiliate commission logic</li>
              </ul>
            </div>
            <div class="quadrant-box learn">
              <div class="quadrant-title">📚 Learn</div>
              <ul class="quadrant-list">
                <li>WhatsApp Cloud API</li>
                <li>Docker for self-hosted n8n</li>
                <li>Basic Python for APIs</li>
              </ul>
            </div>
            <div class="quadrant-box watch">
              <div class="quadrant-title">👀 Watch</div>
              <ul class="quadrant-list">
                <li>AI Agent tool connectors</li>
                <li>Model Context Protocol</li>
                <li>OpenAI Assistants API</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>

  <footer class="app-footer">
    <div class="app-container">
      <p><strong>Gemini Spark AI Career Intelligence</strong> • Automated Daily Job Matching System</p>
      <p style="margin-top: 4px; font-size: 0.76rem; color: #94a3b8;">
        Built for Sohaib Mahmood • Lahore, Pakistan (UTC+5) • 100% Worldwide Remote Career Hub
      </p>
    </div>
  </footer>

  <script src="./assets/js/app.js"></script>
</body>
</html>
"""

with open("/working_dir/c_f852dfa8ed7d66d6/gemini-spark-job-dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

print("index.html successfully built.")
