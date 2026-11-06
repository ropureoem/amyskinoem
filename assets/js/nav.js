/* Amy Skin mobile nav toggle — vanilla JS, no dependencies.
   Toggles the slide-down mobile menu in the site header. */
(function () {
  var btn = document.querySelector('.nav-toggle');
  var menu = document.getElementById('mobileMenu');
  if (!btn || !menu) return;

  function close() {
    btn.classList.remove('is-open');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Open menu');
    menu.classList.remove('is-open');
    document.removeEventListener('click', onDocClick);
  }

  function onDocClick(e) {
    if (!e.target.closest('header.site')) close();
  }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = !menu.classList.contains('is-open');
    btn.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menu.classList.toggle('is-open', open);
    if (open) {
      document.addEventListener('click', onDocClick);
    } else {
      document.removeEventListener('click', onDocClick);
    }
  });

  menu.addEventListener('click', function (e) {
    if (e.target.closest('a')) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });
})();
