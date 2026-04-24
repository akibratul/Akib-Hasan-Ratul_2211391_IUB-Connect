// ========== Toast Auto-dismiss ==========
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  });

  // Mobile menu toggle
  const menuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuBtn) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Role toggle on register page
  const roleRadios = document.querySelectorAll('.role-btn');
  const roleInput = document.getElementById('role-input');
  const studentFields = document.getElementById('student-fields');
  const alumniFields = document.getElementById('alumni-fields');
  roleRadios.forEach(btn => {
    btn.addEventListener('click', () => {
      roleRadios.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const role = btn.dataset.role;
      if (roleInput) roleInput.value = role;
      if (studentFields) studentFields.style.display = role === 'student' ? 'block' : 'none';
      if (alumniFields) alumniFields.style.display = role === 'alumni' ? 'block' : 'none';
      
      const emailHint = document.getElementById('student-email-hint');
      const emailInput = document.getElementById('register-email');
      if (emailHint && emailInput) {
        if (role === 'student') {
          emailHint.style.display = 'block';
          emailInput.placeholder = '2211391@iub.edu.bd';
        } else {
          emailHint.style.display = 'none';
          emailInput.placeholder = 'you@example.com';
        }
      }
    });
  });
});
