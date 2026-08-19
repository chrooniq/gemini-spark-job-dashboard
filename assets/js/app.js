/**
 * Gemini Spark — AI Career Intelligence Dashboard Application
 * 3-Hour Refresh, Application Tracking & Dynamic LocalStorage / Static JSON Controller
 */

// Application Global State
const state = {
  currentRoute: 'dashboard',
  activeDate: 'latest',
  feedScope: 'active', // 'active' | 'processed' | 'all'
  searchQuery: '',
  roleFilter: 'all',
  prioFilter: 'all',
  statusFilter: 'all',
  sortMode: 'score-desc',
  viewMode: 'table', // 'table' | 'grid'
  data: null,
  savedStatuses: {},
  activeDrawerJobId: null,
  countdownInterval: null
};

const PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed"];

// Application Bootstrap
document.addEventListener('DOMContentLoaded', async () => {
  loadSavedStatuses();
  await loadDataset('latest');
  setupEventListeners();
  startCountdownTimer();
});

// Load persistent statuses from browser localStorage
function loadSavedStatuses() {
  try {
    const raw = localStorage.getItem('ghl_career_job_statuses');
    state.savedStatuses = raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.warn('localStorage read error:', e);
    state.savedStatuses = {};
  }
}

// Persist status change
function setJobStatus(jobId, newStatus) {
  state.savedStatuses[jobId] = newStatus;
  try {
    localStorage.setItem('ghl_career_job_statuses', JSON.stringify(state.savedStatuses));
  } catch (e) {
    console.warn('localStorage write error:', e);
  }

  if (state.data) {
    const allJobs = state.data.jobs || [];
    const target = allJobs.find(j => j.id === jobId || j.original_url === jobId || j.app_url === jobId);
    if (target) {
      target.status = newStatus;
      target.is_active = !PROCESSED_STATUSES.includes(newStatus);
    }
  }

  updateNavCounters();
  renderCurrentView();

  // If drawer is open for this job, sync its select box
  const drawerSelect = document.getElementById('drawerStatusSelect');
  if (drawerSelect && state.activeDrawerJobId === jobId) {
    drawerSelect.value = newStatus;
  }

  showToast(`Status updated to "${newStatus}"`);
}

// Fetch dataset dynamically
async function loadDataset(dateKey = 'latest') {
  const url = dateKey === 'latest' ? './data/latest.json' : `./data/history/${dateKey}.json`;

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    state.data = await res.json();
  } catch (err) {
    console.warn(`Dynamic fetch failed for ${url}. Using fallback store.`, err);
    if (window.FALLBACK_DATA) {
      state.data = window.FALLBACK_DATA;
    } else {
      console.error('No dataset available.');
      return;
    }
  }

  // Attach persistent statuses & calculate active states
  if (state.data && state.data.jobs) {
    state.data.jobs.forEach(job => {
      const key = job.original_url || job.app_url || job.id;
      const status = state.savedStatuses[key] || state.savedStatuses[job.id] || job.status || 'New Match';
      job.status = status;
      job.is_active = !PROCESSED_STATUSES.includes(status);
    });
  }

  updateHeaderMetadata();
  populateDateDropdown();
  updateNavCounters();
  renderCurrentView();
  initAnalyticsCharts();
}

// Dynamic Countdown Timer to next 3-hour PKT slot (00, 03, 06, 09, 12, 15, 18, 21 PKT)
function startCountdownTimer() {
  if (state.countdownInterval) clearInterval(state.countdownInterval);

  function update() {
    const now = new Date();
    // PKT is UTC+5
    const utcHours = now.getUTCHours();
    const utcMinutes = now.getUTCMinutes();
    const utcSeconds = now.getUTCSeconds();

    const pktHour = (utcHours + 5) % 24;
    const schedulePktHours = [0, 3, 6, 9, 12, 15, 18, 21];

    let nextPktHour = schedulePktHours.find(h => h > pktHour);
    let hoursDiff = 0;
    if (nextPktHour !== undefined) {
      hoursDiff = nextPktHour - pktHour;
    } else {
      hoursDiff = (24 - pktHour) + schedulePktHours[0];
    }

    let targetDate = new Date(now.getTime());
    targetDate.setMinutes(0, 0, 0);
    targetDate.setHours(targetDate.getHours() + hoursDiff);

    let diffMs = targetDate.getTime() - now.getTime();
    if (diffMs < 0) diffMs = 0;

    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const diffSecs = Math.floor((diffMs % (1000 * 60)) / 1000);

    const pad = (n) => String(n).padStart(2, '0');
    const countdownStr = `${pad(diffHours)}h ${pad(diffMinutes)}m ${pad(diffSecs)}s`;

    const countdownEl = document.getElementById('nextUpdateCountdown');
    if (countdownEl) countdownEl.textContent = countdownStr;
  }

  update();
  state.countdownInterval = setInterval(update, 1000);
}

// Update Header & Profile info
function updateHeaderMetadata() {
  if (!state.data || !state.data.metadata) return;
  const meta = state.data.metadata;
  const allJobs = state.data.jobs || [];

  const activeJobs = allJobs.filter(j => j.is_active);
  const newJobs = activeJobs.filter(j => j.is_new);
  const savedJobs = allJobs.filter(j => j.status === 'Saved');
  const appliedJobs = allJobs.filter(j => j.status === 'Applied');
  const interviewJobs = allJobs.filter(j => j.status.includes('Interview'));
  const offerJobs = allJobs.filter(j => j.status === 'Offer');

  // Header badges & metadata
  const lastUpdatedEl = document.getElementById('lastUpdatedBadge');
  if (lastUpdatedEl) lastUpdatedEl.textContent = meta.last_updated || `${meta.search_date} ${meta.search_time || ''}`;

  const nextJobSearchEl = document.getElementById('nextJobSearchTime');
  if (nextJobSearchEl) nextJobSearchEl.textContent = meta.next_update || 'Every 3 Hours';

  const dateBadgeEl = document.getElementById('searchDateBadge');
  if (dateBadgeEl) dateBadgeEl.textContent = meta.search_date;

  // Real-time KPI Cards
  const kNewJobs = document.getElementById('kpiNewJobs');
  if (kNewJobs) kNewJobs.textContent = newJobs.length;

  const kActive = document.getElementById('kpiActiveJobs');
  if (kActive) kActive.textContent = activeJobs.length;

  const kSaved = document.getElementById('kpiSaved');
  if (kSaved) kSaved.textContent = savedJobs.length;

  const kApplied = document.getElementById('kpiApplied');
  if (kApplied) kApplied.textContent = appliedJobs.length;

  const kInterviews = document.getElementById('kpiInterviews');
  if (kInterviews) kInterviews.textContent = interviewJobs.length;

  const kOffers = document.getElementById('kpiOffers');
  if (kOffers) kOffers.textContent = offerJobs.length;

  const kTopMatch = document.getElementById('kpiTopMatch');
  if (kTopMatch) {
    const topFit = activeJobs.length ? Math.max(...activeJobs.map(j => j.score)) : 0;
    kTopMatch.textContent = `${topFit}%`;
  }
}

// Populate Date Switcher Dropdown
function populateDateDropdown() {
  const select = document.getElementById('dateSelect');
  if (!select || !state.data || !state.data.metadata) return;

  const dates = state.data.metadata.available_dates || ['2026-08-19'];
  select.innerHTML = '';

  const optLatest = document.createElement('option');
  optLatest.value = 'latest';
  optLatest.textContent = `Today (${state.data.metadata.search_date})`;
  optLatest.selected = (state.activeDate === 'latest');
  select.appendChild(optLatest);

  dates.forEach(d => {
    if (d !== state.data.metadata.search_date) {
      const opt = document.createElement('option');
      opt.value = d;
      opt.textContent = `Snapshot: ${d}`;
      opt.selected = (state.activeDate === d);
      select.appendChild(opt);
    }
  });
}

// Update Sidebar Badge Counters
function updateNavCounters() {
  if (!state.data || !state.data.jobs) return;
  const jobs = state.data.jobs;

  const activeJobs = jobs.filter(j => j.is_active);
  const countAll = jobs.length;
  const countTop5 = activeJobs.slice(0, 5).length;
  const countSaved = jobs.filter(j => j.status === 'Saved').length;
  const countApplied = jobs.filter(j => j.status === 'Applied').length;
  const countInterview = jobs.filter(j => j.status.includes('Interview')).length;

  setCount('cntAll', countAll);
  setCount('cntActive', activeJobs.length);
  setCount('cntTop5', countTop5);
  setCount('cntSaved', countSaved);
  setCount('cntApplied', countApplied);
  setCount('cntInterviews', countInterview);
}

function setCount(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// Main View Router
function navigateTo(route) {
  state.currentRoute = route;

  // Update active class in sidebar
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-route') === route);
  });

  // Toggle visible sections
  const viewDashboard = document.getElementById('viewDashboard');
  const viewTopMatches = document.getElementById('viewTopMatches');
  const viewExplorer = document.getElementById('viewExplorer');
  const viewMarketIntel = document.getElementById('viewMarketIntel');
  const viewResumeIntel = document.getElementById('viewResumeIntel');
  const viewHistory = document.getElementById('viewHistory');
  const viewSettings = document.getElementById('viewSettings');

  // Hide all
  [viewDashboard, viewTopMatches, viewExplorer, viewMarketIntel, viewResumeIntel, viewHistory, viewSettings].forEach(v => {
    if (v) v.style.display = 'none';
  });

  if (route === 'dashboard') {
    if (viewDashboard) viewDashboard.style.display = 'block';
  } else if (route === 'top-matches') {
    if (viewTopMatches) viewTopMatches.style.display = 'block';
  } else if (['all-jobs', 'saved', 'applied', 'interviews'].includes(route)) {
    if (viewExplorer) viewExplorer.style.display = 'block';
    
    if (route === 'saved') {
      state.feedScope = 'all';
      state.statusFilter = 'Saved';
    } else if (route === 'applied') {
      state.feedScope = 'processed';
      state.statusFilter = 'Applied';
    } else if (route === 'interviews') {
      state.feedScope = 'processed';
      state.statusFilter = 'Interview Scheduled';
    } else {
      state.feedScope = 'active';
      state.statusFilter = 'all';
    }

    syncFeedScopeButtons();
    syncFilterChips();
  } else if (route === 'market-intel' || route === 'skill-gaps') {
    if (viewMarketIntel) viewMarketIntel.style.display = 'block';
  } else if (route === 'resume-intel') {
    if (viewResumeIntel) viewResumeIntel.style.display = 'block';
  } else if (route === 'history') {
    if (viewHistory) viewHistory.style.display = 'block';
  } else if (route === 'settings') {
    if (viewSettings) viewSettings.style.display = 'block';
  }

  renderCurrentView();
}

function syncFeedScopeButtons() {
  document.querySelectorAll('.feed-scope-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-scope') === state.feedScope);
  });
}

function syncFilterChips() {
  document.querySelectorAll('.filter-chip[data-filter-type="status"]').forEach(c => {
    c.classList.toggle('active', c.getAttribute('data-filter') === state.statusFilter);
  });
}

// Render Active Sub-Views
function renderCurrentView() {
  if (!state.data) return;

  renderTop5Cards();
  renderExplorer();
  renderMarketInsights();
}

// Render Top 5 Strategic Focus Cards (Excludes Applied / Processed Jobs)
function renderTop5Cards() {
  const container = document.getElementById('top5Grid');
  const fullContainer = document.getElementById('topMatchesFullGrid');
  if (!state.data || !state.data.jobs) return;

  // Top 5 from strictly ACTIVE (unapplied / saved) jobs
  const activeJobs = state.data.jobs
    .filter(j => j.is_active)
    .sort((a, b) => b.score - a.score);

  const top5 = activeJobs.slice(0, 5);

  const cardsHtml = top5.length === 0 
    ? `<div style="padding: 24px; text-align: center; color: var(--text-muted); background: #ffffff; border-radius: 12px;">All current top matches have been applied to! Check back on the next 3-hour refresh.</div>`
    : top5.map((job, idx) => {
    const badgeClass = job.score >= 90 ? 'badge-excellent' : 'badge-strong';
    const isNewBadge = job.is_new ? `<span class="new-job-badge">NEW</span>` : '';
    return `
      <article class="top5-card rank-${idx + 1}" onclick="openJobDrawer('${job.id}')">
        <div class="top5-card-header">
          <div class="top5-company-box">
            <div class="company-logo-avatar" style="background-color: ${job.company_color || '#2563eb'};">
              ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
            </div>
            <div class="company-details">
              <h4>${job.company}</h4>
              <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">${job.source}</span>
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            ${isNewBadge}
            <div class="match-ring-badge ${badgeClass}">
              ${job.score}%
              <span>${job.category.replace(' Match', '')}</span>
            </div>
          </div>
        </div>

        <h3>${job.title}</h3>

        <div class="top5-meta-pills">
          <span class="mini-pill prio-apply">${job.priority_icon || '🔥'} ${(job.priority || 'Priority 1').split('—')[0].trim()}</span>
          <span class="mini-pill">📍 ${job.location}</span>
          <span class="mini-pill">💼 ${job.work_mode}</span>
          <span class="mini-pill">⏱ ${job.experience_req}</span>
          <span class="mini-pill">💰 ${job.salary}</span>
        </div>

        <p class="top5-why-text">${job.why_matches}</p>

        <div class="top5-actions" onclick="event.stopPropagation()">
          <button class="btn-card-details" onclick="openJobDrawer('${job.id}')">Breakdown & SOPs</button>
          <a href="${job.app_url}" target="_blank" class="btn-card-apply">Apply Directly →</a>
        </div>
      </article>
    `;
  }).join('');

  if (container) container.innerHTML = cardsHtml;
  if (fullContainer) fullContainer.innerHTML = cardsHtml;
}

// Render All Jobs Explorer (Supports Active, Processed & All scopes)
function renderExplorer() {
  const tableBody = document.getElementById('jobsTableBody');
  const gridView = document.getElementById('jobsGridView');
  const countBadge = document.getElementById('explorerCount');
  if (!state.data || !state.data.jobs) return;

  let list = [...state.data.jobs];

  // Feed Scope filter
  if (state.feedScope === 'active') {
    list = list.filter(j => j.is_active);
  } else if (state.feedScope === 'processed') {
    list = list.filter(j => !j.is_active);
  }

  // Search Filter
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(j => {
      const text = `${j.title} ${j.company} ${(j.matched_skills || []).join(' ')} ${j.why_matches} ${j.location}`.toLowerCase();
      return text.includes(q);
    });
  }

  // Role Category
  if (state.roleFilter !== 'all') {
    list = list.filter(j => j.role_category === state.roleFilter);
  }

  // Priority
  if (state.prioFilter !== 'all') {
    list = list.filter(j => j.priority_class === state.prioFilter);
  }

  // Status
  if (state.statusFilter !== 'all') {
    list = list.filter(j => j.status === state.statusFilter);
  }

  // Sort
  list.sort((a, b) => {
    if (state.sortMode === 'score-desc') return b.score - a.score;
    if (state.sortMode === 'score-asc') return a.score - b.score;
    if (state.sortMode === 'rank-asc') return (a.rank || 99) - (b.rank || 99);
    if (state.sortMode === 'title-asc') return a.title.localeCompare(b.title);
    if (state.sortMode === 'company-asc') return a.company.localeCompare(b.company);
    return 0;
  });

  if (countBadge) countBadge.textContent = `${list.length} Opportunities (${state.feedScope.toUpperCase()} FEED)`;

  // Render Table View
  if (tableBody) {
    if (list.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 36px; color: var(--text-muted);">No matching opportunities in this feed.</td></tr>`;
    } else {
      tableBody.innerHTML = list.map(job => {
        const scoreClass = job.score >= 90 ? 'badge-excellent' : (job.score >= 80 ? 'badge-strong' : 'badge-good');
        const isNewBadge = job.is_new && job.is_active ? `<span class="new-job-badge" style="margin-right: 4px;">NEW</span>` : '';
        return `
          <tr onclick="openJobDrawer('${job.id}')">
            <td>
              <div class="table-company-cell">
                <div class="table-logo-box" style="background-color: ${job.company_color || '#2563eb'};">
                  ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <div style="font-weight: 700; color: var(--text-primary);">${job.company}</div>
                  <div style="font-size: 0.72rem; color: var(--text-muted);">${job.source}</div>
                </div>
              </div>
            </td>
            <td>
              <div class="table-title-cell">
                <h4>${isNewBadge}${job.title}</h4>
                <span>${(job.role_category || 'CRM').toUpperCase()} • Req: ${job.experience_req}</span>
              </div>
            </td>
            <td>
              <div style="font-weight: 600; color: var(--text-primary);">${job.location}</div>
              <div style="font-size: 0.72rem; color: var(--text-muted);">${job.remote_eligibility || 'Remote'}</div>
            </td>
            <td>
              <span class="table-score-pill ${scoreClass}">${job.score}%</span>
            </td>
            <td style="font-weight: 600; font-size: 0.82rem;">
              ${job.salary}
            </td>
            <td onclick="event.stopPropagation()">
              <select class="status-badge-select ${PROCESSED_STATUSES.includes(job.status) ? 'status-applied' : ''}" onchange="setJobStatus('${job.id}', this.value)">
                <option value="New Match" ${job.status === 'New Match' ? 'selected' : ''}>New Match</option>
                <option value="Saved" ${job.status === 'Saved' ? 'selected' : ''}>Saved</option>
                <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
                <option value="Interview Scheduled" ${job.status === 'Interview Scheduled' ? 'selected' : ''}>Interview Scheduled</option>
                <option value="Interview Completed" ${job.status === 'Interview Completed' ? 'selected' : ''}>Interview Completed</option>
                <option value="Offer" ${job.status === 'Offer' ? 'selected' : ''}>Offer</option>
                <option value="Rejected" ${job.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
              </select>
            </td>
            <td style="text-align: right;" onclick="event.stopPropagation()">
              <a href="${job.app_url}" target="_blank" class="btn-card-apply" style="display: inline-block; padding: 5px 12px; font-size: 0.78rem;">
                Apply →
              </a>
            </td>
          </tr>
        `;
      }).join('');
    }
  }

  // Render Grid View
  if (gridView) {
    gridView.style.display = state.viewMode === 'grid' ? 'grid' : 'none';
    const tableWrap = document.getElementById('jobsTableWrap');
    if (tableWrap) tableWrap.style.display = state.viewMode === 'table' ? 'block' : 'none';

    if (state.viewMode === 'grid') {
      gridView.innerHTML = list.map(job => `
        <div class="top5-card" onclick="openJobDrawer('${job.id}')">
          <div class="top5-card-header">
            <div class="top5-company-box">
              <div class="company-logo-avatar" style="background-color: ${job.company_color || '#2563eb'};">
                ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
              </div>
              <div class="company-details">
                <h4>${job.company}</h4>
                <span style="font-size: 0.75rem; color: var(--text-muted);">${job.source}</span>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
              ${job.is_new ? '<span class="new-job-badge">NEW</span>' : ''}
              <div class="match-ring-badge ${job.score >= 90 ? 'badge-excellent' : 'badge-strong'}">
                ${job.score}%
              </div>
            </div>
          </div>
          <h3>${job.title}</h3>
          <div class="top5-meta-pills">
            <span class="mini-pill">📍 ${job.location}</span>
            <span class="mini-pill">💰 ${job.salary}</span>
            <span class="mini-pill">⏱ ${job.experience_req}</span>
          </div>
          <div class="top5-actions" onclick="event.stopPropagation()">
            <button class="btn-card-details" onclick="openJobDrawer('${job.id}')">Details</button>
            <a href="${job.app_url}" target="_blank" class="btn-card-apply">Apply →</a>
          </div>
        </div>
      `).join('');
    }
  }
}

// Open Right-Side Slide-Over Drawer
function openJobDrawer(jobId) {
  const allJobs = state.data.jobs || [];
  const job = allJobs.find(j => j.id === jobId || j.original_url === jobId || j.app_url === jobId);
  if (!job) return;

  state.activeDrawerJobId = jobId;
  const drawer = document.getElementById('jobDrawer');
  const backdrop = document.getElementById('drawerBackdrop');
  if (!drawer || !backdrop) return;

  // Populate drawer content
  document.getElementById('drawerJobTitle').textContent = job.title;
  document.getElementById('drawerCompany').textContent = `${job.company} • ${job.source}`;
  document.getElementById('drawerScoreNum').textContent = `${job.score}%`;
  document.getElementById('drawerScoreCat').textContent = job.category;

  document.getElementById('drawerLocation').textContent = `${job.location} (${job.remote_eligibility || 'Worldwide Remote'})`;
  document.getElementById('drawerWorkMode').textContent = `${job.work_mode} (${job.employment_type || 'Full-Time'})`;
  document.getElementById('drawerSalary').textContent = job.salary;
  document.getElementById('drawerExp').textContent = `Req: ${job.experience_req} (You: ${job.candidate_exp} — ${job.experience_gap || 'No Gap'})`;

  document.getElementById('drawerWhy').textContent = job.why_matches;
  document.getElementById('drawerConcerns').textContent = job.concerns || 'No major concerns identified.';

  // Matched Skills Tags
  const matchedContainer = document.getElementById('drawerMatchedSkills');
  if (matchedContainer) {
    matchedContainer.innerHTML = (job.matched_skills || []).map(s => `<span class="drawer-tag skill-matched">✓ ${s}</span>`).join('');
  }

  // Missing Skills Tags
  const missingContainer = document.getElementById('drawerMissingSkills');
  if (missingContainer) {
    if (job.missing_skills && job.missing_skills[0] !== 'None identified in core scope') {
      missingContainer.innerHTML = job.missing_skills.map(s => `<span class="drawer-tag skill-missing">⚠ ${s}</span>`).join('');
    } else {
      missingContainer.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">None identified</span>`;
    }
  }

  // Advantage Skills Tags
  const advContainer = document.getElementById('drawerAdvSkills');
  if (advContainer) {
    advContainer.innerHTML = (job.advantage_skills || []).map(s => `<span class="drawer-tag skill-adv">+ ${s}</span>`).join('');
  }

  // 7-Dimension Score Breakdown Progress Bars
  const breakdownBox = document.getElementById('drawerScoreBreakdown');
  if (breakdownBox && job.score_breakdown) {
    const sb = job.score_breakdown;
    breakdownBox.innerHTML = Object.keys(sb).map(k => {
      const item = sb[k];
      const pct = Math.round((item.score / item.max) * 100);
      return `
        <div class="breakdown-row">
          <div class="breakdown-label-flex">
            <span>${item.label}</span>
            <span><b>${item.score}/${item.max}</b> (${pct}%)</span>
          </div>
          <div class="breakdown-track">
            <div class="breakdown-fill ${pct >= 90 ? 'high' : 'mid'}" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Status selector sync
  const statusSelect = document.getElementById('drawerStatusSelect');
  if (statusSelect) {
    statusSelect.value = job.status || 'New Match';
    statusSelect.onchange = (e) => setJobStatus(job.id, e.target.value);
  }

  // CTA Link sync
  const applyBtn = document.getElementById('drawerApplyBtn');
  if (applyBtn) applyBtn.href = job.app_url;

  const viewBtn = document.getElementById('drawerViewBtn');
  if (viewBtn) viewBtn.href = job.original_url || job.app_url;

  // Open drawer
  drawer.classList.add('open');
  backdrop.classList.add('open');
}

function closeJobDrawer() {
  const drawer = document.getElementById('jobDrawer');
  const backdrop = document.getElementById('drawerBackdrop');
  if (drawer) drawer.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
  state.activeDrawerJobId = null;
}

// Render Market Insights
function renderMarketInsights() {
  if (!state.data || !state.data.market_insights) return;
  const mi = state.data.market_insights;

  const freqContainer = document.getElementById('inDemandSkillsBars');
  if (freqContainer && mi.most_in_demand_skills) {
    freqContainer.innerHTML = mi.most_in_demand_skills.map(s => `
      <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; margin-bottom: 4px;">
          <span>${s.skill}</span>
          <span style="color: var(--primary-accent);"><b>${s.frequency_pct}</b> (${s.count} roles)</span>
        </div>
        <div style="height: 8px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">
          <div style="height: 100%; width: ${s.frequency_pct}; background: linear-gradient(90deg, #2563eb, #3b82f6); border-radius: 9999px;"></div>
        </div>
      </div>
    `).join('');
  }
}

// Initialize Lightweight Analytics Charts
function initAnalyticsCharts() {
  if (typeof Chart === 'undefined' || !state.data) return;

  const jobs = state.data.jobs || [];
  const activeJobs = jobs.filter(j => j.is_active);

  const catCanvas = document.getElementById('matchDistChart');
  if (catCanvas) {
    const excellent = activeJobs.filter(j => j.score >= 90).length;
    const strong = activeJobs.filter(j => j.score >= 80 && j.score < 90).length;
    const good = activeJobs.filter(j => j.score < 80).length;

    new Chart(catCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Excellent (90–100%)', 'Strong (80–89%)', 'Good (70–79%)'],
        datasets: [{
          data: [excellent, strong, good],
          backgroundColor: ['#16a34a', '#2563eb', '#f59e0b'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Plus Jakarta Sans', size: 11 } } }
        },
        cutout: '70%'
      }
    });
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Sidebar navigation links
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const route = link.getAttribute('data-route');
      if (route) {
        navigateTo(route);
        const sb = document.getElementById('sidebar');
        if (sb) sb.classList.remove('mobile-open');
      }
    });
  });

  // Feed scope switcher buttons (Active, Processed, All)
  document.querySelectorAll('.feed-scope-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.feedScope = btn.getAttribute('data-scope');
      syncFeedScopeButtons();
      renderExplorer();
    });
  });

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      const sb = document.getElementById('sidebar');
      if (sb) sb.classList.toggle('mobile-open');
    });
  }

  // Date select switcher
  const dateSelect = document.getElementById('dateSelect');
  if (dateSelect) {
    dateSelect.addEventListener('change', (e) => {
      state.activeDate = e.target.value;
      loadDataset(e.target.value);
    });
  }

  // Search input
  const searchField = document.getElementById('searchField');
  if (searchField) {
    searchField.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderExplorer();
    });
  }

  // Sort select
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortMode = e.target.value;
      renderExplorer();
    });
  }

  // Quick filter chips
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-filter-type');
      const val = chip.getAttribute('data-filter');

      document.querySelectorAll(`.filter-chip[data-filter-type="${type}"]`).forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      if (type === 'role') state.roleFilter = val;
      if (type === 'prio') state.prioFilter = val;
      if (type === 'status') state.statusFilter = val;

      renderExplorer();
    });
  });

  // View mode switcher
  const btnViewTable = document.getElementById('btnViewTable');
  const btnViewGrid = document.getElementById('btnViewGrid');
  if (btnViewTable && btnViewGrid) {
    btnViewTable.addEventListener('click', () => {
      state.viewMode = 'table';
      btnViewTable.classList.add('active');
      btnViewGrid.classList.remove('active');
      renderExplorer();
    });
    btnViewGrid.addEventListener('click', () => {
      state.viewMode = 'grid';
      btnViewGrid.classList.add('active');
      btnViewTable.classList.remove('active');
      renderExplorer();
    });
  }

  // Drawer close listeners
  const closeBtn = document.getElementById('drawerCloseBtn');
  const backdrop = document.getElementById('drawerBackdrop');
  if (closeBtn) closeBtn.addEventListener('click', closeJobDrawer);
  if (backdrop) backdrop.addEventListener('click', closeJobDrawer);
}

// Toast Feedback Notification
function showToast(message) {
  let toast = document.getElementById('appToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'appToast';
    toast.className = 'toast-notice';
    document.body.appendChild(toast);
  }
  toast.textContent = `✓ ${message}`;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2600);
}
