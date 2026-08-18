/**
 * Gemini Spark AI Career Intelligence Dashboard
 * Dynamic Client Application & Data Manager
 */

let appState = {
  activeDate: 'latest',
  activeTab: 'all',
  searchQuery: '',
  roleFilter: 'all',
  prioFilter: 'all',
  statusFilter: 'all',
  sortMode: 'score-desc',
  data: null,
  savedStatuses: {}
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  loadSavedStatuses();
  await loadDashboardData('latest');
  setupEventListeners();
});

// Load persistent statuses from localStorage
function loadSavedStatuses() {
  try {
    const raw = localStorage.getItem('ghl_career_job_statuses');
    appState.savedStatuses = raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.warn('localStorage access failed:', e);
    appState.savedStatuses = {};
  }
}

// Save status change
function updateJobStatus(jobId, newStatus) {
  appState.savedStatuses[jobId] = newStatus;
  try {
    localStorage.setItem('ghl_career_job_statuses', JSON.stringify(appState.savedStatuses));
  } catch (e) {
    console.warn('Failed to persist status:', e);
  }
  
  if (appState.data && appState.data.jobs) {
    const target = appState.data.jobs.find(j => j.id === jobId);
    if (target) target.status = newStatus;
  }
  renderDashboard();
}

// Fetch dataset dynamically
async function loadDashboardData(dateKey = 'latest') {
  const url = dateKey === 'latest' ? './data/latest.json' : `./data/history/${dateKey}.json`;
  
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    appState.data = await res.json();
  } catch (err) {
    console.warn(`Dynamic fetch failed for ${url}, attempting fallback...`, err);
    if (window.FALLBACK_DATA) {
      appState.data = window.FALLBACK_DATA;
    } else {
      showErrorState(err.message);
      return;
    }
  }

  // Inject persistent statuses into loaded data
  if (appState.data && appState.data.jobs) {
    appState.data.jobs.forEach(job => {
      job.status = appState.savedStatuses[job.id] || 'New Match';
    });
  }

  updateHeaderAndKPIs();
  populateDateDropdown();
  renderDashboard();
}

// Populate Date History Dropdown
function populateDateDropdown() {
  const select = document.getElementById('dateSelect');
  if (!select || !appState.data || !appState.data.metadata) return;

  const dates = appState.data.metadata.available_dates || ['2026-08-19'];
  select.innerHTML = '';

  const optLatest = document.createElement('option');
  optLatest.value = 'latest';
  optLatest.textContent = `Today (${appState.data.metadata.search_date})`;
  optLatest.selected = (appState.activeDate === 'latest');
  select.appendChild(optLatest);

  dates.forEach(d => {
    if (d !== appState.data.metadata.search_date) {
      const opt = document.createElement('option');
      opt.value = d;
      opt.textContent = `Report: ${d}`;
      opt.selected = (appState.activeDate === d);
      select.appendChild(opt);
    }
  });
}

// Update Header & KPI counters
function updateHeaderAndKPIs() {
  const meta = appState.data.metadata;
  const kpis = meta.kpis;
  const candidate = meta.candidate;

  // Header texts
  const candTitle = document.getElementById('candidateTitle');
  if (candTitle) candTitle.textContent = candidate.title;

  const searchDateBadge = document.getElementById('searchDateBadge');
  if (searchDateBadge) searchDateBadge.textContent = meta.search_date;

  // KPIs
  const elDiscovered = document.getElementById('kpiDiscovered');
  if (elDiscovered) elDiscovered.textContent = kpis.relevant_qualified;

  const elTopMatch = document.getElementById('kpiTopMatch');
  if (elTopMatch) elTopMatch.textContent = `${kpis.top_match_score}%`;

  const elAvgMatch = document.getElementById('kpiAvgMatch');
  if (elAvgMatch) elAvgMatch.textContent = `${kpis.avg_match_score}%`;

  const elPriority1 = document.getElementById('kpiPriority1');
  if (elPriority1) elPriority1.textContent = kpis.priority_1_apply_count;

  const elRemotePct = document.getElementById('kpiRemotePct');
  if (elRemotePct) elRemotePct.textContent = `${kpis.remote_worldwide_percentage}%`;
}

// Main Render Function
function renderDashboard() {
  if (!appState.data) return;

  renderJobs();
  renderSkillIntelligence();
}

// Render Job Cards with Filter & Search logic
function renderJobs() {
  const container = document.getElementById('jobsContainer');
  const emptyState = document.getElementById('emptyState');
  const visibleCount = document.getElementById('visibleCount');
  if (!container) return;

  let list = [...appState.data.jobs];

  // Apply tab constraint
  if (appState.activeTab === 'top5') {
    list = list.filter(j => j.rank <= 5);
  }

  // Search filter
  if (appState.searchQuery.trim()) {
    const q = appState.searchQuery.toLowerCase();
    list = list.filter(j => {
      const corpus = `${j.title} ${j.company} ${j.matched_skills.join(' ')} ${j.why_matches} ${j.location}`.toLowerCase();
      return corpus.includes(q);
    });
  }

  // Role Category filter
  if (appState.roleFilter !== 'all') {
    list = list.filter(j => j.role_category === appState.roleFilter);
  }

  // Priority filter
  if (appState.prioFilter !== 'all') {
    list = list.filter(j => j.priority_class === appState.prioFilter);
  }

  // Status filter
  if (appState.statusFilter !== 'all') {
    list = list.filter(j => j.status === appState.statusFilter);
  }

  // Sorting
  list.sort((a, b) => {
    if (appState.sortMode === 'score-desc') return b.score - a.score;
    if (appState.sortMode === 'score-asc') return a.score - b.score;
    if (appState.sortMode === 'rank-asc') return a.rank - b.rank;
    if (appState.sortMode === 'title-asc') return a.title.localeCompare(b.title);
    if (appState.sortMode === 'company-asc') return a.company.localeCompare(b.company);
    return 0;
  });

  if (visibleCount) {
    visibleCount.textContent = `${list.length} ${list.length === 1 ? 'Opportunity' : 'Opportunities'}`;
  }

  if (list.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  } else {
    if (emptyState) emptyState.style.display = 'none';
  }

  container.innerHTML = list.map(job => {
    const isTop5 = job.rank <= 5;
    const scoreClass = job.score >= 90 ? 'score-excellent' : (job.score >= 80 ? 'score-strong' : 'score-good');

    return `
      <article class="job-card ${isTop5 ? 'is-top5' : ''}" id="${job.id}">
        <div class="card-header-flex">
          <div class="card-title-group">
            <div style="font-size: 0.8rem; font-weight: 700; color: ${isTop5 ? 'var(--emerald)' : 'var(--text-muted)'}; margin-bottom: 2px;">
              #${job.rank} Ranked Match ${isTop5 ? '• ⭐ Top Strategic Shortlist' : ''}
            </div>
            <h3>${job.title}</h3>
            <div class="card-company-meta">
              🏢 ${job.company} <span>•</span> <span>${job.source}</span>
            </div>
          </div>
          <div class="score-badge-box ${scoreClass}">
            <span class="score-num">${job.score}%</span>
            <span class="score-tag">${job.category.replace(' Match', '')}</span>
          </div>
        </div>

        <div class="card-pill-row">
          <span class="info-pill ${job.priority_class}">${job.priority_icon} ${job.priority}</span>
          <span class="info-pill">📍 ${job.location} (${job.remote_eligibility})</span>
          <span class="info-pill">💼 ${job.work_mode} (${job.employment_type})</span>
          <span class="info-pill">⏱ Req: ${job.experience_req} (You: ${job.candidate_exp})</span>
          <span class="info-pill">💰 ${job.salary}</span>
        </div>

        <div class="card-desc-block">
          <div class="card-desc-label">Why This Matches Your Experience</div>
          <p class="card-desc-text">${job.why_matches}</p>
        </div>

        <div class="card-desc-block">
          <div class="card-desc-label">Matched Skills</div>
          <div class="skill-chips-wrap">
            ${job.matched_skills.map(s => `<span class="skill-tag skill-matched">✓ ${s}</span>`).join('')}
          </div>
        </div>

        ${job.advantage_skills && job.advantage_skills.length > 0 ? `
          <div class="card-desc-block">
            <div class="card-desc-label">Advantage Differentiators</div>
            <div class="skill-chips-wrap">
              ${job.advantage_skills.map(s => `<span class="skill-tag skill-adv">+ ${s}</span>`).join('')}
            </div>
          </div>
        ` : ''}

        <div class="card-desc-block">
          <div class="card-desc-label">Considerations & Gaps</div>
          <p class="card-desc-text" style="color: #64748b; font-size: 0.85rem;">
            ${job.concerns || 'No major blockers identified.'}
            ${job.missing_skills && job.missing_skills[0] !== 'None identified in core scope' && job.missing_skills[0] !== 'None for listed technical scope' && job.missing_skills[0] !== 'None identified' ? `<br><b style="color: #e11d48;">Skill Gap:</b> ${job.missing_skills.join(', ')}` : ''}
          </p>
        </div>

        <div class="card-bottom-bar">
          <div class="status-dropdown-wrap">
            <label for="status-${job.id}">Status:</label>
            <select class="status-select-input" id="status-${job.id}" onchange="updateJobStatus('${job.id}', this.value)">
              <option value="New Match" ${job.status === 'New Match' ? 'selected' : ''}>New Match</option>
              <option value="Saved" ${job.status === 'Saved' ? 'selected' : ''}>Saved</option>
              <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
              <option value="Interview Scheduled" ${job.status === 'Interview Scheduled' ? 'selected' : ''}>Interview Scheduled</option>
              <option value="Interview Completed" ${job.status === 'Interview Completed' ? 'selected' : ''}>Interview Completed</option>
              <option value="Offer" ${job.status === 'Offer' ? 'selected' : ''}>Offer</option>
              <option value="Rejected" ${job.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
              <option value="Closed" ${job.status === 'Closed' ? 'selected' : ''}>Closed</option>
            </select>
          </div>
          <div class="card-ctas">
            <a href="${job.original_url}" target="_blank" class="btn-secondary-view">View Listing</a>
            <a href="${job.app_url}" target="_blank" class="btn-primary-apply">Apply Directly →</a>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// Render Market Intelligence Charts & Matrix
function renderSkillIntelligence() {
  const insights = appState.data.market_insights;
  const skillsContainer = document.getElementById('demandSkillsContainer');
  if (!skillsContainer || !insights) return;

  skillsContainer.innerHTML = insights.most_in_demand_skills.map(item => `
    <div class="freq-bar-item">
      <div class="freq-bar-label">
        <span>${item.skill}</span>
        <span><b>${item.frequency_pct}</b> (${item.count} jobs)</span>
      </div>
      <div class="freq-bar-track">
        <div class="freq-bar-fill" style="width: ${item.frequency_pct}"></div>
      </div>
    </div>
  `).join('');
}

// Event Listeners Setup
function setupEventListeners() {
  // Search input
  const searchInput = document.getElementById('searchBox');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      appState.searchQuery = e.target.value;
      renderJobs();
    });
  }

  // Sort select
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      appState.sortMode = e.target.value;
      renderJobs();
    });
  }

  // Date select
  const dateSelect = document.getElementById('dateSelect');
  if (dateSelect) {
    dateSelect.addEventListener('change', (e) => {
      appState.activeDate = e.target.value;
      loadDashboardData(e.target.value);
    });
  }

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.activeTab = btn.getAttribute('data-tab');

      // Toggle views
      const intelSection = document.getElementById('intelligenceSection');
      const jobsSection = document.getElementById('jobsSection');
      if (appState.activeTab === 'intelligence') {
        if (intelSection) intelSection.style.display = 'block';
        if (jobsSection) jobsSection.style.display = 'none';
      } else {
        if (intelSection) intelSection.style.display = 'none';
        if (jobsSection) jobsSection.style.display = 'block';
        renderJobs();
      }
    });
  });

  // Filter Chips
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-filter-type');
      const val = chip.getAttribute('data-filter');

      document.querySelectorAll(`.chip[data-filter-type="${type}"]`).forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      if (type === 'role') appState.roleFilter = val;
      if (type === 'prio') appState.prioFilter = val;
      if (type === 'status') appState.statusFilter = val;

      renderJobs();
    });
  });
}

function showErrorState(msg) {
  const container = document.getElementById('jobsContainer');
  if (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h3 style="color: #e11d48; margin-bottom: 8px;">Failed to Load Live Job Data</h3>
        <p style="color: #64748b; font-size: 0.9rem;">${msg}</p>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 12px;">If running from local disk without a web server, ensure fallback dataset is active.</p>
      </div>
    `;
  }
}
