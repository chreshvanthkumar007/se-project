/**
 * Student Dashboard & Feedback Submission Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initStudentDashboard();
  initFeedbackForm();
});

// -------------------------------------------------------------
// Student Dashboard Initialization
// -------------------------------------------------------------
async function initStudentDashboard() {
  const tableBody = document.getElementById('student-feedback-table-body');
  if (!tableBody) return; // Not on student dashboard

  try {
    const res = await fetch('/api/feedback');
    const data = await res.json();

    if (data.success) {
      renderStudentStats(data.items);
      renderStudentTable(data.items, tableBody);
    }
  } catch (err) {
    console.error('Error fetching student feedback:', err);
    showToast('Error', 'Failed to load your feedback history.', 'error');
  }
}

function renderStudentStats(items) {
  const totalEl = document.getElementById('stat-total-submitted');
  const avgRateEl = document.getElementById('stat-avg-rating');
  const lastDateEl = document.getElementById('stat-last-date');
  const lastStatusEl = document.getElementById('stat-last-status');

  if (!totalEl) return;

  const total = items.length;
  totalEl.textContent = total;

  if (total === 0) {
    if (avgRateEl) avgRateEl.textContent = '0.0';
    if (lastDateEl) lastDateEl.textContent = 'None';
    if (lastStatusEl) lastStatusEl.textContent = 'No Submissions';
    return;
  }

  const sumRatings = items.reduce((acc, curr) => acc + Number(curr.rating), 0);
  const avg = (sumRatings / total).toFixed(1);
  if (avgRateEl) avgRateEl.textContent = avg;

  const sorted = [...items].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  const latest = sorted[0];

  if (lastDateEl) lastDateEl.textContent = formatDate(latest.created_at);
  if (lastStatusEl) lastStatusEl.innerHTML = renderSentimentBadge(latest.sentiment);
}

function renderStudentTable(items, tbody) {
  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-4">
          <div class="empty-state">
            <i class="bi bi-chat-square-text empty-state-icon"></i>
            <div class="empty-state-title">No Feedback Submitted Yet</div>
            <div class="empty-state-desc">You have not submitted any academic feedback. Click "Submit New Feedback" above to begin.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map(fb => `
    <tr>
      <td><strong>#${fb.id}</strong></td>
      <td><span class="analysis-tag">${fb.category}</span></td>
      <td>${renderStars(fb.rating)}</td>
      <td style="max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(fb.feedback_text)}">
        ${escapeHtml(fb.feedback_text)}
      </td>
      <td>${renderSentimentBadge(fb.sentiment)}</td>
      <td>${formatDate(fb.created_at)}</td>
      <td>
        <button class="btn btn-outline btn-sm" onclick="viewAnalysisDetails(${fb.id})">
          <i class="bi bi-cpu"></i> View AI Analysis
        </button>
      </td>
    </tr>
  `).join('');
}

// -------------------------------------------------------------
// Student Feedback Submission Form
// -------------------------------------------------------------
function initFeedbackForm() {
  const form = document.getElementById('feedback-submission-form');
  if (!form) return;

  const ratingBtns = document.querySelectorAll('.star-btn');
  const ratingInput = document.getElementById('rating-input');
  const ratingDesc = document.getElementById('rating-descriptor');
  const feedbackTextarea = document.getElementById('feedback-text');
  const charCounter = document.getElementById('char-count');
  const clearBtn = document.getElementById('clear-form-btn');
  const submitBtn = document.getElementById('submit-feedback-btn');

  const ratingLabels = {
    1: '1 - Very Poor',
    2: '2 - Poor',
    3: '3 - Average',
    4: '4 - Good',
    5: '5 - Excellent'
  };

  // Star Rating Interaction
  ratingBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const val = parseInt(btn.dataset.value);
      ratingInput.value = val;
      updateStars(val);
      if (ratingDesc) ratingDesc.textContent = ratingLabels[val] || '';
    });

    btn.addEventListener('mouseenter', () => {
      const val = parseInt(btn.dataset.value);
      highlightStars(val);
    });

    btn.addEventListener('mouseleave', () => {
      const cur = parseInt(ratingInput.value) || 0;
      highlightStars(cur);
    });
  });

  function updateStars(val) {
    highlightStars(val);
  }

  function highlightStars(val) {
    ratingBtns.forEach(b => {
      const v = parseInt(b.dataset.value);
      if (v <= val) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
  }

  // Character Counter
  if (feedbackTextarea && charCounter) {
    feedbackTextarea.addEventListener('input', () => {
      const len = feedbackTextarea.value.length;
      charCounter.textContent = `${len} / 2000 characters`;
      if (len < 10) {
        charCounter.style.color = 'var(--sentiment-neg)';
      } else {
        charCounter.style.color = 'var(--gray-500)';
      }
    });
  }

  // Clear Form
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      form.reset();
      ratingInput.value = '';
      highlightStars(0);
      if (ratingDesc) ratingDesc.textContent = 'Select rating';
      if (charCounter) charCounter.textContent = '0 / 2000 characters';
    });
  }

  // Form Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const category = document.getElementById('category-select').value;
    const rating = ratingInput.value;
    const feedback_text = feedbackTextarea.value.trim();

    if (!category) {
      showToast('Validation Error', 'Please select a feedback category.', 'warning');
      return;
    }

    if (!rating) {
      showToast('Validation Error', 'Please select a rating between 1 and 5.', 'warning');
      return;
    }

    if (feedback_text.length < 10) {
      showToast('Validation Error', 'Feedback must be at least 10 characters long.', 'warning');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing & Submitting...';

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, rating, feedback_text })
      });

      const resData = await response.json();

      if (response.ok && resData.success) {
        showToast('Success', 'Feedback analyzed and submitted successfully!', 'success');
        
        // Show real-time analysis modal immediately!
        displayAnalysisModal({
          category,
          rating,
          feedback_text,
          ...resData.analysis
        });

        // Reset form
        form.reset();
        ratingInput.value = '';
        highlightStars(0);
        if (ratingDesc) ratingDesc.textContent = 'Select rating';
        if (charCounter) charCounter.textContent = '0 / 2000 characters';

      } else {
        showToast('Submission Failed', resData.message || 'Error submitting feedback.', 'error');
      }
    } catch (err) {
      showToast('Network Error', 'Could not connect to the backend server.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-send-check"></i> Submit Feedback';
    }
  });
}

// -------------------------------------------------------------
// Detailed AI Analysis Modal Display
// -------------------------------------------------------------
async function viewAnalysisDetails(feedbackId) {
  try {
    const res = await fetch(`/api/feedback/${feedbackId}`);
    const data = await res.json();
    if (data.success && data.feedback) {
      displayAnalysisModal(data.feedback);
    } else {
      showToast('Error', data.message || 'Could not load analysis details.', 'error');
    }
  } catch (err) {
    showToast('Error', 'Failed to retrieve feedback record.', 'error');
  }
}

function displayAnalysisModal(data) {
  const modalBody = document.getElementById('analysis-modal-body');
  if (!modalBody) return;

  const sentiment = data.sentiment || 'Neutral';
  const score = Number(data.sentiment_score || 0).toFixed(2);
  const keywords = Array.isArray(data.keywords) ? data.keywords : [];
  const topics = Array.isArray(data.topics) ? data.topics : [];
  const strengths = Array.isArray(data.strengths) ? data.strengths : [];
  const problems = Array.isArray(data.problems) ? data.problems : [];
  const recommendations = Array.isArray(data.recommendations) ? data.recommendations : [];

  // Determine meter fill percentage and class
  // Score is between -1.0 and 1.0; map to 0% to 100%
  const normalizedPct = Math.round(((Number(score) + 1.0) / 2.0) * 100);
  const sentClass = sentiment.toLowerCase().substring(0, 3); // pos, neg, neu, mix

  modalBody.innerHTML = `
    <!-- Top Sentiment Card -->
    <div class="analysis-header-score">
      <div class="sentiment-display">
        <div>${renderSentimentBadge(sentiment)}</div>
        <div>
          <div style="font-size: 0.75rem; color: var(--gray-500); font-weight: 600;">Sentiment Polarity</div>
          <div style="font-size: 1.15rem; font-weight: 800; color: var(--navy-900);">${score > 0 ? '+' : ''}${score}</div>
        </div>
      </div>
      <div class="sentiment-meter">
        <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--gray-500);">
          <span>Negative (-1.0)</span>
          <span>Positive (+1.0)</span>
        </div>
        <div class="meter-track">
          <div class="meter-fill ${sentClass}" style="width: ${normalizedPct}%;"></div>
        </div>
      </div>
    </div>

    <!-- Student / Submission Meta -->
    <div style="background-color: var(--gray-50); border: 1px solid var(--gray-200); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
      <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; font-size: 0.82rem;">
        <div><strong>Category:</strong> <span class="badge badge-outline">${data.category}</span></div>
        <div><strong>Rating:</strong> ${renderStars(data.rating)}</div>
        ${data.student_name ? `<div><strong>Student:</strong> ${escapeHtml(data.student_name)} (${data.student_roll_no || 'N/A'})</div>` : ''}
        ${data.department ? `<div><strong>Department:</strong> ${escapeHtml(data.department)}</div>` : ''}
      </div>
      <div style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--gray-700); font-style: italic; border-left: 3px solid var(--gray-300); padding-left: 0.75rem;">
        "${escapeHtml(data.feedback_text)}"
      </div>
    </div>

    <!-- Keywords & Topics -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem;">
      <div>
        <div class="aspect-title"><i class="bi bi-tags text-primary"></i> Extracted Keywords</div>
        <div class="tag-cloud">
          ${keywords.length ? keywords.map(kw => `<span class="analysis-tag">${escapeHtml(kw)}</span>`).join('') : '<span class="text-muted" style="font-size: 0.8rem;">None detected</span>'}
        </div>
      </div>
      <div>
        <div class="aspect-title"><i class="bi bi-bookmark text-primary"></i> Detected Topics</div>
        <div class="tag-cloud">
          ${topics.length ? topics.map(t => `<span class="analysis-tag" style="background-color: var(--primary-50); color: var(--primary-700); border-color: var(--primary-200);">${escapeHtml(t)}</span>`).join('') : '<span class="text-muted" style="font-size: 0.8rem;">General</span>'}
        </div>
      </div>
    </div>

    <!-- Strengths -->
    <div class="aspect-section">
      <div class="aspect-title" style="color: var(--sentiment-pos);"><i class="bi bi-check-circle-fill"></i> Positive Strengths & Commendations</div>
      ${strengths.length ? strengths.map(s => `<div class="aspect-card strength"><i class="bi bi-check2"></i> <span>${escapeHtml(s)}</span></div>`).join('') : '<p class="text-muted" style="font-size: 0.8rem;">No explicit commendations detected in this response.</p>'}
    </div>

    <!-- Problems / Areas for Improvement -->
    <div class="aspect-section">
      <div class="aspect-title" style="color: var(--sentiment-neg);"><i class="bi bi-exclamation-octagon-fill"></i> Identified Deficiencies & Pain Points</div>
      ${problems.length ? problems.map(p => `<div class="aspect-card problem"><i class="bi bi-exclamation-triangle"></i> <span>${escapeHtml(p)}</span></div>`).join('') : '<p class="text-muted" style="font-size: 0.8rem;">No critical pain points or deficiencies detected.</p>'}
    </div>

    <!-- Recommendations -->
    <div class="aspect-section">
      <div class="aspect-title" style="color: var(--primary-700);"><i class="bi bi-lightbulb-fill"></i> AI Institutional Recommendations</div>
      ${recommendations.length ? recommendations.map(r => `<div class="aspect-card recommendation"><i class="bi bi-arrow-right-circle"></i> <span>${escapeHtml(r)}</span></div>`).join('') : '<p class="text-muted" style="font-size: 0.8rem;">Standard review recommended.</p>'}
    </div>
  `;

  openModal('analysis-details-modal');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
