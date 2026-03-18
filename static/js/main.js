/* ═══════════════════════════════════════════════════════════
   ApnaGhar — Main JavaScript (main.js)
   ═══════════════════════════════════════════════════════════ */

/* ── Dark Mode ── */
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

// Load saved theme
if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark');
  if (themeToggle) themeToggle.textContent = '☀️';
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark');
    const isDark = body.classList.contains('dark');
    themeToggle.textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  });
}

/* ── Mobile Hamburger ── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('mobile-open');
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('mobile-open');
    }
  });
}

/* ── Search Bar Expand ── */
const searchInput = document.getElementById('searchInput');
if (searchInput) {
  searchInput.addEventListener('focus', () => searchInput.classList.add('expanded'));
  searchInput.addEventListener('blur',  () => {
    if (!searchInput.value) searchInput.classList.remove('expanded');
  });
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && searchInput.value.trim()) {
      // Basic search — redirect to bproperty with city filter
      const q = searchInput.value.trim();
      const cities = ['Delhi', 'Noida', 'Gurugram', 'Mumbai'];
      const match = cities.find(c => c.toLowerCase() === q.toLowerCase());
      if (match) window.location.href = `/bproperty?city=${match}`;
      else window.location.href = `/bproperty`;
    }
  });
}

/* ══════════════════════════════════════════
   HERO SLIDESHOW
   ══════════════════════════════════════════ */
(function initSlideshow() {
  const slides     = document.querySelectorAll('.slide');
  const indicators = document.querySelectorAll('.indicator');
  if (!slides.length) return;

  let current = 0;
  let timer;

  function goTo(index) {
    slides[current].classList.remove('active');
    indicators[current]?.classList.remove('active');
    current = (index + slides.length) % slides.length;
    slides[current].classList.add('active');
    indicators[current]?.classList.add('active');
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  function startAuto() {
    timer = setInterval(next, 5000);
  }
  function stopAuto() { clearInterval(timer); }

  // Init
  slides[0].classList.add('active');
  indicators[0]?.classList.add('active');
  startAuto();

  // Arrow buttons
  document.getElementById('slidePrev')?.addEventListener('click', () => { stopAuto(); prev(); startAuto(); });
  document.getElementById('slideNext')?.addEventListener('click', () => { stopAuto(); next(); startAuto(); });

  // Indicators
  indicators.forEach((dot, i) => {
    dot.addEventListener('click', () => { stopAuto(); goTo(i); startAuto(); });
  });

  // Pause on hover
  const hero = document.querySelector('.hero');
  if (hero) {
    hero.addEventListener('mouseenter', stopAuto);
    hero.addEventListener('mouseleave', startAuto);
  }
})();

/* ══════════════════════════════════════════
   SCROLL ANIMATIONS
   ══════════════════════════════════════════ */
(function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger delay for multiple cards
        const siblings = [...entry.target.parentElement.children];
        const idx = siblings.indexOf(entry.target);
        setTimeout(() => {
          entry.target.classList.add('animate-in');
        }, idx * 120);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  // Observe all animated elements
  document.querySelectorAll('.place-card, .why-card, .support-card, .property-card').forEach(el => {
    observer.observe(el);
  });
})();

/* ══════════════════════════════════════════
   PROPERTY TYPE CAROUSEL
   ══════════════════════════════════════════ */
(function initTypeCarousel() {
  const carousel = document.getElementById('typeCarousel');
  const prevBtn  = document.getElementById('carouselPrev');
  const nextBtn  = document.getElementById('carouselNext');
  if (!carousel) return;

  const cardWidth = 280 + 20; // card + gap
  prevBtn?.addEventListener('click', () => {
    carousel.scrollBy({ left: -cardWidth * 2, behavior: 'smooth' });
  });
  nextBtn?.addEventListener('click', () => {
    carousel.scrollBy({ left: cardWidth * 2, behavior: 'smooth' });
  });
})();

/* ══════════════════════════════════════════
   AUTH MODAL
   ══════════════════════════════════════════ */
const loginModal   = document.getElementById('loginModal');
const signupModal  = document.getElementById('signupModal');

function openModal(modal)  { modal?.classList.add('open'); document.body.style.overflow = 'hidden'; }
function closeModal(modal) { modal?.classList.remove('open'); document.body.style.overflow = ''; }

// Close on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal(overlay);
  });
});

// Close buttons
document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', () => {
    closeModal(btn.closest('.modal-overlay'));
  });
});

// Switch between login and signup
window.switchToSignup = () => { closeModal(loginModal); openModal(signupModal); };
window.switchToLogin  = () => { closeModal(signupModal); openModal(loginModal); };

// Open login
document.querySelectorAll('[data-open-login]').forEach(btn => {
  btn.addEventListener('click', () => openModal(loginModal));
});
// Open signup
document.querySelectorAll('[data-open-signup]').forEach(btn => {
  btn.addEventListener('click', () => openModal(signupModal));
});

/* ── LOGIN ── */
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email    = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errEl    = document.getElementById('loginError');

    try {
      const res  = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (data.success) {
        closeModal(loginModal);
        showToast(`Welcome back, ${data.name}! 🏠`, 'success');
        setTimeout(() => location.reload(), 1000);
      } else {
        if (errEl) errEl.textContent = data.message;
      }
    } catch { if (errEl) errEl.textContent = 'Something went wrong. Try again.'; }
  });
}

/* ── SIGNUP ── */
const signupForm = document.getElementById('signupForm');
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      name:     document.getElementById('signupName').value,
      surname:  document.getElementById('signupSurname').value,
      gender:   document.getElementById('signupGender').value,
      age:      document.getElementById('signupAge').value,
      address:  document.getElementById('signupAddress').value,
      email:    document.getElementById('signupEmail').value,
      password: document.getElementById('signupPassword').value,
    };
    const errEl = document.getElementById('signupError');
    try {
      const res  = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const result = await res.json();
      if (result.success) {
        closeModal(signupModal);
        showToast(`Welcome to ApnaGhar, ${result.name}! 🎉`, 'success');
        setTimeout(() => location.reload(), 1000);
      } else {
        if (errEl) errEl.textContent = result.message;
      }
    } catch { if (errEl) errEl.textContent = 'Something went wrong. Try again.'; }
  });
}

/* ── LOGOUT ── */
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', async () => {
    await fetch('/api/logout');
    showToast('Logged out successfully', 'info');
    setTimeout(() => location.reload(), 800);
  });
}

/* ── PROFILE ── */
const viewProfileBtn = document.getElementById('viewProfileBtn');
if (viewProfileBtn) {
  viewProfileBtn.addEventListener('click', async () => {
    const res  = await fetch('/api/profile');
    const data = await res.json();
    if (data.success) {
      const u = data.user;
      const profileModal = document.getElementById('profileModal');
      if (profileModal) {
        document.getElementById('profileName').textContent    = `${u.Name} ${u.Surname}`;
        document.getElementById('profileEmail').textContent   = u.Email;
        document.getElementById('profileGender').textContent  = u.Gender;
        document.getElementById('profileAge').textContent     = u.Age;
        document.getElementById('profileAddress').textContent = u.Address;
        openModal(profileModal);
      }
    }
  });
}

/* ── SHORTLISTED ── */
const shortlistedBtn = document.getElementById('shortlistedBtn');
if (shortlistedBtn) {
  shortlistedBtn.addEventListener('click', async () => {
    const res  = await fetch('/api/shortlisted');
    const data = await res.json();
    const modal = document.getElementById('shortlistedModal');
    const list  = document.getElementById('shortlistedList');
    if (!modal || !list) return;
    if (data.success) {
      if (data.properties.length === 0) {
        list.innerHTML = '<div class="no-results"><div class="icon">💔</div><h3>No shortlisted properties yet</h3><p>Browse and shortlist properties you love!</p></div>';
      } else {
        list.innerHTML = data.properties.map(p => `
          <div class="property-card" style="animation-delay:0s">
            <div class="property-card-img">
              <img src="/static/images/house/pic1.jpg" alt="${p.Society}" onerror="this.src='https://via.placeholder.com/400x200?text=Property'">
              <span class="property-badge ${p.Purpose === 'Rent' ? 'rent' : ''}">${p.Purpose}</span>
            </div>
            <div class="property-card-body">
              <div class="property-society">${p.Society}</div>
              <div class="property-address">${p.Address}</div>
              <div class="property-price">${p.formatted_price}</div>
              <div class="property-area">${p.Area} sq.ft</div>
            </div>
          </div>
        `).join('');
      }
      openModal(modal);
    }
  });
}

/* ══════════════════════════════════════════
   SHORTLIST BUTTON (on property pages)
   ══════════════════════════════════════════ */
document.querySelectorAll('.shortlist-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.stopPropagation();
    const propertyID = btn.dataset.id;
    const res  = await fetch('/api/shortlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ propertyID: parseInt(propertyID) })
    });
    const data = await res.json();
    if (data.success) {
      btn.classList.toggle('active', data.action === 'added');
      btn.textContent = data.action === 'added' ? '❤️' : '🤍';
      showToast(data.action === 'added' ? 'Added to shortlist!' : 'Removed from shortlist', 'info');
    } else {
      showToast('Please login to shortlist properties', 'error');
      openModal(loginModal);
    }
  });
});

/* ══════════════════════════════════════════
   TOAST NOTIFICATION
   ══════════════════════════════════════════ */
function showToast(message, type = 'info') {
  // Remove existing toast
  document.querySelectorAll('.toast').forEach(t => t.remove());

  const icons = { success: '✅', error: '❌', info: '💡' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type]}</span> ${message}`;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add('show'));
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// Expose globally
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
