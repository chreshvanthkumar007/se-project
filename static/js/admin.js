/**
 * Administrator Dashboard, Analytics Charts, & Feedback Management
 */

let sentimentChartInstance = null;
let categoryChartInstance = null;
let ratingChartInstance = null;
let trendChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('admin-stats-container')) {
    initAdminDashboard();
  }

  if (document.getElementById('feedback-table-body')) {
    initFeedbackManagement();
  }
});

// -------------------------------------------------------------
// Admin Dashboard
// -------------------------------------------------------------
async function initAdminDashboard() {
  await loadDashboardKPIs();
  await loadDashboardCharts();
  await loadRecentFeedbackSnippet();
}

async function loadDashboardKPIs() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    if (data.success && data.stats) {
      const s = data.stats;
      document.getElementById('kpi-total-students').textContent = s.total_students;
      document.getElementById('kpi-total-feedback').textContent = s.total_feedback;
      document.getElementById('kpi-avg-rating').textContent = s.avg_rating;
      document.getElementById('kpi-pos-pct').textContent = `${s.positive_pct}%`;
      document.getElementById('kpi-neg-pct').textContent = `${s.negative_pct}%`;
      document.getElementById('kpi-neu-pct').textContent = `${s.neutral_pct}%`;
      document.getElementById('kpi-pending').textContent = s.pending_count;
      document.getElementById('kpi-most-issue').textContent = s.most_reported_issue || 'None';
    }
  } catch (err) {
    console.error('Failed to load admin KPIs:', err);
  }
}

async function loadDashboardCharts() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();
    if (!data.success || !data.charts) return;

    const charts = data.charts;

    // 1. Sentiment Distribution (Doughnut)
    const ctxSent = document.getElementById('chart-sentiment');
    if (ctxSent) {
      if (sentimentChartInstance) sentimentChartInstance.destroy();
      sentimentChartInstance = new Chart(ctxSent, {
        type: 'doughnut',
        data: {
          labels: charts.sentiment.labels,
          datasets: [{
            data: charts.sentiment.data,
            backgroundColor: ['#059669', '#dc2626', '#64748b', '#d97706'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Plus Jakarta Sans', size: 12 } } }
          },
          cutout: '65%'
        }
      });
    }

    // 2. Feedback by Category (Bar)
    const ctxCat = document.getElementById('chart-categories');
    if (ctxCat) {
      if (categoryChartInstance) categoryChartInstance.destroy();
      categoryChartInstance = new Chart(ctxCat, {
        type: 'bar',
        data: {
          labels: charts.categories.labels,
          datasets: [{
            label: 'Feedback Count',
            data: charts.categories.data,
            backgroundColor: '#3b82f6',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true, ticks: { precision: 0, font: { family: 'Plus Jakarta Sans' } } },
            x: { ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } } }
          }
        }
      });
    }

    // 3. Average Rating by Category (Horizontal Bar)
    const ctxRate = document.getElementById('chart-ratings');
    if (ctxRate) {
      if (ratingChartInstance) ratingChartInstance.destroy();
      ratingChartInstance = new Chart(ctxRate, {
        type: 'bar',
        data: {
          labels: charts.ratings.labels,
          datasets: [{
            label: 'Avg Rating (1-5)',
            data: charts.ratings.data,
            backgroundColor: '#f59e0b',
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { min: 0, max: 5, ticks: { stepSize: 1, font: { family: 'Plus Jakarta Sans' } } },
            y: { ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } } }
          }
        }
      });
    }

    // 4. Feedback Trend (Line)
    const ctxTrend = document.getElementById('chart-trends');
    if (ctxTrend) {
      if (trendChartInstance) trendChartInstance.destroy();
      trendChartInstance = new Chart(ctxTrend, {
        type: 'line',
        data: {
          labels: charts.trends.labels,
          datasets: [{
            label: 'Submissions',
            data: charts.trends.counts,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#2563eb'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true, ticks: { precision: 0, font: { family: 'Plus Jakarta Sans' } } },
            x: { ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } } }
          }
        }
      });
    }

  } catch (err) {
    console.error('Failed to load chart analytics:', err);
  }
}

async function loadRecentFeedbackSnippet() {
  const tbody = document.getElementById('recent-feedback-tbody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/feedback?per_page=5');
    const data = await res.json();
    if (data.success && data.data && data.data.items) {
      const items = data.data.items;
      if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-3">No feedback available.</td></tr>';
        return;
      }
      tbody.innerHTML = items.map(fb => `
        <tr>
          <td><strong>#${fb.id}</strong></td>
          <td>${escapeHtml(fb.student_name)} <span class="text-muted">(${fb.student_roll_no || 'N/A'})</span></td>
          <td><span class="analysis-tag">${fb.category}</span></td>
          <td>${renderStars(fb.rating)}</td>
          <td>${renderSentimentBadge(fb.sentiment)}</td>
          <td>${formatDate(fb.created_at)}</td>
          <td>
            <button class="btn btn-outline btn-sm" onclick="viewAnalysisDetails(${fb.id})">
              <i class="bi bi-eye"></i> View
            </button>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load recent feedback:', err);
  }
}

// -------------------------------------------------------------
// Admin Feedback Management Page
// -------------------------------------------------------------
let currentFilters = {
  search: '',
  category: 'all',
  sentiment: 'all',
  rating: 'all',
  department: 'all',
  page: 1,
  per_page: 10
};

async function initFeedbackManagement() {
  await loadFilterOptions();
  setupFilterListeners();
  await fetchFeedbackList();
}

async function loadFilterOptions() {
  try {
    const [catRes, deptRes] = await Promise.all([
      fetch('/api/categories'),
      fetch('/api/departments')
    ]);
    const catData = await catRes.json();
    const deptData = await deptRes.json();

    const catSelect = document.getElementById('filter-category');
    if (catSelect && catData.success) {
      catData.categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.category_name;
        opt.textContent = c.category_name;
        catSelect.appendChild(opt);
      });
    }

    const deptSelect = document.getElementById('filter-department');
    if (deptSelect && deptData.success) {
      deptData.departments.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        deptSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error('Error loading filter options:', err);
  }
}

function setupFilterListeners() {
  const searchInput = document.getElementById('filter-search');
  const catSelect = document.getElementById('filter-category');
  const sentSelect = document.getElementById('filter-sentiment');
  const rateSelect = document.getElementById('filter-rating');
  const deptSelect = document.getElementById('filter-department');
  const resetBtn = document.getElementById('filter-reset-btn');

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentFilters.search = searchInput.value.trim();
        currentFilters.page = 1;
        fetchFeedbackList();
      }, 300);
    });
  }

  [catSelect, sentSelect, rateSelect, deptSelect].forEach(select => {
    if (select) {
      select.addEventListener('change', () => {
        currentFilters[select.dataset.field] = select.value;
        currentFilters.page = 1;
        fetchFeedbackList();
      });
    }
  });

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (catSelect) catSelect.value = 'all';
      if (sentSelect) sentSelect.value = 'all';
      if (rateSelect) rateSelect.value = 'all';
      if (deptSelect) deptSelect.value = 'all';

      currentFilters = {
        search: '',
        category: 'all',
        sentiment: 'all',
        rating: 'all',
        department: 'all',
        page: 1,
        per_page: 10
      };
      fetchFeedbackList();
    });
  }
}

async function fetchFeedbackList() {
  const tbody = document.getElementById('feedback-table-body');
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="10" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span> Loading records...</td></tr>`;

  const query = new URLSearchParams(currentFilters).toString();
  try {
    const res = await fetch(`/api/feedback?${query}`);
    const data = await res.json();

    if (data.success && data.data) {
      renderFeedbackTable(data.data.items, tbody);
      renderPagination(data.data);
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="10" class="text-center py-4 text-danger">Failed to fetch feedback records.</td></tr>`;
  }
}

function renderFeedbackTable(items, tbody) {
  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-search empty-state-icon"></i>
            <div class="empty-state-title">No Matching Feedback Records</div>
            <div class="empty-state-desc">Try clearing your search query or adjusting your filters.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map(fb => `
    <tr>
      <td><strong>#${fb.id}</strong></td>
      <td>
        <div style="font-weight: 600; color: var(--navy-900);">${escapeHtml(fb.student_name)}</div>
        <div style="font-size: 0.72rem; color: var(--gray-500);">${fb.student_roll_no || 'N/A'}</div>
      </td>
      <td><span style="font-size: 0.8rem; color: var(--gray-600);">${escapeHtml(fb.department || 'General')}</span></td>
      <td><span class="analysis-tag">${fb.category}</span></td>
      <td>${renderStars(fb.rating)}</td>
      <td style="max-width: 240px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(fb.feedback_text)}">
        ${escapeHtml(fb.feedback_text)}
      </td>
      <td>${renderSentimentBadge(fb.sentiment)}</td>
      <td>
        <span style="font-weight: 700; font-size: 0.8rem; color: ${Number(fb.sentiment_score) >= 0 ? 'var(--sentiment-pos)' : 'var(--sentiment-neg)'};">
          ${Number(fb.sentiment_score) > 0 ? '+' : ''}${Number(fb.sentiment_score).toFixed(2)}
        </span>
      </td>
      <td><span style="font-size: 0.75rem; color: var(--gray-500);">${formatDate(fb.created_at)}</span></td>
      <td>
        <div style="display: flex; gap: 0.35rem;">
          <button class="btn btn-outline btn-sm" onclick="viewAnalysisDetails(${fb.id})" title="View Complete AI Analysis">
            <i class="bi bi-eye"></i>
          </button>
          <button class="btn btn-danger btn-sm" onclick="confirmDeleteFeedback(${fb.id})" title="Delete Feedback">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

function renderPagination(pageData) {
  const container = document.getElementById('pagination-container');
  if (!container) return;

  const total = pageData.total;
  const page = pageData.page;
  const totalPages = pageData.total_pages;

  const start = total === 0 ? 0 : (page - 1) * pageData.per_page + 1;
  const end = Math.min(page * pageData.per_page, total);

  container.innerHTML = `
    <div class="pagination-info">
      Showing <strong>${start}</strong> - <strong>${end}</strong> of <strong>${total}</strong> records
    </div>
    <div class="pagination-buttons">
      <button class="btn btn-outline btn-sm" ${page <= 1 ? 'disabled' : ''} onclick="goToPage(${page - 1})">
        <i class="bi bi-chevron-left"></i> Previous
      </button>
      <span style="font-size: 0.82rem; font-weight: 600; padding: 0.35rem 0.65rem; background: var(--gray-100); border-radius: var(--radius-sm);">
        Page ${page} of ${totalPages}
      </span>
      <button class="btn btn-outline btn-sm" ${page >= totalPages ? 'disabled' : ''} onclick="goToPage(${page + 1})">
        Next <i class="bi bi-chevron-right"></i>
      </button>
    </div>
  `;
}

function goToPage(p) {
  currentFilters.page = p;
  fetchFeedbackList();
}

let feedbackIdToDelete = null;

function confirmDeleteFeedback(id) {
  feedbackIdToDelete = id;
  const delMsg = document.getElementById('delete-modal-msg');
  if (delMsg) delMsg.textContent = `Are you sure you want to permanently delete feedback record #${id}? This action cannot be undone.`;
  openModal('delete-confirm-modal');
}

async function executeDeleteFeedback() {
  if (!feedbackIdToDelete) return;
  try {
    const res = await fetch(`/api/feedback/${feedbackIdToDelete}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Deleted', 'Feedback record was successfully removed.', 'success');
      closeModal('delete-confirm-modal');
      fetchFeedbackList();
    } else {
      showToast('Error', data.message || 'Failed to delete record.', 'error');
    }
  } catch (err) {
    showToast('Error', 'Network error while attempting deletion.', 'error');
  } finally {
    feedbackIdToDelete = null;
  }
}
