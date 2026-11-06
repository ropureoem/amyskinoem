/* Amy Skin home: hero carousel, count-up stats, fade-up sections.
   Dependency-free. All motion off under prefers-reduced-motion. */
(function () {
  'use strict';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- hero carousel ---- */
  var carousel = document.getElementById('heroCarousel');
  if (carousel) {
    var slides = Array.prototype.slice.call(carousel.querySelectorAll('.slide'));
    var dots = Array.prototype.slice.call(carousel.querySelectorAll('.dot'));
    var prevBtn = carousel.querySelector('.prev');
    var nextBtn = carousel.querySelector('.next');
    var current = 0;
    var timer = null;
    var DELAY = 6000;

    function show(i) {
      current = (i + slides.length) % slides.length;
      slides.forEach(function (s, idx) { s.classList.toggle('is-active', idx === current); });
      dots.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === current);
        d.setAttribute('aria-selected', idx === current ? 'true' : 'false');
      });
    }
    function start() {
      if (reduceMotion || document.hidden) return;
      stop();
      timer = setInterval(function () { show(current + 1); }, DELAY);
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function restart() { stop(); start(); }

    if (prevBtn) prevBtn.addEventListener('click', function () { show(current - 1); restart(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { show(current + 1); restart(); });
    dots.forEach(function (d, idx) {
      d.addEventListener('click', function () { show(idx); restart(); });
    });
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    carousel.addEventListener('focusin', stop);
    carousel.addEventListener('focusout', start);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else start();
    });
    start();
  }

  /* ---- count-up stats ---- */
  var counters = Array.prototype.slice.call(document.querySelectorAll('[data-count]'));
  function setFinal(el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    el.textContent = el.getAttribute('data-format') === 'comma'
      ? target.toLocaleString('en-US') : String(target);
  }
  if (counters.length) {
    if (reduceMotion || !('IntersectionObserver' in window)) {
      counters.forEach(setFinal);
    } else {
      var counterObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          counterObs.unobserve(el);
          var target = parseInt(el.getAttribute('data-count'), 10);
          var comma = el.getAttribute('data-format') === 'comma';
          var start = null;
          var dur = 1200;
          function tick(now) {
            if (start === null) start = now;
            var p = Math.min((now - start) / dur, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            var val = Math.round(target * eased);
            el.textContent = comma ? val.toLocaleString('en-US') : String(val);
            if (p < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { counterObs.observe(el); });
    }
  }

  /* ---- fade-up on sections (added by JS only, so no-JS stays visible) ---- */
  var sections = Array.prototype.slice.call(document.querySelectorAll('main > section:not(.hero)'));
  if (sections.length) {
    if (reduceMotion || !('IntersectionObserver' in window)) return; /* CSS keeps them visible */
    sections.forEach(function (s) { s.classList.add('reveal'); });
    var revealObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          revealObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    sections.forEach(function (s) { revealObs.observe(s); });
  }
})();
