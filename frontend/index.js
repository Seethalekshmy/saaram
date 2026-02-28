/* ══════════════════════════════════════════════
   SAARAM — Interactive Scripts
   Particles · Scroll Reveal · Navigation · Counters
   ══════════════════════════════════════════════ */

(function () {
  'use strict';

  // ─── Particle System ───
  const canvas = document.getElementById('particles-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animId;

    function resize() {
      const hero = canvas.parentElement;
      canvas.width = hero.offsetWidth;
      canvas.height = hero.offsetHeight;
    }

    function createParticles() {
      particles = [];
      const count = Math.floor((canvas.width * canvas.height) / 12000);
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 2 + 0.5,
          dx: (Math.random() - 0.5) * 0.4,
          dy: (Math.random() - 0.5) * 0.4,
          alpha: Math.random() * 0.5 + 0.1,
        });
      }
    }

    function drawParticles() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.x += p.dx;
        p.y += p.dy;

        // Wrap around edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(124, 58, 237, ${p.alpha})`;
        ctx.fill();
      });

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(124, 58, 237, ${0.08 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(drawParticles);
    }

    resize();
    createParticles();
    drawParticles();

    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });
  }

  // ─── Scroll Reveal ───
  const revealElements = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );
  revealElements.forEach((el) => revealObserver.observe(el));

  // ─── Navbar scroll styling ───
  const navbar = document.getElementById('navbar');
  const backToTop = document.getElementById('backToTop');

  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY > 60;
    navbar.classList.toggle('scrolled', scrolled);
    backToTop.classList.toggle('visible', window.scrollY > 500);
  });

  // ─── Mobile nav toggle ───
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });

    // Close mobile menu when a link is clicked
    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });
  }

  // ─── Back to top ───
  if (backToTop) {
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ─── Counter Animation (Hero Stats) ───
  const counters = document.querySelectorAll('[data-count]');
  let countersDone = false;

  function animateCounters() {
    if (countersDone) return;
    countersDone = true;

    counters.forEach((el) => {
      const target = parseInt(el.dataset.count, 10);
      const suffix = el.dataset.suffix || '';
      const duration = 1800;
      const start = performance.now();

      function step(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(eased * target);
        el.textContent = current + suffix;
        if (progress < 1) requestAnimationFrame(step);
      }

      requestAnimationFrame(step);
    });
  }

  // Trigger counters when hero is visible
  const heroObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounters();
          heroObserver.disconnect();
        }
      });
    },
    { threshold: 0.3 }
  );
  const heroSection = document.getElementById('hero');
  if (heroSection) heroObserver.observe(heroSection);

  // ─── Demo Section — Letter Cycling ───
  const demoLetter = document.getElementById('demoLetter');
  const demoSentence = document.getElementById('demoSentence');

  if (demoLetter) {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    let idx = 0;
    setInterval(() => {
      idx = (idx + 1) % letters.length;
      demoLetter.textContent = letters[idx];
      demoLetter.style.transform = 'scale(1.2)';
      setTimeout(() => {
        demoLetter.style.transition = 'transform 0.3s';
        demoLetter.style.transform = 'scale(1)';
      }, 150);
    }, 2000);
  }

  // ─── Demo Sentence Typing Effect ───
  if (demoSentence) {
    const phrases = [
      'Hello world',
      'How are you',
      'Thank you so much',
      'Nice to meet you',
      'Good morning',
    ];
    let phraseIdx = 0;
    let charIdx = 0;
    let isDeleting = false;

    function typeSentence() {
      const currentPhrase = phrases[phraseIdx];

      if (!isDeleting) {
        charIdx++;
        if (charIdx > currentPhrase.length) {
          setTimeout(() => {
            isDeleting = true;
            typeSentence();
          }, 2000);
          return;
        }
      } else {
        charIdx--;
        if (charIdx < 0) {
          charIdx = 0;
          isDeleting = false;
          phraseIdx = (phraseIdx + 1) % phrases.length;
        }
      }

      demoSentence.innerHTML =
        currentPhrase.substring(0, charIdx) + '<span class="cursor"></span>';

      const speed = isDeleting ? 50 : 80;
      setTimeout(typeSentence, speed);
    }

    // Start after a short delay
    setTimeout(typeSentence, 1500);
  }

  // ─── Feature card staggered reveal ───
  const featureCards = document.querySelectorAll('.feature-card.reveal');
  featureCards.forEach((card, i) => {
    card.style.transitionDelay = `${i * 0.1}s`;
  });

  // Step cards staggered reveal
  const stepCards = document.querySelectorAll('.step-card.reveal');
  stepCards.forEach((card, i) => {
    card.style.transitionDelay = `${i * 0.12}s`;
  });

  // Tech cards staggered reveal
  const techCards = document.querySelectorAll('.tech-card.reveal');
  techCards.forEach((card, i) => {
    card.style.transitionDelay = `${i * 0.06}s`;
  });
})();
