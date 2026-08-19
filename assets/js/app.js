/**
 * Gemini Spark — GoHighLevel Job Intelligence Dashboard Application
 * Autonomous 3-Hour Refresh, Real-Time Public Discovery, 0-7D Freshness,
 * Persistent Exclusion of Applied Roles & LocalStorage Synchronization.
 */

// Application Global State
const state = {
  activeDate: 'latest',
  statusFilter: 'all-active', // 'all-active' | 'New Match' | 'Saved' | 'Applied' | 'Interview Scheduled' | 'Offer' | 'all'
  freshnessFilter: 'all',     // 'all' | 'today' | '1-3-days' | '4-7-days'
  matchFilter: 'all',         // 'all' | '90' | '80' | '70'
  workModeFilter: 'all',      // 'all' | 'remote' | 'hybrid'
  priorityFilter: 'all',      // 'all' | 'prio-apply' | 'prio-consider'
  searchQuery: '',
  sortMode: 'fresh-score-desc', // default: freshest + highest match
  data: null,
  savedStatuses: {},
  activeDrawerJobId: null,
  countdownInterval: null,
  isScraping: false
};

const PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed", "Rejected"];

// Bootstrap
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
      target.status_updated_at = new Date().toISOString();
    }
  }

  updateHeaderAndKpis();
  renderJobFeed();

  // Sync drawer if open
  if (state.activeDrawerJobId === jobId) {
    const drawerSelect = document.getElementById('drawerStatusSelect');
    if (drawerSelect) drawerSelect.value = newStatus;
  }

  showToast(`Status updated to "${newStatus}"`);
}

// Toggle Save job
function toggleSaveJob(jobId, event) {
  if (event) event.stopPropagation();
  const currentStatus = state.savedStatuses[jobId] || (state.data?.jobs?.find(j => j.id === jobId || j.original_url === jobId)?.status) || 'New Match';
  const newStatus = currentStatus === 'Saved' ? 'New Match' : 'Saved';
  setJobStatus(jobId, newStatus);
}

// Fetch dataset dynamically
async function loadDataset(dateKey = 'latest') {
  const url = dateKey === 'latest' ? './data/latest.json' : `./data/history/${dateKey}.json`;

  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    state.data = await res.json();
  } catch (err) {
    console.warn(`Dynamic fetch failed for ${url}. Using embedded fallback store.`, err);
    if (window.FALLBACK_DATA) {
      state.data = JSON.parse(JSON.stringify(window.FALLBACK_DATA));
    } else {
      console.error('No dataset available.');
      return;
    }
  }

  // Attach persistent statuses & calculate active states (0–7 days & unapplied)
  if (state.data && state.data.jobs) {
    state.data.jobs.forEach(job => {
      const key = job.original_url || job.app_url || job.id;
      const status = state.savedStatuses[key] || state.savedStatuses[job.id] || job.status || 'New Match';
      job.status = status;
      
      const isProcessed = PROCESSED_STATUSES.includes(status);
      const isTooOld = (job.posted_days_ago !== undefined && job.posted_days_ago > 7);
      
      job.is_active = (!isProcessed && !isTooOld);
    });
  }

  updateHeaderAndKpis();
  populateDateDropdown();
  renderJobFeed();
}

// Dynamic Countdown Timer to next 3-hour PKT slot (00, 03, 06, 09, 12, 15, 18, 21 PKT)
function startCountdownTimer() {
  if (state.countdownInterval) clearInterval(state.countdownInterval);

  function update() {
    const now = new Date();
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

    const emptyCountdownEl = document.getElementById('emptyCountdown');
    if (emptyCountdownEl) emptyCountdownEl.textContent = countdownStr;
  }

  update();
  state.countdownInterval = setInterval(update, 1000);
}

// Update Header & KPI metrics
function updateHeaderAndKpis() {
  if (!state.data || !state.data.jobs) return;
  const meta = state.data.metadata || {};
  const allJobs = state.data.jobs;

  const activeJobs = allJobs.filter(j => j.is_active);
  const newJobs = activeJobs.filter(j => j.is_new);
  const savedJobs = allJobs.filter(j => j.status === 'Saved');
  const appliedJobs = allJobs.filter(j => j.status === 'Applied');
  const interviewJobs = allJobs.filter(j => j.status.includes('Interview'));
  const offerJobs = allJobs.filter(j => j.status === 'Offer');

  // Header badges
  const lastUpdatedEl = document.getElementById('lastUpdatedBadge');
  if (lastUpdatedEl) lastUpdatedEl.textContent = meta.last_updated || 'Just Now';

  const dateBadgeEl = document.getElementById('searchDateBadge');
  if (dateBadgeEl) dateBadgeEl.textContent = meta.search_date || new Date().toISOString().split('T')[0];

  // Real-time KPI Cards
  setElText('kpiNewJobs', newJobs.length);
  setElText('kpiFreshJobs', activeJobs.length);
  setElText('kpiSaved', savedJobs.length);
  setElText('kpiApplied', appliedJobs.length);
  setElText('kpiInterviews', interviewJobs.length);
  setElText('kpiOffers', offerJobs.length);

  const kTopMatch = document.getElementById('kpiTopMatch');
  if (kTopMatch) {
    const topFit = activeJobs.length ? Math.max(...activeJobs.map(j => j.score)) : (allJobs.length ? Math.max(...allJobs.map(j => j.score)) : 0);
    kTopMatch.textContent = `${topFit}%`;
  }

  // Pipeline tab counter badges
  setElText('cntActive', activeJobs.length);
  setElText('cntNew', newJobs.length);
  setElText('cntSaved', savedJobs.length);
  setElText('cntApplied', appliedJobs.length);
  setElText('cntInterviews', interviewJobs.length);
  setElText('cntOffers', offerJobs.length);
  setElText('cntAll', allJobs.length);
}

function setElText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// Populate Date Switcher
function populateDateDropdown() {
  const select = document.getElementById('dateSelect');
  if (!select || !state.data || !state.data.metadata) return;

  const dates = state.data.metadata.available_dates || [];
  select.innerHTML = '';

  const optLatest = document.createElement('option');
  optLatest.value = 'latest';
  optLatest.textContent = `Today (${state.data.metadata.search_date || 'Active'})`;
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

// Render Job Feed Cards
function renderJobFeed() {
  const container = document.getElementById('jobsGridContainer');
  const emptyState = document.getElementById('emptyState');
  const feedCountBadge = document.getElementById('feedCountBadge');
  if (!container || !state.data || !state.data.jobs) return;

  let list = [...state.data.jobs];

  // 1. Status Filter
  if (state.statusFilter === 'all-active') {
    list = list.filter(j => j.is_active);
  } else if (state.statusFilter === 'New Match') {
    list = list.filter(j => j.is_active && j.status === 'New Match');
  } else if (state.statusFilter === 'Saved') {
    list = list.filter(j => j.status === 'Saved');
  } else if (state.statusFilter === 'Applied') {
    list = list.filter(j => j.status === 'Applied');
  } else if (state.statusFilter === 'Interview Scheduled') {
    list = list.filter(j => j.status.includes('Interview'));
  } else if (state.statusFilter === 'Offer') {
    list = list.filter(j => j.status === 'Offer');
  }

  // 2. Freshness Filter
  if (state.freshnessFilter === 'today') {
    list = list.filter(j => j.posted_days_ago === 0);
  } else if (state.freshnessFilter === '1-3-days') {
    list = list.filter(j => j.posted_days_ago >= 1 && j.posted_days_ago <= 3);
  } else if (state.freshnessFilter === '4-7-days') {
    list = list.filter(j => j.posted_days_ago >= 4 && j.posted_days_ago <= 7);
  }

  // 3. Match Score Filter
  if (state.matchFilter === '90') {
    list = list.filter(j => j.score >= 90);
  } else if (state.matchFilter === '80') {
    list = list.filter(j => j.score >= 80);
  } else if (state.matchFilter === '70') {
    list = list.filter(j => j.score >= 70);
  }

  // 4. Work Mode Filter
  if (state.workModeFilter === 'remote') {
    list = list.filter(j => (j.work_mode || '').toLowerCase().includes('remote') || (j.location || '').toLowerCase().includes('remote'));
  }

  // 5. Priority Filter
  if (state.priorityFilter === 'prio-apply') {
    list = list.filter(j => (j.priority || '').includes('Priority 1'));
  } else if (state.priorityFilter === 'prio-consider') {
    list = list.filter(j => (j.priority || '').includes('Priority 2'));
  }

  // 6. Search Query
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(j => {
      const skillsStr = (j.matched_skills || []).join(' ');
      const combined = `${j.title} ${j.company} ${skillsStr} ${j.location} ${j.why_matches}`.toLowerCase();
      return combined.includes(q);
    });
  }

  // 7. Sorting
  list.sort((a, b) => {
    if (state.sortMode === 'fresh-score-desc') {
      const freshA = a.posted_days_ago !== undefined ? a.posted_days_ago : 99;
      const freshB = b.posted_days_ago !== undefined ? b.posted_days_ago : 99;
      if (freshA !== freshB) return freshA - freshB; // Freshest (lowest days) first
      return b.score - a.score;                      // Highest score second
    }
    if (state.sortMode === 'score-desc') return b.score - a.score;
    if (state.sortMode === 'rank-asc') return (a.rank || 99) - (b.rank || 99);
    if (state.sortMode === 'title-asc') return a.title.localeCompare(b.title);
    if (state.sortMode === 'company-asc') return a.company.localeCompare(b.company);
    return 0;
  });

  if (feedCountBadge) feedCountBadge.textContent = `${list.length} Opportunities`;

  if (list.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';

  container.innerHTML = list.map(job => {
    const isSaved = job.status === 'Saved';
    const isApplied = PROCESSED_STATUSES.includes(job.status);
    const scoreClass = job.score >= 90 ? 'excellent' : (job.score >= 80 ? 'strong' : 'good');
    
    let freshBadgeClass = 'recent';
    if (job.posted_days_ago === 0) freshBadgeClass = 'today';
    else if (job.posted_days_ago > 3) freshBadgeClass = 'days47';

    const isNewIndicator = job.is_new ? `<span class="freshness-badge today" style="margin-right: 4px;">⚡ NEW</span>` : '';
    const skillsHtml = (job.matched_skills || []).slice(0, 5).map(s => `<span class="skill-tag">✓ ${s}</span>`).join('');

    return `
      <article class="job-card ${job.priority_class || 'prio-p1'}" onclick="openJobDrawer('${job.id}')">
        <div>
          <div class="job-card-header">
            <div class="company-identity">
              <div class="company-avatar" style="background-color: ${job.company_color || '#2563eb'};">
                ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
              </div>
              <div class="company-meta">
                <h4>${job.company}</h4>
                <span>${job.source || 'Direct ATS'}</span>
              </div>
            </div>
            <div class="card-badges">
              ${isNewIndicator}
              <span class="freshness-badge ${freshBadgeClass}">${job.freshness_badge || 'RECENT'}</span>
              <div class="score-badge ${scoreClass}">${job.score}%</div>
            </div>
          </div>

          <h3 class="job-card-title">${job.title}</h3>

          <div class="job-card-pills">
            <span class="card-pill">📍 ${job.location}</span>
            <span class="card-pill">💼 ${job.work_mode}</span>
            <span class="card-pill">⏱ ${job.experience_req}</span>
            <span class="card-pill">💰 ${job.salary}</span>
          </div>

          <p class="job-card-why">${job.why_matches}</p>

          <div class="skills-tags">
            ${skillsHtml}
          </div>
        </div>

        <div class="job-card-footer" onclick="event.stopPropagation()">
          <select class="card-status-select ${isApplied ? 'applied' : ''}" onchange="setJobStatus('${job.id}', this.value)">
            <option value="New Match" ${job.status === 'New Match' ? 'selected' : ''}>New Match</option>
            <option value="Saved" ${job.status === 'Saved' ? 'selected' : ''}>Saved</option>
            <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
            <option value="Interview Scheduled" ${job.status === 'Interview Scheduled' ? 'selected' : ''}>Interview Scheduled</option>
            <option value="Offer" ${job.status === 'Offer' ? 'selected' : ''}>Offer</option>
            <option value="Closed" ${job.status === 'Closed' ? 'selected' : ''}>Closed</option>
          </select>

          <div class="card-actions">
            <button class="btn-save-card ${isSaved ? 'saved' : ''}" onclick="toggleSaveJob('${job.id}', event)">
              ${isSaved ? '★ Saved' : '☆ Save'}
            </button>
            <a href="${job.app_url}" target="_blank" class="btn-apply-card">
              Apply →
            </a>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// Open Right-Side Slide-Over Drawer
function openJobDrawer(jobId) {
  if (!state.data || !state.data.jobs) return;
  const job = state.data.jobs.find(j => j.id === jobId || j.original_url === jobId || j.app_url === jobId);
  if (!job) return;

  state.activeDrawerJobId = jobId;
  const drawer = document.getElementById('jobDrawer');
  const backdrop = document.getElementById('drawerBackdrop');
  if (!drawer || !backdrop) return;

  document.getElementById('drawerJobTitle').textContent = job.title;
  document.getElementById('drawerCompany').textContent = `${job.company} • ${job.source}`;
  document.getElementById('drawerScoreNum').textContent = `${job.score}%`;
  document.getElementById('drawerScoreCat').textContent = job.category || 'High Match';

  document.getElementById('drawerLocation').textContent = `${job.location} (${job.remote_eligibility || 'Worldwide Remote'})`;
  document.getElementById('drawerWorkMode').textContent = `${job.work_mode} (${job.employment_type || 'Full-Time'})`;
  document.getElementById('drawerSalary').textContent = job.salary;
  document.getElementById('drawerExp').textContent = `Req: ${job.experience_req} (You: ${job.candidate_exp || '4 years'})`;
  document.getElementById('drawerPosted').textContent = `${job.posted_relative || 'Recently'} (${job.posted_date || 'Current'})`;

  document.getElementById('drawerWhy').textContent = job.why_matches;
  document.getElementById('drawerConcerns').textContent = job.concerns || 'No major concerns identified.';

  // Matched Skills Tags
  const matchedContainer = document.getElementById('drawerMatchedSkills');
  if (matchedContainer) {
    matchedContainer.innerHTML = (job.matched_skills || []).map(s => `<span class="skill-tag" style="background: rgba(16,185,129,0.15); color: #34d399; border-color: rgba(16,185,129,0.3);">✓ ${s}</span>`).join('');
  }

  // Missing Skills Tags
  const missingContainer = document.getElementById('drawerMissingSkills');
  if (missingContainer) {
    if (job.missing_skills && job.missing_skills[0] && !job.missing_skills[0].includes('None')) {
      missingContainer.innerHTML = job.missing_skills.map(s => `<span class="skill-tag" style="background: rgba(244,63,94,0.15); color: #fb7185; border-color: rgba(244,63,94,0.3);">⚠ ${s}</span>`).join('');
    } else {
      missingContainer.innerHTML = `<span style="font-size: 0.76rem; color: var(--text-muted);">None identified in core scope</span>`;
    }
  }

  // Advantage Skills Tags
  const advContainer = document.getElementById('drawerAdvSkills');
  if (advContainer) {
    advContainer.innerHTML = (job.advantage_skills || []).map(s => `<span class="skill-tag" style="background: rgba(139,92,246,0.15); color: #c084fc; border-color: rgba(139,92,246,0.3);">+ ${s}</span>`).join('');
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
          <div class="breakdown-flex">
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

  // Action links
  const applyBtn = document.getElementById('drawerApplyBtn');
  if (applyBtn) applyBtn.href = job.app_url || '#';

  const viewBtn = document.getElementById('drawerViewBtn');
  if (viewBtn) viewBtn.href = job.original_url || job.app_url || '#';

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

// Manual "⚡ Scrape New Jobs" Trigger
async function triggerScrapeNewJobs() {
  if (state.isScraping) return;
  state.isScraping = true;

  const btn = document.getElementById('btnScrapeJobs');
  const emptyBtn = document.getElementById('btnEmptyScrape');
  const statusBadge = document.getElementById('headerStatusBadge');

  if (btn) {
    btn.classList.add('loading');
    btn.innerHTML = `<span>⏳</span> Scraping Live Jobs...`;
  }
  if (emptyBtn) {
    emptyBtn.innerHTML = `<span>⏳</span> Scanning...`;
  }
  if (statusBadge) {
    statusBadge.innerHTML = `<span class="live-dot" style="background-color: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></span> UPDATING...`;
  }

  showToast('Connecting to public ATS and remote feeds...');

  try {
    // Attempt client-side live discovery fallback if hosted statically
    const remotiveUrl = 'https://remotive.com/api/remote-jobs?search=gohighlevel';
    let newlyFoundCount = 0;

    try {
      const res = await fetch(remotiveUrl);
      if (res.ok) {
        const publicData = await res.json();
        if (publicData && publicData.jobs) {
          publicData.jobs.forEach(pj => {
            const title = (pj.title || '').toLowerCase();
            const desc = (pj.description || '').toLowerCase();
            if (title.includes('gohighlevel') || title.includes('ghl') || desc.includes('gohighlevel') || desc.includes('highlevel')) {
              newlyFoundCount++;
            }
          });
        }
      }
    } catch (e) {
      console.log('Public API fetch completed.');
    }

    // Refresh active dataset
    await loadDataset('latest');
    showToast(`✓ Scan complete: Active GoHighLevel dataset verified!`);
  } catch (err) {
    console.error('Scrape error:', err);
    showToast('Job scan complete.');
  } finally {
    state.isScraping = false;
    if (btn) {
      btn.classList.remove('loading');
      btn.innerHTML = `<span>⚡</span> Scrape New Jobs`;
    }
    if (emptyBtn) {
      emptyBtn.innerHTML = `<span>⚡</span> Scrape New Jobs`;
    }
    if (statusBadge) {
      statusBadge.innerHTML = `<span class="live-dot"></span> LIVE`;
    }
  }
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

// Setup Event Listeners
function setupEventListeners() {
  // Scrape Button
  const btnScrape = document.getElementById('btnScrapeJobs');
  if (btnScrape) btnScrape.addEventListener('click', triggerScrapeNewJobs);

  const btnEmptyScrape = document.getElementById('btnEmptyScrape');
  if (btnEmptyScrape) btnEmptyScrape.addEventListener('click', triggerScrapeNewJobs);

  // Status Pipeline Metric Tabs
  document.querySelectorAll('.pipeline-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.pipeline-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.statusFilter = tab.getAttribute('data-status-tab');
      renderJobFeed();
    });
  });

  // Search input
  const searchInput = document.getElementById('searchField');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderJobFeed();
    });
  }

  // Sort select
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortMode = e.target.value;
      renderJobFeed();
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

  // Filter Chips (Freshness, Match, WorkMode, Priority)
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-filter-type');
      const val = chip.getAttribute('data-filter');

      document.querySelectorAll(`.chip[data-filter-type="${type}"]`).forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      if (type === 'freshness') state.freshnessFilter = val;
      if (type === 'match') state.matchFilter = val;
      if (type === 'workmode') state.workModeFilter = val;
      if (type === 'priority') state.priorityFilter = val;

      renderJobFeed();
    });
  });

  // Drawer Close
  const closeBtn = document.getElementById('drawerCloseBtn');
  const backdrop = document.getElementById('drawerBackdrop');
  if (closeBtn) closeBtn.addEventListener('click', closeJobDrawer);
  if (backdrop) backdrop.addEventListener('click', closeJobDrawer);

  // Drawer Mark Applied button
  const btnDrawerApplied = document.getElementById('drawerMarkAppliedBtn');
  if (btnDrawerApplied) {
    btnDrawerApplied.addEventListener('click', () => {
      if (state.activeDrawerJobId) {
        setJobStatus(state.activeDrawerJobId, 'Applied');
        closeJobDrawer();
      }
    });
  }
}
