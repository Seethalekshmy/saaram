/*
  SAARAM — Interactive Scripts
  Handles: particles, scroll reveal, navbar, counters, demo animations
*/

(function () {
  'use strict';

  // -----------------------------------------------------------------------
  // Particle canvas in the hero section
  // Creates floating dots that slowly drift and connect with lines nearby
  // -----------------------------------------------------------------------
  // -----------------------------------------------------------------------
  // Unified Antigravity Particle System
  // Features: Mouse repulsion, inertia, friction, and dynamic connections
  // -----------------------------------------------------------------------
  const canvas = document.getElementById('antigravity-canvas');

  if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    const mouse = { x: -1000, y: -1000, active: false };
    const repulsionRadius = 180;
    const repulsionStrength = 0.65;
    const friction = 0.95;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      spawnParticles();
    }

    function spawnParticles() {
      particles = [];
      const count = Math.floor((canvas.width * canvas.height) / 6500);

      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          originX: Math.random() * canvas.width,
          originY: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          r: Math.random() * 2 + 0.5,
          color: Math.random() > 0.5 ? '#7c3aed' : '#06b6d4',
          alpha: Math.random() * 0.6 + 0.2,
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, i) => {
        // Mouse repulsion physics
        if (mouse.active) {
          const dx = p.x - mouse.x;
          const dy = p.y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < repulsionRadius) {
            const force = (repulsionRadius - dist) / repulsionRadius;
            p.vx += (dx / dist) * force * repulsionStrength;
            p.vy += (dy / dist) * force * repulsionStrength;
          }
        }

        // Apply velocities and friction
        p.vx *= friction;
        p.vy *= friction;
        p.x += p.vx;
        p.y += p.vy;

        // Subtle drift back toward origin or just drift randomly
        p.x += (Math.random() - 0.5) * 0.1;
        p.y += (Math.random() - 0.5) * 0.1;

        // Screen wrap
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
        ctx.globalAlpha = 1;

        // Draw connections
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx2 = p.x - p2.x;
          const dy2 = p.y - p2.y;
          const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

          if (dist2 < 100) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            const connectionAlpha = (1 - dist2 / 100) * 0.25;
            ctx.strokeStyle = `rgba(124, 58, 237, ${connectionAlpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      });

      // Mouse glow
      if (mouse.active) {
        const gradient = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, repulsionRadius);
        gradient.addColorStop(0, 'rgba(124, 58, 237, 0.1)');
        gradient.addColorStop(1, 'rgba(124, 58, 237, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    });
    window.addEventListener('mouseleave', () => {
      mouse.active = false;
    });

    resize();
    draw();
  }


  // -----------------------------------------------------------------------
  // Scroll Reveal
  // Elements with class .reveal fade in as they enter the viewport
  // -----------------------------------------------------------------------
  const revealEls = document.querySelectorAll('.reveal');

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

  revealEls.forEach((el) => revealObserver.observe(el));

  // Add a small stagger delay to groups of cards so they don't all pop in together
  document.querySelectorAll('.feature-card.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.10}s`;
  });

  document.querySelectorAll('.step-card.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.12}s`;
  });

  document.querySelectorAll('.tech-card.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.06}s`;
  });


  // -----------------------------------------------------------------------
  // Navbar — add background blur once the user scrolls past the hero
  // -----------------------------------------------------------------------
  const navbar = document.getElementById('navbar');
  const backToTop = document.getElementById('backToTop');

  window.addEventListener('scroll', () => {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 60);
    if (backToTop) backToTop.classList.toggle('visible', window.scrollY > 500);
  });


  // -----------------------------------------------------------------------
  // Mobile nav toggle — hamburger open/close
  // -----------------------------------------------------------------------
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });

    // Close the menu when the user taps a link
    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }


  // -----------------------------------------------------------------------
  // Back to top button
  // -----------------------------------------------------------------------
  if (backToTop) {
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }


  // -----------------------------------------------------------------------
  // Hero stat counters — animate numbers up when the hero section is visible
  // -----------------------------------------------------------------------
  const counters = document.querySelectorAll('[data-count]');
  let countersFired = false;

  function animateCounters() {
    if (countersFired) return;
    countersFired = true;

    counters.forEach((el) => {
      const target = parseInt(el.dataset.count, 10);
      const suffix = el.dataset.suffix || '';
      const duration = 1800;
      const start = performance.now();

      function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.round(eased * target) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      }

      requestAnimationFrame(tick);
    });
  }

  const heroSection = document.getElementById('hero');
  if (heroSection) {
    const heroObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          animateCounters();
          heroObserver.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    heroObserver.observe(heroSection);
  }


  // -----------------------------------------------------------------------
  // Demo section — cycle through ISL letters every 2 seconds
  // -----------------------------------------------------------------------
  const demoLetter = document.getElementById('demoLetter');

  if (demoLetter) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    let letterIndex = 0;

    setInterval(() => {
      letterIndex = (letterIndex + 1) % alphabet.length;
      demoLetter.textContent = alphabet[letterIndex];

      // Small pop animation on change
      demoLetter.style.transform = 'scale(1.2)';
      setTimeout(() => {
        demoLetter.style.transition = 'transform 0.25s ease';
        demoLetter.style.transform = 'scale(1)';
      }, 120);
    }, 2000);
  }


  // -----------------------------------------------------------------------
  // Demo section — typewriter effect cycling through example sentences
  // -----------------------------------------------------------------------
  const demoSentence = document.getElementById('demoSentence');

  if (demoSentence) {
    const phrases = [
      'Hello world',
      'How are you',
      'Thank you so much',
      'Nice to meet you',
      'Good morning',
    ];

    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;

    function type() {
      const phrase = phrases[phraseIndex];

      if (!isDeleting) {
        charIndex++;
        if (charIndex > phrase.length) {
          // Pause at the end before deleting
          setTimeout(() => { isDeleting = true; type(); }, 2000);
          return;
        }
      } else {
        charIndex--;
        if (charIndex < 0) {
          charIndex = 0;
          isDeleting = false;
          phraseIndex = (phraseIndex + 1) % phrases.length;
        }
      }

      demoSentence.innerHTML =
        phrase.substring(0, charIndex) + '<span class="cursor"></span>';

      setTimeout(type, isDeleting ? 45 : 75);
    }

    setTimeout(type, 1400);
  }

})();
