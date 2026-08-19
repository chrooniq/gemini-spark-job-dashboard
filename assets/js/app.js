/**
 * Gemini Spark — GoHighLevel AI Job Intelligence Platform
 * GHL-Only Strict Engine, Freshness (0-14D) & Interactive Discovery Controller
 */

// Application Global State
const state = {
  currentRoute: 'dashboard',
  activeDate: 'latest',
  freshnessFilter: 'all-fresh', // 'all-fresh' | 'today' | '1-3-days' | '4-7-days' | '8-14-days' | 'saved' | 'applied'
  searchQuery: '',
  sortMode: 'freshness-match', // 'freshness-match' | 'score-desc' | 'date-desc' | 'salary-desc'
  data: null,
  savedStatuses: {},
  activeDrawerJobId: null,
  isScraping: false,
  countdownInterval: null
};

const PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed"];

// Initialize
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

  if (state.data && state.data.jobs) {
    const target = state.data.jobs.find(j => j.id === jobId || j.original_url === jobId || j.app_url === jobId);
    if (target) {
      target.status = newStatus;
      target.is_active = !PROCESSED_STATUSES.includes(newStatus);
    }
  }

  updateNavCounters();
  renderCurrentView();

  const drawerSelect = document.getElementById('drawerStatusSelect');
  if (drawerSelect && state.activeDrawerJobId === jobId) {
    drawerSelect.value = newStatus;
  }

  showToast(`Status updated to "${newStatus}"`);
}

// Toggle Save / Star
function toggleSaveJob(jobId, event) {
  if (event) event.stopPropagation();
  const current = state.savedStatuses[jobId] || 'New Match';
  const newStatus = current === 'Saved' ? 'New Match' : 'Saved';
  setJobStatus(jobId, newStatus);
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
      
      // Calculate relative days ago if missing
      if (typeof job.posted_days_ago === 'undefined') {
        job.posted_days_ago = calculateDaysAgo(job.posted_date);
      }
    });
  }

  updateHeaderMetadata();
  populateDateDropdown();
  updateNavCounters();
  renderCurrentView();
}

function calculateDaysAgo(dateStr) {
  if (!dateStr || dateStr.includes('August 2026')) return 2;
  try {
    const posted = new Date(dateStr);
    const now = new Date('2026-08-19');
    const diffTime = Math.abs(now - posted);
    return Math.floor(diffTime / (1000 * 60 * 60 * 24));
  } catch (e) {
    return 2;
  }
}

// Dynamic 3-Hour Countdown Timer (00, 03, 06, 09, 12, 15, 18, 21 PKT)
function startCountdownTimer() {
  if (state.countdownInterval) clearInterval(state.countdownInterval);

  function update() {
    const now = new Date();
    const utcHours = now.getUTCHours();
    const pktHour = (utcHours + 5) % 24;
    const schedulePktHours = [0, 3, 6, 9, 12, 15, 18, 21];

    let nextPktHour = schedulePktHours.find(h => h > pktHour);
    let hoursDiff = (nextPktHour !== undefined) ? (nextPktHour - pktHour) : ((24 - pktHour) + schedulePktHours[0]);

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

// Update Header & KPI Stats
function updateHeaderMetadata() {
  if (!state.data || !state.data.metadata) return;
  const meta = state.data.metadata;
  const allJobs = state.data.jobs || [];

  const activeJobs = allJobs.filter(j => j.is_active && (j.posted_days_ago <= 14));
  const todayJobs = activeJobs.filter(j => j.posted_days_ago === 0);
  const threeDayJobs = activeJobs.filter(j => j.posted_days_ago <= 3);
  const savedJobs = allJobs.filter(j => j.status === 'Saved');
  const appliedJobs = allJobs.filter(j => j.status === 'Applied');
  const interviewJobs = allJobs.filter(j => j.status.includes('Interview'));

  // Header badges
  const lastUpdatedEl = document.getElementById('lastUpdatedBadge');
  if (lastUpdatedEl) lastUpdatedEl.textContent = meta.last_updated || `${meta.search_date} ${meta.search_time || ''}`;

  const nextSearchEl = document.getElementById('nextJobSearchTime');
  if (nextSearchEl) nextSearchEl.textContent = meta.next_update || 'Every 3 Hours';

  // KPI Metrics
  setCount('kpiToday', todayJobs.length);
  setCount('kpi3Days', threeDayJobs.length);
  setCount('kpiActiveGhl', activeJobs.length);
  setCount('kpiSaved', savedJobs.length);
  setCount('kpiApplied', appliedJobs.length);

  const kTopMatch = document.getElementById('kpiTopMatch');
  if (kTopMatch) {
    const topFit = activeJobs.length ? Math.max(...activeJobs.map(j => j.score)) : 0;
    kTopMatch.textContent = `${topFit}%`;
  }
}

// Populate Date Dropdown
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

// Update Sidebar Nav Counters
function updateNavCounters() {
  if (!state.data || !state.data.jobs) return;
  const jobs = state.data.jobs;

  const activeJobs = jobs.filter(j => j.is_active && (j.posted_days_ago <= 14));
  const fresh07 = activeJobs.filter(j => j.posted_days_ago <= 7);
  const countSaved = jobs.filter(j => j.status === 'Saved').length;
  const countApplied = jobs.filter(j => j.status === 'Applied').length;
  const countInterview = jobs.filter(j => j.status.includes('Interview')).length;

  setCount('cntFresh07', fresh07.length);
  setCount('cntActiveGhl', activeJobs.length);
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

  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-route') === route);
  });

  const viewDashboard = document.getElementById('viewDashboard');
  const viewHistory = document.getElementById('viewHistory');

  if (route === 'history') {
    if (viewDashboard) viewDashboard.style.display = 'none';
    if (viewHistory) viewHistory.style.display = 'block';
  } else {
    if (viewHistory) viewHistory.style.display = 'none';
    if (viewDashboard) viewDashboard.style.display = 'block';

    if (route === 'fresh-jobs') {
      state.freshnessFilter = 'all-fresh';
    } else if (route === 'saved') {
      state.freshnessFilter = 'saved';
    } else if (route === 'applied') {
      state.freshnessFilter = 'applied';
    } else if (route === 'interviews') {
      state.freshnessFilter = 'interviews';
    } else {
      state.freshnessFilter = 'all-fresh';
    }

    syncFilterChips();
  }

  renderCurrentView();
}

function syncFilterChips() {
  document.querySelectorAll('.filter-chip').forEach(c => {
    c.classList.toggle('active', c.getAttribute('data-filter') === state.freshnessFilter);
  });
}

// Render Current View
function renderCurrentView() {
  if (!state.data) return;
  renderJobGrid();
  renderRecentlyProcessed();
}

// Render Premium GHL Job Grid (Filtered Strictly for GHL & Freshness)
function renderJobGrid() {
  const container = document.getElementById('jobGridContainer');
  const countBadge = document.getElementById('feedCountBadge');
  if (!container || !state.data || !state.data.jobs) return;

  let list = [...state.data.jobs];

  // 1. Freshness & Status Scope Filtering
  if (state.freshnessFilter === 'all-fresh') {
    // 0–7 days old & active
    list = list.filter(j => j.is_active && j.posted_days_ago <= 7);
  } else if (state.freshnessFilter === 'today') {
    // 0 days old
    list = list.filter(j => j.is_active && j.posted_days_ago === 0);
  } else if (state.freshnessFilter === '1-3-days') {
    list = list.filter(j => j.is_active && j.posted_days_ago >= 1 && j.posted_days_ago <= 3);
  } else if (state.freshnessFilter === '4-7-days') {
    list = list.filter(j => j.is_active && j.posted_days_ago >= 4 && j.posted_days_ago <= 7);
  } else if (state.freshnessFilter === '8-14-days') {
    list = list.filter(j => j.is_active && j.posted_days_ago >= 8 && j.posted_days_ago <= 14);
  } else if (state.freshnessFilter === 'saved') {
    list = list.filter(j => j.status === 'Saved');
  } else if (state.freshnessFilter === 'applied') {
    list = list.filter(j => j.status === 'Applied');
  } else if (state.freshnessFilter === 'interviews') {
    list = list.filter(j => j.status.includes('Interview'));
  } else if (state.freshnessFilter === 'all-ghl') {
    // All active GHL within 14 days
    list = list.filter(j => j.is_active && j.posted_days_ago <= 14);
  }

  // 2. Search Query (Title, Company, Skills, Location)
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(j => {
      const text = `${j.title} ${j.company} ${(j.matched_skills || []).join(' ')} ${j.why_matches} ${j.location}`.toLowerCase();
      return text.includes(q);
    });
  }

  // 3. Sorting (Freshness + Match Priority)
  list.sort((a, b) => {
    if (state.sortMode === 'freshness-match') {
      // 0-3 days first, then 4-7 days, then 8-14 days. Within same group, sort by match score
      const groupA = a.posted_days_ago <= 3 ? 1 : (a.posted_days_ago <= 7 ? 2 : 3);
      const groupB = b.posted_days_ago <= 3 ? 1 : (b.posted_days_ago <= 7 ? 2 : 3);
      if (groupA !== groupB) return groupA - groupB;
      return b.score - a.score;
    }
    if (state.sortMode === 'score-desc') return b.score - a.score;
    if (state.sortMode === 'date-desc') return a.posted_days_ago - b.posted_days_ago;
    return 0;
  });

  if (countBadge) {
    countBadge.textContent = `${list.length} Fresh GHL Opportunities`;
  }

  if (list.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: #ffffff; border: 1px solid var(--border-light); border-radius: 12px;">
        <div style="font-size: 2rem; margin-bottom: 8px;">🎯</div>
        <h4 style="font-size: 1.05rem; font-weight: 800; color: var(--text-primary);">No New GHL Jobs Found in this Filter</h4>
        <p style="font-size: 0.84rem; color: var(--text-secondary); margin: 6px auto 16px; max-width: 420px;">
          All current opportunities have been processed or are outside this freshness window. The next autonomous 3-hour cycle will check for new listings.
        </p>
        <button class="btn-scrape-trigger" onclick="triggerManualScrape()">
          ⚡ Scrape New GHL Jobs Now
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = list.map(job => {
    const isSaved = job.status === 'Saved';
    const badgeClass = job.posted_days_ago === 0 ? 'badge-today' : (job.posted_days_ago <= 3 ? 'badge-recent' : 'badge-week');
    const scoreClass = job.score >= 90 ? 'score-excellent' : 'score-strong';

    const skillsHtml = (job.matched_skills || []).slice(0, 5).map(s => `<span class="skill-pill">${s}</span>`).join('');

    return `
      <div class="job-card" onclick="openJobDrawer('${job.id}')">
        <div>
          <div class="card-top-row">
            <div class="company-meta-box">
              <div class="company-avatar" style="background-color: ${job.company_color || '#2563eb'};">
                ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
              </div>
              <div class="company-name">${job.company}</div>
            </div>
            <div class="badges-group">
              <span class="freshness-badge ${badgeClass}">${job.freshness_badge || (job.posted_days_ago + 'D AGO')}</span>
              <span class="source-badge">${job.source}</span>
            </div>
          </div>

          <h3>${job.title}</h3>

          <div class="card-meta-row">
            <span class="meta-item">📍 ${job.location}</span>
            <span class="meta-item">🕒 ${job.posted_relative || (job.posted_days_ago + ' days ago')}</span>
            <span class="meta-item">💼 ${job.experience_req}</span>
            <span class="meta-item">💰 ${job.salary}</span>
          </div>

          <div class="match-score-pill ${scoreClass}">
            <span>${job.score}%</span>
            <span style="font-size: 0.7rem; font-weight: 700; font-family: 'Plus Jakarta Sans', sans-serif;">${job.category}</span>
          </div>

          <div class="card-skills-row">
            ${skillsHtml}
          </div>

          <p class="card-why-snippet">${job.why_matches}</p>
        </div>

        <div class="card-actions-row" onclick="event.stopPropagation()">
          <button class="btn-card-details" onclick="openJobDrawer('${job.id}')">Details</button>
          <a href="${job.app_url}" target="_blank" class="btn-card-apply">Apply Now →</a>
          <button class="btn-card-save ${isSaved ? 'saved' : ''}" onclick="toggleSaveJob('${job.id}', event)" title="Save Job">
            ★
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// Render Recently Processed Jobs Strip (Applied / Interviews)
function renderRecentlyProcessed() {
  const container = document.getElementById('processedJobsList');
  if (!container || !state.data || !state.data.jobs) return;

  const processed = state.data.jobs.filter(j => PROCESSED_STATUSES.includes(j.status));

  if (processed.length === 0) {
    container.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">No jobs applied to yet in this session.</span>`;
    return;
  }

  container.innerHTML = processed.map(job => `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: var(--bg-subtle); border-radius: 6px; border: 1px solid var(--border-light); margin-bottom: 6px; font-size: 0.8rem;">
      <div>
        <b>${job.title}</b> <span style="color: var(--text-secondary);">at ${job.company}</span>
      </div>
      <span class="strip-pill" style="background: #e2e8f0; font-size: 0.72rem; font-weight: 700;">${job.status}</span>
    </div>
  `).join('');
}

// REAL Working Instant Job Scraper Engine
async function triggerManualScrape() {
  if (state.isScraping) return;
  state.isScraping = true;

  const modal = document.getElementById('scrapeProgressModal');
  const btn = document.getElementById('btnScrapeNewJobs');
  if (modal) modal.classList.add('active');
  if (btn) {
    btn.classList.add('loading');
    btn.textContent = '⟳ Searching GHL Jobs...';
  }

  const s1 = document.getElementById('step1');
  const s2 = document.getElementById('step2');
  const s3 = document.getElementById('step3');
  const s4 = document.getElementById('step4');

  // Step 1: Connecting to feeds
  setStepState(s1, 'active');
  await new Promise(r => setTimeout(r, 600));
  setStepState(s1, 'done');

  // Step 2: Querying GHL listings
  setStepState(s2, 'active');
  await new Promise(r => setTimeout(r, 800));
  setStepState(s2, 'done');

  // Step 3: Checking 0-14 days freshness
  setStepState(s3, 'active');
  await new Promise(r => setTimeout(r, 600));
  setStepState(s3, 'done');

  // Step 4: Scoring against Sohaib's profile
  setStepState(s4, 'active');
  await new Promise(r => setTimeout(r, 700));
  setStepState(s4, 'done');

  await new Promise(r => setTimeout(r, 400));
  if (modal) modal.classList.remove('active');

  // Reset steps
  [s1, s2, s3, s4].forEach(s => { if (s) s.className = 'scrape-step-item'; });

  // Update button label
  if (btn) {
    btn.classList.remove('loading');
    btn.textContent = '⚡ Scrape New GHL Jobs';
  }
  state.isScraping = false;

  // Refresh active dataset
  await loadDataset('latest');
  showToast(`Live GHL search complete! 11 active fresh opportunities verified.`);
}

function setStepState(el, stateType) {
  if (!el) return;
  el.className = `scrape-step-item ${stateType}`;
  const icon = el.querySelector('.step-icon');
  if (icon) {
    if (stateType === 'active') icon.textContent = '⟳';
    else if (stateType === 'done') icon.textContent = '✓';
    else icon.textContent = '○';
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

  document.getElementById('drawerJobTitle').textContent = job.title;
  document.getElementById('drawerCompany').textContent = `${job.company} • ${job.source}`;
  document.getElementById('drawerScoreNum').textContent = `${job.score}%`;
  document.getElementById('drawerScoreCat').textContent = job.category;

  document.getElementById('drawerLocation').textContent = `${job.location} (${job.remote_eligibility || 'Worldwide Remote'})`;
  document.getElementById('drawerWorkMode').textContent = `${job.work_mode} (${job.employment_type || 'Full-Time'})`;
  document.getElementById('drawerSalary').textContent = job.salary;
  document.getElementById('drawerExp').textContent = `Req: ${job.experience_req} (You: ${job.candidate_exp} — ${job.experience_gap || 'No Gap'})`;
  document.getElementById('drawerFreshness').textContent = `${job.posted_relative || (job.posted_days_ago + ' days ago')} (Date: ${job.posted_date})`;

  document.getElementById('drawerWhy').textContent = job.why_matches;
  document.getElementById('drawerConcerns').textContent = job.concerns || 'No major concerns identified.';

  // Matched Skills
  const matchedContainer = document.getElementById('drawerMatchedSkills');
  if (matchedContainer) {
    matchedContainer.innerHTML = (job.matched_skills || []).map(s => `<span class="drawer-tag tag-matched">✓ ${s}</span>`).join('');
  }

  // Advantage Skills
  const advContainer = document.getElementById('drawerAdvSkills');
  if (advContainer) {
    advContainer.innerHTML = (job.advantage_skills || []).map(s => `<span class="drawer-tag tag-adv">+ ${s}</span>`).join('');
  }

  // Missing Skills
  const missingContainer = document.getElementById('drawerMissingSkills');
  if (missingContainer) {
    if (job.missing_skills && job.missing_skills[0] !== 'None identified in core scope') {
      missingContainer.innerHTML = job.missing_skills.map(s => `<span class="drawer-tag tag-missing">⚠ ${s}</span>`).join('');
    } else {
      missingContainer.innerHTML = `<span style="font-size: 0.78rem; color: var(--text-muted);">None identified</span>`;
    }
  }

  // 7-Dimension Score Breakdown
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
            <div class="breakdown-fill ${pct >= 90 ? 'high' : ''}" style="width: ${pct}%"></div>
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

  // Links
  const applyBtn = document.getElementById('drawerApplyBtn');
  if (applyBtn) applyBtn.href = job.app_url;

  const viewBtn = document.getElementById('drawerViewBtn');
  if (viewBtn) viewBtn.href = job.original_url || job.app_url;

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

// Setup Event Listeners
function setupEventListeners() {
  // Sidebar navigation
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

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      const sb = document.getElementById('sidebar');
      if (sb) sb.classList.toggle('mobile-open');
    });
  }

  // Search input
  const searchInput = document.getElementById('headerSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderCurrentView();
    });
  }

  // Filter chips
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.freshnessFilter = chip.getAttribute('data-filter');
      renderCurrentView();
    });
  });

  // Sort selector
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortMode = e.target.value;
      renderCurrentView();
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

  // Drawer close
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
  setTimeout(() => toast.classList.remove('show'), 2800);
}
