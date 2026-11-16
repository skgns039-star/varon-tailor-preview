/* home collection lightbox: big photo + optional ~4s muted loop clip (data-lb-video). Reduced motion → still photo only.
   Keyboard: ESC close, ←/→ prev/next, Tab stays inside. Touch: swipe left/right. */
(function () {
  var lb = document.getElementById('lb'); if (!lb) return;
  var items = [].slice.call(document.querySelectorAll('[data-lb-item]'));
  var img = lb.querySelector('.lb-img'), vid = lb.querySelector('.lb-video'), cap = lb.querySelector('.lb-cap');
  var RM = matchMedia('(prefers-reduced-motion: reduce)'), idx = 0, opener = null;
  var stage = lb.querySelector('.lb-stage');
  function go(i) {   /* switch with a short crossfade (no hard jump) */
    if (!lb.classList.contains('is-on')) return show(i);
    stage.classList.add('is-swap');
    setTimeout(function () { show(i); var done = function () { stage.classList.remove('is-swap'); }; if (img.complete) requestAnimationFrame(done); else img.onload = done; }, RM.matches ? 210 : 210);
  }
  function show(i) {
    idx = (i + items.length) % items.length; var a = items[idx];
    img.src = a.getAttribute('data-lb-img'); img.alt = a.getAttribute('data-lb-title') || '';
    cap.textContent = a.getAttribute('data-lb-title') || '';
    var v = a.getAttribute('data-lb-video');
    vid.pause(); vid.removeAttribute('src');
    if (v && !RM.matches) { vid.poster = img.src; vid.src = v; vid.hidden = false; img.hidden = true; var p = vid.play(); if (p && p.catch) p.catch(function () { vid.hidden = true; img.hidden = false; }); }
    else { vid.hidden = true; img.hidden = false; }
  }
  function open(i, from) {
    opener = from; lb.hidden = false; document.documentElement.classList.add('lb-open');
    if (window.Motion && Motion.lenis) Motion.lenis.stop();
    show(i); void lb.offsetWidth;   /* commit opacity:0 first so the fade-in always runs */
    requestAnimationFrame(function () { requestAnimationFrame(function () { lb.classList.add('is-on'); lb.querySelector('.lb-close').focus(); }); });
  }
  function close() {
    lb.classList.remove('is-on'); vid.pause();
    setTimeout(function () { lb.hidden = true; }, RM.matches ? 230 : 330);
    document.documentElement.classList.remove('lb-open');
    if (window.Motion && Motion.lenis) Motion.lenis.start();
    if (opener) opener.focus();
  }
  var tap = null, skipClick = 0;
  items.forEach(function (a, i) {
    a.addEventListener('touchstart', function (e) { var t = e.touches[0]; tap = { x: t.clientX, y: t.clientY, t: Date.now() }; }, { passive: true });
    a.addEventListener('touchend', function (e) {
      if (!tap) return; var t = e.changedTouches[0];
      if (Math.abs(t.clientX - tap.x) < 10 && Math.abs(t.clientY - tap.y) < 10 && Date.now() - tap.t < 600) { e.preventDefault(); skipClick = Date.now(); open(i, a); }
      tap = null;
    });
    a.addEventListener('click', function (e) { e.preventDefault(); if (Date.now() - skipClick < 800) return; open(i, a); });
  });
  lb.querySelectorAll('[data-lb-close]').forEach(function (b) { b.addEventListener('click', close); });
  lb.querySelector('.lb-prev').addEventListener('click', function () { go(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { go(idx + 1); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowLeft') go(idx - 1);
    else if (e.key === 'ArrowRight') go(idx + 1);
    else if (e.key === 'Tab') {
      e.preventDefault();   /* manage Tab ourselves so every engine (incl. Safari defaults) stays inside */
      var f = [].slice.call(lb.querySelectorAll('button,a[href]')).filter(function (el) { return el.offsetParent !== null; });
      var i = f.indexOf(document.activeElement);
      f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
    }
  });
  document.addEventListener('focusin', function (e) { if (lb.classList.contains('is-on') && !lb.contains(e.target)) lb.querySelector('.lb-close').focus(); });
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) go(idx + (dx < 0 ? 1 : -1)); x0 = null; });
})();
