/**
 * PropertyWeb – main.js
 * ─────────────────────
 * Shared utilities used across all pages:
 *  - Auth (login / signup / profile) via sessionStorage
 *  - Navbar setup (search expand, profile menu, dropdown)
 *  - Dark / Light mode toggle
 *  - Toast notifications
 *  - Intersection Observer for scroll animations
 *  - Price formatting helpers
 */

/* ════════════════════════════════════
   AUTH HELPERS
════════════════════════════════════ */

/** Save logged-in user to sessionStorage */
function authSave(user) {
  sessionStorage.setItem("pw_user", JSON.stringify(user));
}

/** Get logged-in user object (or null) */
function authGet() {
  const raw = sessionStorage.getItem("pw_user");
  return raw ? JSON.parse(raw) : null;
}

/** Remove user from sessionStorage (logout) */
function authLogout() {
  sessionStorage.removeItem("pw_user");
  location.reload();
}

/* ════════════════════════════════════
   TOAST
════════════════════════════════════ */

/** Show a toast message for `duration` ms */
function showToast(msg, duration = 3000) {
  let toast = document.getElementById("pw-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "pw-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), duration);
}

/* ════════════════════════════════════
   DARK MODE
════════════════════════════════════ */

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("pw_theme", theme);
  // Update toggle icon
  const btn = document.getElementById("theme-toggle");
  if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
}

function initTheme() {
  const saved = localStorage.getItem("pw_theme") || "light";
  applyTheme(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  applyTheme(current === "dark" ? "light" : "dark");
}

/* ════════════════════════════════════
   PRICE FORMATTERS
════════════════════════════════════ */

/** Format buy price: <1 → Lakhs, else → Cr */
function formatPrice(priceCr) {
  if (!priceCr) return "N/A";
  if (priceCr < 1) {
    return Math.round(priceCr * 100) + "L";
  }
  return parseFloat(priceCr.toFixed(2)) + " Cr";
}

/** Format rent: <100 → K, else → L */
function formatRent(rent) {
  if (!rent) return "N/A";
  if (rent < 100) {
    return Math.round(rent) + "K";
  }
  return parseFloat((rent / 100).toFixed(2)) + "L";
}

/* ════════════════════════════════════
   NAVBAR SETUP
════════════════════════════════════ */

function buildNavbar() {
  const user = authGet();
  const navHTML = `
    <nav class="navbar">
      <!-- Brand -->
      <a class="nav-brand" href="/">🏠 Aashiyana</a>

      <!-- Links -->
      <ul class="nav-links" id="nav-links">
        <li class="nav-item" id="prop-dropdown-item">
          <span class="nav-link">Property ▾</span>
          <div class="nav-dropdown">
            <a href="/bproperty">🏢 Buying</a>
            <a href="/rproperty">🔑 Renting</a>
          </div>
        </li>
        <li class="nav-item"><a class="nav-link" href="/map">🗺️ Map</a></li>
        <li class="nav-item"><a class="nav-link" href="/connect">💬 Connect</a></li>
        <li class="nav-item"><a class="nav-link" href="/sell">🏷️ Sell</a></li>
        <li class="nav-item"><a class="nav-link" href="/table">📋 Table</a></li>
      </ul>

      <!-- Search -->
      <div class="nav-search" id="nav-search">
        <span class="search-icon">🔍</span>
        <input type="text" id="nav-search-input" placeholder="Search societies..." />
      </div>

      <!-- Right Icons -->
      <div class="nav-right">
        <button class="nav-icon-btn" id="theme-toggle" onclick="toggleTheme()" title="Toggle dark/light">🌙</button>

        <!-- Profile -->
        <div class="nav-item" style="position:relative;">
          <button class="nav-icon-btn" id="profile-btn" title="Profile">👤</button>
          <div class="profile-menu" id="profile-menu">
            ${user
              ? `<div class="profile-user-name">👋 ${user.name}</div>
                 <div class="profile-menu-item" onclick="viewProfile()">🪪 View Profile</div>
                 <div class="profile-menu-divider"></div>
                 <div class="profile-menu-item" onclick="authLogout()">🚪 Logout</div>`
              : `<div class="profile-menu-item" onclick="openLogin()">🔐 Login</div>
                 <div class="profile-menu-item" onclick="openSignup()">📝 Sign Up</div>`
            }
          </div>
        </div>
      </div>
    </nav>

    <!-- Login Dialog -->
    <div class="dialog-overlay" id="login-dialog">
      <div class="dialog-box">
        <button class="dialog-close" onclick="closeDialog('login-dialog')">✕</button>
        <h2 class="dialog-title">Welcome Back</h2>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input class="form-input" type="email" id="login-email" placeholder="you@example.com">
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-input" type="password" id="login-password" placeholder="••••••••">
        </div>
        <button class="btn btn-primary btn-full" onclick="doLogin()" style="margin-top:0.5rem">Login</button>
        <p style="text-align:center;margin-top:1rem;font-size:0.85rem;color:var(--text2)">
          Don't have an account?
          <span style="color:var(--accent);cursor:pointer" onclick="closeDialog('login-dialog');openSignup()">Sign Up</span>
        </p>
      </div>
    </div>

    <!-- Signup Dialog -->
    <div class="dialog-overlay" id="signup-dialog">
      <div class="dialog-box">
        <button class="dialog-close" onclick="closeDialog('signup-dialog')">✕</button>
        <h2 class="dialog-title">Create Account</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input class="form-input" type="text" id="su-name" placeholder="Aarav Sharma">
          </div>
          <div class="form-group">
            <label class="form-label">Age</label>
            <input class="form-input" type="number" id="su-age" placeholder="25">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input class="form-input" type="email" id="su-email" placeholder="you@example.com">
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" type="password" id="su-password" placeholder="••••••••">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Gender</label>
            <select class="form-select" id="su-gender">
              <option value="">Select</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Occupation</label>
            <select class="form-select" id="su-occupation">
              <option value="">Select</option>
              <option value="student">Student</option>
              <option value="job">Job</option>
              <option value="business">Business</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Organisation</label>
          <input class="form-input" type="text" id="su-org" placeholder="Company / College name">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Org Address</label>
            <input class="form-input" type="text" id="su-orgAddr" placeholder="Address">
          </div>
          <div class="form-group">
            <label class="form-label">Org Sector</label>
            <input class="form-input" type="text" id="su-orgSector" placeholder="e.g. sector 24">
          </div>
        </div>
        <button class="btn btn-primary btn-full" onclick="doSignup()" style="margin-top:0.5rem">Create Account</button>
      </div>
    </div>

    <!-- Profile Dialog -->
    <div class="dialog-overlay" id="profile-dialog">
      <div class="dialog-box">
        <button class="dialog-close" onclick="closeDialog('profile-dialog')">✕</button>
        <h2 class="dialog-title">My Profile</h2>
        <div id="profile-content" style="font-size:0.9rem;line-height:2;color:var(--text)"></div>
      </div>
    </div>
  `;

  // Insert navbar at top of body
  document.body.insertAdjacentHTML("afterbegin", navHTML);

  // ── Search expand on click ──
  const searchBox = document.getElementById("nav-search");
  const searchInput = document.getElementById("nav-search-input");
  searchBox.addEventListener("click", () => {
    searchBox.classList.toggle("expanded");
    if (searchBox.classList.contains("expanded")) searchInput.focus();
  });
  // Search on Enter key
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && searchInput.value.trim()) {
      window.location.href = `/bproperty?sector=${encodeURIComponent(searchInput.value.trim())}`;
    }
  });

  // ── Profile menu toggle ──
  document.getElementById("profile-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    document.getElementById("profile-menu").classList.toggle("open");
  });

  // Close profile menu on outside click
  document.addEventListener("click", () => {
    document.getElementById("profile-menu").classList.remove("open");
  });

  // ── Highlight active nav link ──
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === path) link.classList.add("active");
  });

  // Apply saved theme
  initTheme();
}

/* ════════════════════════════════════
   DIALOG HELPERS
════════════════════════════════════ */

function openDialog(id) {
  document.getElementById(id).classList.add("open");
}
function closeDialog(id) {
  document.getElementById(id).classList.remove("open");
}
// Close on overlay click
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("dialog-overlay")) {
    e.target.classList.remove("open");
  }
});

function openLogin()  { openDialog("login-dialog"); }
function openSignup() { openDialog("signup-dialog"); }

/* ════════════════════════════════════
   AUTH ACTIONS
════════════════════════════════════ */

async function doLogin() {
  const email    = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();
  if (!email || !password) { showToast("Please fill all fields"); return; }

  const res  = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (data.success) {
    authSave(data.user);
    closeDialog("login-dialog");
    showToast(`Welcome back, ${data.user.name}! 👋`);
    setTimeout(() => location.reload(), 1200);
  } else {
    showToast(data.message || "Login failed");
  }
}

async function doSignup() {
  const payload = {
    name:        document.getElementById("su-name").value.trim(),
    email:       document.getElementById("su-email").value.trim(),
    password:    document.getElementById("su-password").value.trim(),
    gender:      document.getElementById("su-gender").value,
    age:         parseInt(document.getElementById("su-age").value) || 0,
    occupation:  document.getElementById("su-occupation").value,
    organisation:document.getElementById("su-org").value.trim(),
    orgAddress:  document.getElementById("su-orgAddr").value.trim(),
    orgSector:   document.getElementById("su-orgSector").value.trim(),
  };
  if (!payload.name || !payload.email || !payload.password) {
    showToast("Name, email and password are required");
    return;
  }
  const res  = await fetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (data.success) {
    closeDialog("signup-dialog");
    showToast("Account created! Please login.");
    openLogin();
  } else {
    showToast(data.message || "Signup failed");
  }
}

async function viewProfile() {
  const user = authGet();
  if (!user) return;
  const res  = await fetch(`/api/profile/${user.UserId}`);
  const data = await res.json();
  const labels = {
    UserId:"User ID", name:"Name", email:"Email", gender:"Gender", age:"Age",
    occupation:"Occupation", organisation:"Organisation",
    orgAddress:"Org Address", orgSector:"Org Sector", Status:"Flatmate Status"
  };
  document.getElementById("profile-content").innerHTML =
    Object.entries(labels).map(([k, l]) =>
      `<div style="display:flex;gap:1rem;border-bottom:1px solid var(--border);padding:0.3rem 0">
        <span style="min-width:140px;color:var(--text2);font-weight:600">${l}</span>
        <span>${data[k] ?? "—"}</span>
      </div>`
    ).join("");
  closeDialog("login-dialog");
  document.getElementById("profile-menu").classList.remove("open");
  openDialog("profile-dialog");
}

/* ════════════════════════════════════
   SCROLL ANIMATIONS (Intersection Observer)
════════════════════════════════════ */

function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
      }
    });
  }, { threshold: 0.15 });

  // Observe explore boxes and type boxes
  document.querySelectorAll(".explore-box, .type-box").forEach(el => {
    observer.observe(el);
  });
}

/* ════════════════════════════════════
   PROPERTY CARD BUILDER
════════════════════════════════════ */

/**
 * Build a property card HTML string.
 * @param {Object} p  - property row from API
 * @param {boolean} isRent - true for rental mode
 */
function buildPropertyCard(p, isRent = false) {
  // Collect images from Image table columns
  const imgs = [p.i1, p.i2, p.i3, p.i4, p.i5, p.i6]
    .filter(Boolean)
    .map(img => `/static/images/${img}`);

  // Fallback if no images
  const fallback = "https://placehold.co/400x200/1A1A2E/C9982A?text=Property";
  const imageList = imgs.length ? imgs : [fallback];

  const carouselImgs = imageList.map((src, i) =>
    `<img src="${src}" class="${i === 0 ? 'active' : ''}" alt="Property" loading="lazy"
          onerror="this.src='${fallback}'">`
  ).join("");
  const dots = imageList.map((_, i) =>
    `<div class="carousel-dot ${i === 0 ? 'active' : ''}" data-idx="${i}"></div>`
  ).join("");

  const price = isRent ? formatRent(p.Rent) : formatPrice(p.priceCr);
  const priceLabel = isRent ? "Rent/mo" : "Price";

  // Badge class for furnishing
  const ftype = (p.Furnishing_type || "").toLowerCase().replace(/\s/g, "");
  const badgeClass = `badge-${ftype}`;

  return `
    <div class="card" data-id="${p.id}">
      <div class="card-carousel" data-carousel>
        ${carouselImgs}
        <div class="carousel-dots">${dots}</div>
      </div>
      <div class="card-body">
        <div class="card-society">${capitalize(p.society)}</div>
        <div class="card-sector">📍 ${capitalize(p.sector)}</div>
        <div class="card-price">${price} <small style="font-size:0.7rem;font-weight:400;color:var(--text2)">${priceLabel}</small></div>
        <div class="card-meta">
          <span class="card-tag">🛏 ${p.bedroom} Bed</span>
          <span class="card-tag">🚿 ${p.bathroom} Bath</span>
          <span class="card-tag">🌿 ${p.balcony} Balcony</span>
          <span class="card-tag">📐 ${p.area} sqft</span>
          <span class="card-tag">🏢 Floor ${p.floorNum}</span>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:0.5rem">
          <span class="card-furnish-badge ${badgeClass}">${p.Furnishing_type}</span>
          <button class="btn btn-primary" style="padding:0.4rem 0.9rem;font-size:0.8rem"
            onclick="goConnect(${p.UserID})">💬 Connect</button>
        </div>
      </div>
    </div>
  `;
}

/** Initialize all carousels on the page */
function initCarousels() {
  document.querySelectorAll("[data-carousel]").forEach(carousel => {
    const imgs = carousel.querySelectorAll("img");
    const dots = carousel.querySelectorAll(".carousel-dot");
    if (imgs.length <= 1) return;

    let current = 0;

    function goTo(idx) {
      imgs[current].classList.remove("active");
      dots[current].classList.remove("active");
      current = (idx + imgs.length) % imgs.length;
      imgs[current].classList.add("active");
      dots[current].classList.add("active");
    }

    // Auto-advance every 3 seconds
    const timer = setInterval(() => goTo(current + 1), 3000);
    carousel.addEventListener("mouseleave", () => clearInterval(timer));

    dots.forEach((dot, i) => dot.addEventListener("click", (e) => {
      e.stopPropagation();
      goTo(i);
    }));
  });
}

/** Navigate to connect page with a specific user pre-selected */
function goConnect(userId) {
  const me = authGet();
  if (!me) { showToast("Please login to connect"); openLogin(); return; }
  window.location.href = `/connect?to=${userId}`;
}

/* ════════════════════════════════════
   UTILITIES
════════════════════════════════════ */

/** Capitalize first letter of each word */
function capitalize(str) {
  if (!str) return "";
  return str.replace(/\b\w/g, c => c.toUpperCase());
}

/** Debounce a function call */
function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

/* ════════════════════════════════════
   AUTO-INIT on DOMContentLoaded
════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
  buildNavbar();
  initScrollAnimations();
});
