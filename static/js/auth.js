/**
 * AI Student Feedback Analyzer - Authentication Module
 * Enhanced with role switching, password visibility toggle & 1-click viva presets
 */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const emailInput = document.getElementById('login-email');
  const passwordInput = document.getElementById('login-password');
  const rememberInput = document.getElementById('login-remember');
  const loginBtn = document.getElementById('login-btn');
  const errorAlert = document.getElementById('login-error-alert');
  const studentTab = document.getElementById('tab-student');
  const adminTab = document.getElementById('tab-admin');
  const demoRoleText = document.getElementById('demo-role-text');
  const demoCreds = document.getElementById('demo-credentials');
  const togglePasswordBtn = document.getElementById('toggle-password-btn');
  const quickFillBtns = document.querySelectorAll('.quick-fill-btn');

  let activeRole = 'student';

  function setRole(role) {
    activeRole = role;
    if (role === 'admin') {
      if (adminTab) adminTab.classList.add('active');
      if (studentTab) studentTab.classList.remove('active');
      if (emailInput) emailInput.value = 'admin@college.edu';
      if (passwordInput) passwordInput.value = 'admin123';
      if (demoRoleText) demoRoleText.textContent = 'Administrator';
      if (demoCreds) demoCreds.innerHTML = '<strong>Email:</strong> admin@college.edu | <strong>Password:</strong> admin123';
      
      quickFillBtns.forEach(btn => {
        if (btn.getAttribute('data-fill-role') === 'admin') {
          btn.classList.add('active-preset');
        } else {
          btn.classList.remove('active-preset');
        }
      });
    } else {
      if (studentTab) studentTab.classList.add('active');
      if (adminTab) adminTab.classList.remove('active');
      if (emailInput) emailInput.value = 'alex.turner@college.edu';
      if (passwordInput) passwordInput.value = 'student123';
      if (demoRoleText) demoRoleText.textContent = 'Student';
      if (demoCreds) demoCreds.innerHTML = '<strong>Email:</strong> alex.turner@college.edu | <strong>Password:</strong> student123';
      
      quickFillBtns.forEach(btn => {
        if (btn.getAttribute('data-fill-role') === 'student') {
          btn.classList.add('active-preset');
        } else {
          btn.classList.remove('active-preset');
        }
      });
    }
    if (errorAlert) errorAlert.style.display = 'none';
  }

  // Role Tab Switching
  if (studentTab) {
    studentTab.addEventListener('click', () => setRole('student'));
  }

  if (adminTab) {
    adminTab.addEventListener('click', () => setRole('admin'));
  }

  // 1-Click Viva Presets
  quickFillBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const role = btn.getAttribute('data-fill-role');
      const email = btn.getAttribute('data-fill-email');
      const pass = btn.getAttribute('data-fill-password');
      if (role) setRole(role);
      if (email && emailInput) emailInput.value = email;
      if (pass && passwordInput) passwordInput.value = pass;
      
      quickFillBtns.forEach(b => b.classList.remove('active-preset'));
      btn.classList.add('active-preset');

      if (typeof showToast === 'function') {
        showToast('Credentials Applied', `Loaded credentials for ${role === 'admin' ? 'Administrator' : 'Student'}`, 'info');
      }
    });
  });

  // Password Visibility Toggle
  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      const currentType = passwordInput.getAttribute('type');
      const newType = currentType === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', newType);
      
      const icon = togglePasswordBtn.querySelector('i');
      if (icon) {
        icon.className = newType === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash-fill';
      }
    });
  }

  // Login Form Submission
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = emailInput ? emailInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value.trim() : '';
      const remember = rememberInput ? rememberInput.checked : false;

      if (!email || !password) {
        showError('Please enter both email/ID and password.');
        return;
      }

      loginBtn.disabled = true;
      loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Signing In...';
      if (errorAlert) errorAlert.style.display = 'none';

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, remember })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          if (typeof showToast === 'function') {
            showToast('Login Successful', data.message, 'success');
          }
          setTimeout(() => {
            window.location.href = data.redirect;
          }, 400);
        } else {
          showError(data.message || 'Invalid credentials. Please try again.');
          loginBtn.disabled = false;
          loginBtn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Sign In to Portal';
        }
      } catch (err) {
        showError('Unable to connect to server. Please check your network or database connection.');
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Sign In to Portal';
      }
    });
  }

  function showError(msg) {
    if (errorAlert) {
      errorAlert.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> <span>${msg}</span>`;
      errorAlert.style.display = 'flex';
    } else if (typeof showToast === 'function') {
      showToast('Login Failed', msg, 'error');
    }
  }
});
