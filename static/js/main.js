/**
 * AI Student Feedback Analyzer - Core Frontend Utilities
 */

// Toast Notification Manager
function showToast(title, message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: 'bi-check-circle-fill',
    error: 'bi-exclamation-triangle-fill',
    warning: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill'
  };

  const iconClass = iconMap[type] || 'bi-info-circle-fill';

  toast.innerHTML = `
    <i class="bi ${iconClass} toast-icon"></i>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// Modal Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Global modal close on click outside
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// Helper: Render Star Icons
function renderStars(rating) {
  const fullStars = Math.floor(rating);
  let starsHtml = '';
  for (let i = 1; i <= 5; i++) {
    if (i <= fullStars) {
      starsHtml += '<i class="bi bi-star-fill text-warning"></i> ';
    } else {
      starsHtml += '<i class="bi bi-star text-muted"></i> ';
    }
  }
  return `<span class="rating-stars" title="${rating} out of 5">${starsHtml} <span class="rating-num">(${rating})</span></span>`;
}

// Helper: Render Sentiment Badge
function renderSentimentBadge(sentiment) {
  const s = (sentiment || 'Neutral').toLowerCase();
  let badgeClass = 'badge-neutral';
  let icon = 'bi-dash-circle';

  if (s === 'positive') {
    badgeClass = 'badge-positive';
    icon = 'bi-emoji-smile-fill';
  } else if (s === 'negative') {
    badgeClass = 'badge-negative';
    icon = 'bi-emoji-frown-fill';
  } else if (s === 'mixed') {
    badgeClass = 'badge-mixed';
    icon = 'bi-arrow-left-right';
  }

  return `<span class="badge ${badgeClass}"><i class="bi ${icon}"></i> ${sentiment}</span>`;
}

// Format Date nicely
function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (e) {
    return dateStr;
  }
}

// Global Logout Handler
async function handleLogout() {
  try {
    const res = await fetch('/api/logout', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    window.location.href = '/login';
  } catch (err) {
    window.location.href = '/login';
  }
}

// Mobile sidebar toggle
function toggleMobileSidebar() {
  const sidebar = document.querySelector('.app-sidebar');
  if (sidebar) {
    sidebar.classList.toggle('open');
  }
}
