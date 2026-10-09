/**
 * Reports & Export Management Module
 */

document.addEventListener('DOMContentLoaded', () => {
  initReports();
});

async function initReports() {
  await loadReportFilters();
  setupReportListeners();
  // Generate default report on load
  generateReport();
}

async function loadReportFilters() {
  try {
    const [catRes, deptRes] = await Promise.all([
      fetch('/api/categories'),
      fetch('/api/departments')
    ]);
    const catData = await catRes.json();
    const deptData = await deptRes.json();

    const catSelect = document.getElementById('report-category');
    if (catSelect && catData.success) {
      catData.categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.category_name;
        opt.textContent = c.category_name;
        catSelect.appendChild(opt);
      });
    }

    const deptSelect = document.getElementById('report-department');
    if (deptSelect && deptData.success) {
      deptData.departments.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        deptSelect.appendChild(opt);
      });
    }
  } catch (e) {
    console.error('Error loading report filter dropdowns:', e);
  }
}

function getReportFilterParams() {
  return new URLSearchParams({
    start_date: document.getElementById('report-start-date')?.value || '',
    end_date: document.getElementById('report-end-date')?.value || '',
    department: document.getElementById('report-department')?.value || 'all',
    category: document.getElementById('report-category')?.value || 'all',
    sentiment: document.getElementById('report-sentiment')?.value || 'all',
    rating: document.getElementById('report-rating')?.value || 'all'
  });
}

function setupReportListeners() {
  const genBtn = document.getElementById('generate-report-btn');
  const exportBtn = document.getElementById('export-csv-btn');
  const printBtn = document.getElementById('print-report-btn');
  const resetBtn = document.getElementById('report-reset-btn');

  if (genBtn) {
    genBtn.addEventListener('click', () => generateReport());
  }

  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const params = getReportFilterParams().toString();
      window.location.href = `/api/reports/export?${params}`;
    });
  }

  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (document.getElementById('report-start-date')) document.getElementById('report-start-date').value = '';
      if (document.getElementById('report-end-date')) document.getElementById('report-end-date').value = '';
      if (document.getElementById('report-department')) document.getElementById('report-department').value = 'all';
      if (document.getElementById('report-category')) document.getElementById('report-category').value = 'all';
      if (document.getElementById('report-sentiment')) document.getElementById('report-sentiment').value = 'all';
      if (document.getElementById('report-rating')) document.getElementById('report-rating').value = 'all';
      generateReport();
    });
  }
}

async function generateReport() {
  const tbody = document.getElementById('report-table-body');
  const genBtn = document.getElementById('generate-report-btn');

  if (genBtn) {
    genBtn.disabled = true;
    genBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';
  }

  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span> Analyzing and compiling report...</td></tr>';
  }

  const query = getReportFilterParams().toString();

  try {
    const res = await fetch(`/api/reports?${query}`);
    const data = await res.json();

    if (data.success && data.data) {
      renderReportSummary(data.data.summary);
      renderReportRecords(data.data.records, tbody);
    }
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-danger">Failed to generate report.</td></tr>';
    }
  } finally {
    if (genBtn) {
      genBtn.disabled = false;
      genBtn.innerHTML = '<i class="bi bi-gear-fill"></i> Generate Report';
    }
  }
}

function renderReportSummary(summary) {
  if (!summary) return;

  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setVal('rep-total', summary.total_responses);
  setVal('rep-avg-rate', summary.avg_rating);
  setVal('rep-pos-pct', `${summary.positive_pct}%`);
  setVal('rep-neg-pct', `${summary.negative_pct}%`);
  setVal('rep-neu-pct', `${summary.neutral_pct}%`);
  setVal('rep-mix-pct', `${summary.mixed_pct}%`);
  setVal('rep-praised', summary.most_praised || 'None');
  setVal('rep-problem', summary.most_problematic || 'None');
}

function renderReportRecords(records, tbody) {
  if (!tbody) return;

  if (!records || records.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-file-earmark-x empty-state-icon"></i>
            <div class="empty-state-title">No Records Found for Selected Filters</div>
            <div class="empty-state-desc">Try widening the date range or selecting "All" categories.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = records.map(r => `
    <tr>
      <td><strong>#${r.id}</strong></td>
      <td>
        <div><strong>${escapeHtml(r.student_name)}</strong></div>
        <div style="font-size: 0.72rem; color: var(--gray-500);">${r.student_roll_no || 'N/A'} &bull; ${escapeHtml(r.department)}</div>
      </td>
      <td><span class="analysis-tag">${r.category}</span></td>
      <td>${renderStars(r.rating)}</td>
      <td>${renderSentimentBadge(r.sentiment)}</td>
      <td style="font-size: 0.8rem; font-weight: 700; color: ${Number(r.sentiment_score) >= 0 ? 'var(--sentiment-pos)' : 'var(--sentiment-neg)'};">
        ${Number(r.sentiment_score) > 0 ? '+' : ''}${Number(r.sentiment_score).toFixed(2)}
      </td>
      <td style="max-width: 250px; font-size: 0.82rem;" title="${escapeHtml(r.feedback_text)}">
        ${escapeHtml(r.feedback_text)}
      </td>
      <td><span style="font-size: 0.75rem; color: var(--gray-500);">${formatDate(r.created_at)}</span></td>
    </tr>
  `).join('');
}
