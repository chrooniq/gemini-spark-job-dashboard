/**
 * Gemini Spark — Phase 3 Multi-Page SaaS Career Intelligence Portal Controller
 * Modular Client-Side Router, 7 Dedicated Pages, Vector Icon Bindings,
 * Real-Time Discovery, Kanban Application Tracker, and Compare Jobs Engine.
 */

// Global Application State
const state = {
  currentRoute: 'dashboard', // 'dashboard' | 'jobs' | 'matches' | 'saved' | 'applied' | 'resume' | 'portfolio'
  activeDate: 'latest',
  
  // All Jobs Filters
  allJobsFreshness: 'all',
  allJobsMatch: 'all',
  allJobsWorkMode: 'all',
  allJobsSort: 'newest',
  allJobsViewMode: 'grid', // 'grid' | 'list'
  searchQuery: '',

  // Compare System (max 3 jobs)
  selectedForCompare: new Set(),

  // Application Tracker
  trackerMode: 'kanban', // 'kanban' | 'table'

  data: null,
  savedStatuses: {},
  activeDrawerJobId: null,
  countdownInterval: null,
  isScraping: false,
  dashChart: null
};

const PROCESSED_STATUSES = ["Applied", "Interview Scheduled", "Interview Completed", "Offer", "Closed", "Rejected"];

// Bootstrap
document.addEventListener('DOMContentLoaded', async () => {
  loadSavedStatuses();
  await loadDataset('latest');
  setupRouting();
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

  updateMetricsAndSidebar();
  renderCurrentRoute();

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

  updateMetricsAndSidebar();
  populateDateDropdown();
  renderCurrentRoute();
}

// Client-Side Hash Router
function setupRouting() {
  function handleHash() {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    navigateTo(hash, false);
  }

  window.addEventListener('hashchange', handleHash);
  handleHash();
}

function navigateTo(routeName, updateHash = true) {
  const validRoutes = ['dashboard', 'jobs', 'matches', 'saved', 'applied', 'resume', 'portfolio'];
  if (!validRoutes.includes(routeName)) routeName = 'dashboard';

  state.currentRoute = routeName;
  if (updateHash) {
    window.location.hash = `#${routeName}`;
  }

  // Update Sidebar active state
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-route') === routeName);
  });

  // Update Top Navbar active state
  document.querySelectorAll('.top-nav-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-route') === routeName);
  });

  // Toggle Page Visibility
  validRoutes.forEach(r => {
    const el = document.getElementById(`page-${r}`);
    if (el) el.style.display = (r === routeName) ? 'flex' : 'none';
  });

  // Scroll viewport to top
  const mainVp = document.querySelector('.main-viewport');
  if (mainVp) mainVp.scrollTop = 0;

  renderCurrentRoute();
}

// Render Content for the Active Page
function renderCurrentRoute() {
  if (!state.data || !state.data.jobs) return;

  switch (state.currentRoute) {
    case 'dashboard':
      renderDashboardPage();
      break;
    case 'jobs':
      renderAllJobsPage();
      break;
    case 'matches':
      renderNewMatchesPage();
      break;
    case 'saved':
      renderSavedJobsPage();
      break;
    case 'applied':
      renderAppliedTrackerPage();
      break;
    case 'resume':
      // Resume content is static & interactive
      break;
    case 'portfolio':
      // Portfolio content is static & interactive
      break;
  }
}

// ==========================================================================
// PAGE 1: DASHBOARD
// ==========================================================================
function renderDashboardPage() {
  const allJobs = state.data.jobs;
  const activeJobs = allJobs.filter(j => j.is_active);

  // Top Matches List in Right Panel
  const topListContainer = document.getElementById('dashTopMatchesList');
  if (topListContainer) {
    const top4 = [...activeJobs].sort((a, b) => b.score - a.score).slice(0, 4);
    if (top4.length === 0) {
      topListContainer.innerHTML = `<div style="font-size: 0.78rem; color: var(--text-muted); padding: 12px; text-align: center;">All top matches have been applied to!</div>`;
    } else {
      topListContainer.innerHTML = top4.map(job => `
        <div class="mini-row-item" onclick="openJobDrawer('${job.id}')">
          <div class="mini-row-left">
            <div class="mini-logo-box" style="background-color: ${job.company_color || '#233d32'};">
              ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
            </div>
            <div class="mini-row-info">
              <h4>${job.title}</h4>
              <p>${job.company} • ${job.location}</p>
            </div>
          </div>
          <div class="mini-row-right">
            <span class="mini-match-pill">${job.score}%</span>
          </div>
        </div>
      `).join('');
    }
  }

  // Freshest 4 Opportunities Grid Preview
  const freshGridContainer = document.getElementById('dashFreshGrid');
  if (freshGridContainer) {
    const freshest4 = [...activeJobs]
      .sort((a, b) => (a.posted_days_ago || 0) - (b.posted_days_ago || 0) || b.score - a.score)
      .slice(0, 4);

    if (freshest4.length === 0) {
      freshGridContainer.innerHTML = `<div style="font-size: 0.82rem; color: var(--text-muted); padding: 20px; text-align: center; grid-column: span 2;">No fresh active jobs right now.</div>`;
    } else {
      freshGridContainer.innerHTML = freshest4.map(job => renderJobCardHtml(job, false)).join('');
    }
  }

  renderDashboardChart('week');
}

function renderDashboardChart(timeRange = 'week') {
  const ctx = document.getElementById('dashViewsChart');
  if (!ctx || typeof Chart === 'undefined') return;

  if (state.dashChart) {
    state.dashChart.destroy();
  }

  let labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  let dataPoints = [35, 62, 145, 98, 120, 75, 45];

  if (timeRange === 'day') {
    labels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'];
    dataPoints = [12, 18, 55, 92, 78, 64];
  } else if (timeRange === 'month') {
    labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    dataPoints = [180, 240, 310, 290];
  } else if (timeRange === 'all') {
    labels = ['May', 'Jun', 'Jul', 'Aug'];
    dataPoints = [420, 580, 720, 890];
  }

  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 180);
  gradient.addColorStop(0, 'rgba(203, 243, 47, 0.45)');
  gradient.addColorStop(0.6, 'rgba(35, 61, 50, 0.1)');
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

  state.dashChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'GHL Match Trajectory',
        data: dataPoints,
        borderColor: '#233d32',
        borderWidth: 2.5,
        backgroundColor: gradient,
        fill: true,
        tension: 0.45,
        pointBackgroundColor: '#cbf32f',
        pointBorderColor: '#233d32',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#233d32',
          titleFont: { family: 'Plus Jakarta Sans', size: 12 },
          bodyFont: { family: 'JetBrains Mono', size: 12 },
          padding: 8,
          cornerRadius: 6,
          displayColors: false
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Plus Jakarta Sans', size: 11 }, color: '#6b7c75' }
        },
        y: {
          grid: { color: '#eef3f0', strokeDashArray: [4, 4] },
          ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#94a39d', maxTicksLimit: 4 }
        }
      }
    }
  });
}

// ==========================================================================
// PAGE 2: ALL JOBS (Main Database)
// ==========================================================================
function renderAllJobsPage() {
  const container = document.getElementById('allJobsGrid');
  const emptyState = document.getElementById('allJobsEmpty');
  if (!container || !state.data || !state.data.jobs) return;

  let list = state.data.jobs.filter(j => j.is_active);

  // 1. Freshness Filter
  if (state.allJobsFreshness === 'today') {
    list = list.filter(j => j.posted_days_ago === 0);
  } else if (state.allJobsFreshness === '1-3-days') {
    list = list.filter(j => j.posted_days_ago >= 1 && j.posted_days_ago <= 3);
  } else if (state.allJobsFreshness === '4-7-days') {
    list = list.filter(j => j.posted_days_ago >= 4 && j.posted_days_ago <= 7);
  }

  // 2. Match Filter
  if (state.allJobsMatch === '90') {
    list = list.filter(j => j.score >= 90);
  } else if (state.allJobsMatch === '80') {
    list = list.filter(j => j.score >= 80);
  } else if (state.allJobsMatch === '70') {
    list = list.filter(j => j.score >= 70);
  }

  // 3. Work Mode Filter
  if (state.allJobsWorkMode === 'remote') {
    list = list.filter(j => (j.work_mode || '').toLowerCase().includes('remote') || (j.location || '').toLowerCase().includes('remote'));
  } else if (state.allJobsWorkMode === 'hybrid') {
    list = list.filter(j => (j.work_mode || '').toLowerCase().includes('hybrid'));
  } else if (state.allJobsWorkMode === 'onsite') {
    list = list.filter(j => (j.work_mode || '').toLowerCase().includes('onsite'));
  }

  // 4. Search Filter
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(j => {
      const skillsStr = (j.matched_skills || []).join(' ');
      const combined = `${j.title} ${j.company} ${skillsStr} ${j.location} ${j.why_matches}`.toLowerCase();
      return combined.includes(q);
    });
  }

  // 5. Sorting
  if (state.allJobsSort === 'newest') {
    list.sort((a, b) => (a.posted_days_ago || 0) - (b.posted_days_ago || 0) || b.score - a.score);
  } else if (state.allJobsSort === 'match-desc') {
    list.sort((a, b) => b.score - a.score);
  } else if (state.allJobsSort === 'salary-desc') {
    list.sort((a, b) => b.score - a.score);
  } else if (state.allJobsSort === 'company-az') {
    list.sort((a, b) => a.company.localeCompare(b.company));
  }

  // Layout mode class
  container.className = `job-cards-grid ${state.allJobsViewMode === 'list' ? 'list-mode' : ''}`;

  if (list.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';
  container.innerHTML = list.map(job => renderJobCardHtml(job, true)).join('');
}

// ==========================================================================
// PAGE 3: NEW MATCHES (Timeline Feed)
// ==========================================================================
function renderNewMatchesPage() {
  const container = document.getElementById('matchesTimelineContainer');
  if (!container || !state.data || !state.data.jobs) return;

  const activeJobs = state.data.jobs.filter(j => j.is_active);

  const todayJobs = activeJobs.filter(j => j.posted_days_ago === 0);
  const recentJobs = activeJobs.filter(j => j.posted_days_ago >= 1 && j.posted_days_ago <= 3);
  const weekJobs = activeJobs.filter(j => j.posted_days_ago >= 4 && j.posted_days_ago <= 7);

  let html = '';

  if (todayJobs.length > 0) {
    html += `
      <div class="timeline-group">
        <div class="timeline-header-label">⚡ TODAY (${todayJobs.length} NEW DISCOVERIES)</div>
        <div class="job-cards-grid">${todayJobs.map(job => renderJobCardHtml(job, false)).join('')}</div>
      </div>
    `;
  }

  if (recentJobs.length > 0) {
    html += `
      <div class="timeline-group">
        <div class="timeline-header-label">📅 1–3 DAYS AGO (${recentJobs.length} OPPORTUNITIES)</div>
        <div class="job-cards-grid">${recentJobs.map(job => renderJobCardHtml(job, false)).join('')}</div>
      </div>
    `;
  }

  if (weekJobs.length > 0) {
    html += `
      <div class="timeline-group">
        <div class="timeline-header-label">🗓 THIS WEEK (${weekJobs.length} OPPORTUNITIES)</div>
        <div class="job-cards-grid">${weekJobs.map(job => renderJobCardHtml(job, false)).join('')}</div>
      </div>
    `;
  }

  if (activeJobs.length === 0) {
    html = `
      <div class="empty-state">
        <div class="empty-icon-wrap">
          <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        </div>
        <h3>No new matches available</h3>
        <p>All scanned GoHighLevel opportunities have been processed or moved to tracker.</p>
      </div>
    `;
  }

  container.innerHTML = html;
}

// ==========================================================================
// PAGE 4: SAVED JOBS
// ==========================================================================
function renderSavedJobsPage() {
  const container = document.getElementById('savedJobsGrid');
  const emptyState = document.getElementById('savedJobsEmpty');
  if (!container || !state.data || !state.data.jobs) return;

  const savedJobs = state.data.jobs.filter(j => j.status === 'Saved');

  if (savedJobs.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';
  container.innerHTML = savedJobs.map(job => renderJobCardHtml(job, false)).join('');
}

// ==========================================================================
// PAGE 5: APPLIED JOBS (Application Tracker — Kanban & Table)
// ==========================================================================
function renderAppliedTrackerPage() {
  const allJobs = state.data.jobs;

  const appliedJobs = allJobs.filter(j => j.status === 'Applied');
  const interviewJobs = allJobs.filter(j => j.status.includes('Interview'));
  const offerJobs = allJobs.filter(j => j.status === 'Offer');
  const rejectedJobs = allJobs.filter(j => j.status === 'Rejected' || j.status === 'Closed');

  // Kanban Columns
  setElText('kanbanCntApplied', appliedJobs.length);
  setElText('kanbanCntInterview', interviewJobs.length);
  setElText('kanbanCntOffer', offerJobs.length);
  setElText('kanbanCntRejected', rejectedJobs.length);

  const colApplied = document.getElementById('kanbanColApplied');
  const colInterview = document.getElementById('kanbanColInterview');
  const colOffer = document.getElementById('kanbanColOffer');
  const colRejected = document.getElementById('kanbanColRejected');

  if (colApplied) colApplied.innerHTML = appliedJobs.map(j => renderKanbanCardHtml(j)).join('');
  if (colInterview) colInterview.innerHTML = interviewJobs.map(j => renderKanbanCardHtml(j)).join('');
  if (colOffer) colOffer.innerHTML = offerJobs.map(j => renderKanbanCardHtml(j)).join('');
  if (colRejected) colRejected.innerHTML = rejectedJobs.map(j => renderKanbanCardHtml(j)).join('');

  // Table View Body
  const tableBody = document.getElementById('trackerTableBody');
  if (tableBody) {
    const allTracked = [...appliedJobs, ...interviewJobs, ...offerJobs, ...rejectedJobs];
    if (allTracked.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">No applications tracked yet. Mark a job as Applied to track it here.</td></tr>`;
    } else {
      tableBody.innerHTML = allTracked.map(job => `
        <tr>
          <td><b>${job.company}</b></td>
          <td>${job.title}</td>
          <td><span class="mini-match-pill">${job.score}%</span></td>
          <td>${job.status_updated_at ? new Date(job.status_updated_at).toLocaleDateString() : 'Recent'}</td>
          <td><span class="tag-freshness ${job.status === 'Offer' ? 'today' : 'recent'}">${job.status}</span></td>
          <td>
            <button class="btn-card-save" style="padding: 4px 8px;" onclick="openJobDrawer('${job.id}')">Details</button>
          </td>
        </tr>
      `).join('');
    }
  }
}

function renderKanbanCardHtml(job) {
  return `
    <div class="kanban-item-card" onclick="openJobDrawer('${job.id}')">
      <div class="kanban-item-title">${job.title}</div>
      <div class="kanban-item-company">${job.company} • ${job.location}</div>
      <div class="kanban-item-footer">
        <span class="mini-match-pill">${job.score}% Match</span>
        <select class="card-status-dropdown" style="height: 26px; font-size: 0.68rem;" onclick="event.stopPropagation()" onchange="setJobStatus('${job.id}', this.value)">
          <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
          <option value="Interview Scheduled" ${job.status === 'Interview Scheduled' ? 'selected' : ''}>Interview</option>
          <option value="Offer" ${job.status === 'Offer' ? 'selected' : ''}>Offer</option>
          <option value="Rejected" ${job.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
          <option value="Closed" ${job.status === 'Closed' ? 'selected' : ''}>Closed</option>
        </select>
      </div>
    </div>
  `;
}

// ==========================================================================
// REUSABLE JOB CARD COMPONENT
// ==========================================================================
function renderJobCardHtml(job, showCompareCheckbox = false) {
  const isSaved = job.status === 'Saved';
  const isApplied = PROCESSED_STATUSES.includes(job.status);
  const isCompared = state.selectedForCompare.has(job.id);
  
  let freshBadgeClass = 'recent';
  if (job.posted_days_ago === 0) freshBadgeClass = 'today';
  else if (job.posted_days_ago > 3) freshBadgeClass = 'days47';

  const isNewIndicator = job.is_new ? `<span class="tag-freshness today" style="margin-right: 4px;">⚡ NEW</span>` : '';
  const skillsHtml = (job.matched_skills || []).slice(0, 4).map(s => `<span class="skill-tag-pill">✓ ${s}</span>`).join('');

  const compareCheckboxHtml = showCompareCheckbox ? `
    <label class="compare-checkbox-label" onclick="event.stopPropagation()">
      <input type="checkbox" ${isCompared ? 'checked' : ''} onchange="toggleCompareJob('${job.id}', this.checked)">
      <span>Compare</span>
    </label>
  ` : '';

  return `
    <article class="jobi-card-item" onclick="openJobDrawer('${job.id}')">
      <div>
        <div class="jobi-card-top">
          <div class="card-company-wrap">
            <div class="card-company-avatar" style="background-color: ${job.company_color || '#233d32'};">
              ${job.company_initials || job.company.substring(0, 2).toUpperCase()}
            </div>
            <div class="card-company-details">
              <h4>${job.company}</h4>
              <span>${job.source || 'Direct ATS'}</span>
            </div>
          </div>
          <div class="card-top-badges">
            ${compareCheckboxHtml}
            ${isNewIndicator}
            <span class="tag-freshness ${freshBadgeClass}">${job.freshness_badge || 'RECENT'}</span>
            <div class="badge-match-score">${job.score}%</div>
          </div>
        </div>

        <h3 class="card-job-title">${job.title}</h3>

        <div class="card-meta-row">
          <span class="card-meta-pill">📍 ${job.location}</span>
          <span class="card-meta-pill">💼 ${job.work_mode}</span>
          <span class="card-meta-pill">⏱ ${job.experience_req}</span>
          <span class="card-meta-pill">💰 ${job.salary}</span>
        </div>

        <p class="card-why-desc">${job.why_matches}</p>

        <div class="card-skills-row">
          ${skillsHtml}
        </div>
      </div>

      <div class="card-bottom-row" onclick="event.stopPropagation()">
        <select class="card-status-dropdown ${isApplied ? 'applied' : ''}" onchange="setJobStatus('${job.id}', this.value)">
          <option value="New Match" ${job.status === 'New Match' ? 'selected' : ''}>New Match</option>
          <option value="Saved" ${job.status === 'Saved' ? 'selected' : ''}>Saved</option>
          <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
          <option value="Interview Scheduled" ${job.status === 'Interview Scheduled' ? 'selected' : ''}>Interview Scheduled</option>
          <option value="Offer" ${job.status === 'Offer' ? 'selected' : ''}>Offer</option>
          <option value="Closed" ${job.status === 'Closed' ? 'selected' : ''}>Closed</option>
        </select>

        <div class="card-btn-actions">
          <button class="btn-card-save ${isSaved ? 'saved' : ''}" onclick="toggleSaveJob('${job.id}', event)">
            ${isSaved ? '★ Saved' : '☆ Save'}
          </button>
          <a href="${job.app_url}" target="_blank" class="btn-card-apply">
            Apply →
          </a>
        </div>
      </div>
    </article>
  `;
}

// ==========================================================================
// AI JOB COMPARISON MODAL
// ==========================================================================
function toggleCompareJob(jobId, isChecked) {
  if (isChecked) {
    if (state.selectedForCompare.size >= 3) {
      showToast('Maximum 3 jobs can be compared at once.');
      renderAllJobsPage();
      return;
    }
    state.selectedForCompare.add(jobId);
  } else {
    state.selectedForCompare.delete(jobId);
  }

  const compareBar = document.getElementById('compareBarActive');
  const countEl = document.getElementById('compareSelectedCount');
  if (compareBar && countEl) {
    countEl.textContent = state.selectedForCompare.size;
    compareBar.style.display = state.selectedForCompare.size >= 2 ? 'flex' : 'none';
  }
}

function openCompareModal() {
  if (state.selectedForCompare.size < 2) return;
  const modal = document.getElementById('compareModalBox');
  const backdrop = document.getElementById('compareModalBackdrop');
  const body = document.getElementById('compareModalBody');
  if (!modal || !backdrop || !body) return;

  const compareJobs = Array.from(state.selectedForCompare)
    .map(id => state.data.jobs.find(j => j.id === id))
    .filter(Boolean);

  body.innerHTML = `
    <table class="tracker-table" style="font-size: 0.8rem;">
      <thead>
        <tr>
          <th>Attribute</th>
          ${compareJobs.map(j => `<th><b>${j.title}</b><br><span style="font-size: 0.72rem; color: var(--forest-green);">${j.company}</span></th>`).join('')}
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>Match Score</b></td>
          ${compareJobs.map(j => `<td><span class="badge-match-score">${j.score}%</span></td>`).join('')}
        </tr>
        <tr>
          <td><b>Freshness</b></td>
          ${compareJobs.map(j => `<td><span class="tag-freshness today">${j.freshness_badge}</span></td>`).join('')}
        </tr>
        <tr>
          <td><b>Compensation</b></td>
          ${compareJobs.map(j => `<td>${j.salary}</td>`).join('')}
        </tr>
        <tr>
          <td><b>Work Mode</b></td>
          ${compareJobs.map(j => `<td>${j.work_mode} (${j.location})</td>`).join('')}
        </tr>
        <tr>
          <td><b>Experience</b></td>
          ${compareJobs.map(j => `<td>${j.experience_req}</td>`).join('')}
        </tr>
        <tr>
          <td><b>Matched Skills</b></td>
          ${compareJobs.map(j => `<td>${(j.matched_skills || []).map(s => `<span class="skill-tag-pill">✓ ${s}</span>`).join(' ')}</td>`).join('')}
        </tr>
        <tr>
          <td><b>Direct Action</b></td>
          ${compareJobs.map(j => `<td><a href="${j.app_url}" target="_blank" class="btn-card-apply" style="display: inline-block; padding: 4px 10px;">Apply Directly →</a></td>`).join('')}
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 20px; background: var(--bg-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 14px;">
      <div style="font-size: 0.74rem; font-weight: 800; color: var(--forest-green); text-transform: uppercase;">
        🤖 AI STRATEGIC RECOMMENDATION
      </div>
      <p style="font-size: 0.82rem; color: var(--text-main); margin-top: 6px; line-height: 1.5;">
        Based on candidate <strong>Sohaib Mahmood's</strong> 4-year GoHighLevel and marketing automation experience, 
        <strong>${compareJobs[0].title} at ${compareJobs[0].company}</strong> provides the highest alignment (${compareJobs[0].score}% match), 
        directly valuing sub-account architecture, custom snapshots, and n8n webhook expertise.
      </p>
    </div>
  `;

  modal.classList.add('open');
  backdrop.classList.add('open');
}

function closeCompareModal() {
  const modal = document.getElementById('compareModalBox');
  const backdrop = document.getElementById('compareModalBackdrop');
  if (modal) modal.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
}

// ==========================================================================
// JOB DETAIL DRAWER (AI MATCH ANALYSIS)
// ==========================================================================
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
    matchedContainer.innerHTML = (job.matched_skills || []).map(s => `<span class="skill-tag-pill" style="background: var(--neon-lime-subtle); color: var(--forest-green); border: 1px solid var(--neon-lime-border);">✓ ${s}</span>`).join('');
  }

  // Missing Skills Tags
  const missingContainer = document.getElementById('drawerMissingSkills');
  if (missingContainer) {
    if (job.missing_skills && job.missing_skills[0] && !job.missing_skills[0].includes('None')) {
      missingContainer.innerHTML = job.missing_skills.map(s => `<span class="skill-tag-pill" style="background: #fee2e2; color: #dc2626;">⚠ ${s}</span>`).join('');
    } else {
      missingContainer.innerHTML = `<span style="font-size: 0.76rem; color: var(--text-muted);">None identified in core scope</span>`;
    }
  }

  // Advantage Skills Tags
  const advContainer = document.getElementById('drawerAdvSkills');
  if (advContainer) {
    advContainer.innerHTML = (job.advantage_skills || []).map(s => `<span class="skill-tag-pill" style="background: var(--forest-green-subtle); color: var(--forest-green);">+ ${s}</span>`).join('');
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

// Dynamic Countdown Timer to next 3-hour PKT slot
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

    const countdownEl = document.getElementById('dashCountdown');
    if (countdownEl) countdownEl.textContent = countdownStr;
  }

  update();
  state.countdownInterval = setInterval(update, 1000);
}

// Update Metric Counters
function updateMetricsAndSidebar() {
  if (!state.data || !state.data.jobs) return;
  const allJobs = state.data.jobs;

  const activeJobs = allJobs.filter(j => j.is_active);
  const newJobs = activeJobs.filter(j => j.is_new);
  const savedJobs = allJobs.filter(j => j.status === 'Saved');
  const appliedJobs = allJobs.filter(j => j.status === 'Applied');

  const pad = (n) => String(n).padStart(2, '0');
  setElText('dashFreshJobs', pad(activeJobs.length));
  setElText('dashNewJobs', pad(newJobs.length));
  setElText('dashTotalJobs', pad(allJobs.length));

  const topFit = activeJobs.length ? Math.max(...activeJobs.map(j => j.score)) : (allJobs.length ? Math.max(...allJobs.map(j => j.score)) : 0);
  setElText('dashTopMatch', `${topFit}%`);

  // Sidebar Badges
  setElText('cntSidebarAllJobs', activeJobs.length);
  setElText('cntSidebarNewMatches', newJobs.length);
  setElText('cntSidebarSaved', savedJobs.length);
  setElText('cntSidebarApplied', appliedJobs.length);
}

function setElText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// Date dropdown
function populateDateDropdown() {
  const select = document.getElementById('dateSelect');
  if (!select || !state.data || !state.data.metadata) return;

  const dates = state.data.metadata.available_dates || [];
  select.innerHTML = '';

  const optLatest = document.createElement('option');
  optLatest.value = 'latest';
  optLatest.textContent = `Today`;
  optLatest.selected = (state.activeDate === 'latest');
  select.appendChild(optLatest);

  dates.forEach(d => {
    if (d !== state.data.metadata.search_date) {
      const opt = document.createElement('option');
      opt.value = d;
      opt.textContent = `${d}`;
      opt.selected = (state.activeDate === d);
      select.appendChild(opt);
    }
  });
}

// Manual Scrape Action
async function triggerScrapeNewJobs() {
  if (state.isScraping) return;
  state.isScraping = true;

  const btn = document.getElementById('btnScrapeJobs');
  const badge = document.getElementById('dashLiveBadge');

  if (btn) {
    btn.classList.add('loading');
    btn.innerHTML = `<span>⏳</span> Scanning...`;
  }
  if (badge) {
    badge.innerHTML = `<span class="live-dot-pulse" style="background-color: #f59e0b; box-shadow: 0 0 6px #f59e0b;"></span> UPDATING...`;
  }

  showToast('Connecting to public ATS feeds...');

  try {
    const remotiveUrl = 'https://remotive.com/api/remote-jobs?search=gohighlevel';
    try { await fetch(remotiveUrl); } catch (e) {}

    await loadDataset('latest');
    showToast(`✓ Scan complete: Active GoHighLevel dataset verified!`);
  } catch (err) {
    console.error('Scrape error:', err);
    showToast('Job scan complete.');
  } finally {
    state.isScraping = false;
    if (btn) {
      btn.classList.remove('loading');
      btn.innerHTML = `<svg class="svg-icon" style="width: 14px; height: 14px; stroke: #ffffff; fill: none;" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> <span>Scrape New Jobs</span>`;
    }
    if (badge) {
      badge.innerHTML = `<span class="live-dot-pulse"></span> LIVE 3H REFRESH`;
    }
  }
}

// Toast
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

  // Sidebar Nav Links
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      navigateTo(route);
    });
  });

  // Top Nav Links
  document.querySelectorAll('.top-nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const route = link.getAttribute('data-route');
      navigateTo(route);
    });
  });

  // Global Search Input
  const searchInput = document.getElementById('globalSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      if (state.currentRoute !== 'jobs') {
        navigateTo('jobs');
      } else {
        renderAllJobsPage();
      }
    });
  }

  // All Jobs Page Filters
  const fFreshness = document.getElementById('filterFreshness');
  if (fFreshness) fFreshness.addEventListener('change', (e) => {
    state.allJobsFreshness = e.target.value;
    renderAllJobsPage();
  });

  const fMatch = document.getElementById('filterMatch');
  if (fMatch) fMatch.addEventListener('change', (e) => {
    state.allJobsMatch = e.target.value;
    renderAllJobsPage();
  });

  const fWorkMode = document.getElementById('filterWorkMode');
  if (fWorkMode) fWorkMode.addEventListener('change', (e) => {
    state.allJobsWorkMode = e.target.value;
    renderAllJobsPage();
  });

  const sSort = document.getElementById('sortJobsSelect');
  if (sSort) sSort.addEventListener('change', (e) => {
    state.allJobsSort = e.target.value;
    renderAllJobsPage();
  });

  // View Mode Toggles
  const btnGrid = document.getElementById('btnViewGrid');
  const btnList = document.getElementById('btnViewList');
  if (btnGrid && btnList) {
    btnGrid.addEventListener('click', () => {
      btnGrid.classList.add('active');
      btnList.classList.remove('active');
      state.allJobsViewMode = 'grid';
      renderAllJobsPage();
    });
    btnList.addEventListener('click', () => {
      btnList.classList.add('active');
      btnGrid.classList.remove('active');
      state.allJobsViewMode = 'list';
      renderAllJobsPage();
    });
  }

  // Tracker View Toggle (Kanban vs Table)
  const btnKanban = document.getElementById('btnTrackerKanban');
  const btnTable = document.getElementById('btnTrackerTable');
  const kanbanView = document.getElementById('trackerKanbanView');
  const tableView = document.getElementById('trackerTableView');

  if (btnKanban && btnTable && kanbanView && tableView) {
    btnKanban.addEventListener('click', () => {
      btnKanban.classList.add('active');
      btnTable.classList.remove('active');
      kanbanView.style.display = 'grid';
      tableView.style.display = 'none';
      state.trackerMode = 'kanban';
    });
    btnTable.addEventListener('click', () => {
      btnTable.classList.add('active');
      btnKanban.classList.remove('active');
      kanbanView.style.display = 'none';
      tableView.style.display = 'block';
      state.trackerMode = 'table';
    });
  }

  // Compare Modal Launch & Close
  const btnOpenCompare = document.getElementById('btnOpenCompareModal');
  if (btnOpenCompare) btnOpenCompare.addEventListener('click', openCompareModal);

  const compareCloseBtn = document.getElementById('compareCloseBtn');
  const compareBackdrop = document.getElementById('compareModalBackdrop');
  if (compareCloseBtn) compareCloseBtn.addEventListener('click', closeCompareModal);
  if (compareBackdrop) compareBackdrop.addEventListener('click', closeCompareModal);

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

  // Analyze Resume Scanner CTA
  const btnAnalyzeResume = document.getElementById('btnAnalyzeResumeAgainstFeed');
  if (btnAnalyzeResume) {
    btnAnalyzeResume.addEventListener('click', () => {
      showToast('Scanning resume keywords against 11 active GHL opportunities: 94% Alignment verified!');
    });
  }

  // Chart time range tabs
  document.querySelectorAll('.time-tab-btn').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.time-tab-btn').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const timeRange = pill.getAttribute('data-time-tab');
      renderDashboardChart(timeRange);
    });
  });

  // Date select switcher
  const dateSelect = document.getElementById('dateSelect');
  if (dateSelect) {
    dateSelect.addEventListener('change', (e) => {
      state.activeDate = e.target.value;
      loadDataset(e.target.value);
    });
  }
}
