/* ═══════════════════════════════════════════════════════════════
   Niraj Byanjankar Portfolio — main.js
   Handles: navbar, typing effect, AOS, stats counter, contact form
═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. Navbar scroll behaviour & active link ──────────────── */
  const navbar  = document.getElementById('navbar');
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');

  window.addEventListener('scroll', () => {
    // Scrolled style
    if (window.scrollY > 50) navbar.classList.add('scrolled');
    else navbar.classList.remove('scrolled');

    // Active nav link
    let current = '';
    sections.forEach(sec => {
      const top = sec.offsetTop - 100;
      if (window.scrollY >= top) current = sec.getAttribute('id');
    });
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) link.classList.add('active');
    });

    // Back to top
    const btn = document.getElementById('backToTop');
    if (window.scrollY > 400) btn.classList.add('visible');
    else btn.classList.remove('visible');
  });

  // Smooth scroll for nav links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
        // Close mobile menu
        document.getElementById('navLinks').classList.remove('open');
      }
    });
  });

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const navLinksEl = document.getElementById('navLinks');
  navToggle.addEventListener('click', () => navLinksEl.classList.toggle('open'));


  /* ── 2. Back to top ─────────────────────────────────────────── */
  document.getElementById('backToTop').addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });


  /* ── 3. Typing effect ───────────────────────────────────────── */
  const roles = [
    'Principal Software Engineer',
    'Data Governance Leader',
    'Google Cloud Architect',
    'AI/ML Practitioner',
    'DevSecOps Engineer',
    'Full Stack Developer',
  ];
  let roleIndex = 0, charIndex = 0, isDeleting = false;
  const typingEl = document.getElementById('typingText');

  function type() {
    if (!typingEl) return;
    const current = roles[roleIndex];
    if (isDeleting) {
      typingEl.textContent = current.substring(0, charIndex - 1);
      charIndex--;
    } else {
      typingEl.textContent = current.substring(0, charIndex + 1);
      charIndex++;
    }
    let speed = isDeleting ? 60 : 100;
    if (!isDeleting && charIndex === current.length) {
      speed = 2000; // pause at end
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      roleIndex = (roleIndex + 1) % roles.length;
      speed = 400;
    }
    setTimeout(type, speed);
  }
  type();


  /* ── 4. Scroll-triggered animations (AOS-lite) ─────────────── */
  const aosElements = document.querySelectorAll('[data-aos]');

  const aosObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = parseInt(entry.target.dataset.aosDelay || '0');
        setTimeout(() => entry.target.classList.add('aos-animate'), delay);
        aosObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

  aosElements.forEach(el => aosObserver.observe(el));


  /* ── 5. Stats counter ───────────────────────────────────────── */
  const statNumbers = document.querySelectorAll('.stat-number');

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.target);
        let count = 0;
        const duration = 1500;
        const step = Math.ceil(target / (duration / 30));
        const timer = setInterval(() => {
          count += step;
          if (count >= target) { count = target; clearInterval(timer); }
          el.textContent = count;
        }, 30);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(el => counterObserver.observe(el));


  /* ── 6. Particle generator (hero bg) ────────────────────────── */
  const container = document.getElementById('particles');
  if (container) {
    for (let i = 0; i < 50; i++) {
      const dot = document.createElement('div');
      dot.style.cssText = `
        position: absolute;
        width: ${Math.random() * 3 + 1}px;
        height: ${Math.random() * 3 + 1}px;
        background: rgba(0, 212, 255, ${Math.random() * 0.4 + 0.1});
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: float ${Math.random() * 10 + 8}s linear infinite;
        animation-delay: ${Math.random() * 8}s;
      `;
      container.appendChild(dot);
    }
    // CSS for float animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes float {
        0%   { transform: translateY(0)   translateX(0); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translateY(-120vh) translateX(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 100}px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }


  /* ── 7. Contact form ─────────────────────────────────────────── */
  const form       = document.getElementById('contactForm');
  const submitBtn  = document.getElementById('submitBtn');
  const statusEl   = document.getElementById('formStatus');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Clear previous state
      statusEl.className = 'form-status';
      statusEl.textContent = '';
      clearErrors();

      // Gather data
      const name    = document.getElementById('name').value.trim();
      const email   = document.getElementById('email').value.trim();
      const subject = document.getElementById('subject').value.trim();
      const message = document.getElementById('message').value.trim();

      // Validate
      let valid = true;
      if (!name)    { showError('name',    'nameError',    'Please enter your name.');        valid = false; }
      if (!email)   { showError('email',   'emailError',   'Please enter your email.');        valid = false; }
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                      showError('email',   'emailError',   'Please enter a valid email.');     valid = false; }
      if (!subject) { showError('subject', 'subjectError', 'Please enter a subject.');         valid = false; }
      if (!message) { showError('message', 'messageError', 'Please enter a message.');         valid = false; }
      if (!valid) return;

      // Send
      submitBtn.classList.add('loading');
      submitBtn.querySelector('span').textContent = 'Sending…';

      try {
        const res  = await fetch('/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, subject, message }),
        });
        const data = await res.json();

        if (data.success) {
          statusEl.className = 'form-status success';
          statusEl.textContent = '✓ ' + data.message;
          form.reset();
        } else {
          statusEl.className = 'form-status error';
          statusEl.textContent = '✗ ' + (data.error || 'Something went wrong.');
        }
      } catch (err) {
        statusEl.className = 'form-status error';
        statusEl.textContent = '✗ Network error. Please try again.';
      } finally {
        submitBtn.classList.remove('loading');
        submitBtn.querySelector('span').textContent = 'Send Message';
      }
    });
  }

  function showError(fieldId, errorId, msg) {
    document.getElementById(fieldId).classList.add('error');
    document.getElementById(errorId).textContent = msg;
  }
  function clearErrors() {
    ['name','email','subject','message'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.remove('error');
    });
    ['nameError','emailError','subjectError','messageError'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = '';
    });
  }

});
