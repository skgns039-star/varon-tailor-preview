/* VARON TAILOR — page-only extras. All motion (page-in, Lenis, header, mega menu, accordions, sliders, to-top, video)
   lives in motion/motion.js (widget agent). This file only adds:
   1) --vh fixed per width (avoids 100vh feedback loops; reference uses the same --vh idea)
   2) hero caption lines (reference burns subtitles into its film; our AI film has none, so HTML lines switch like subtitles) */
(function () {
  var html = document.documentElement, vw0 = 0;
  function setVh() { if (innerWidth !== vw0) { vw0 = innerWidth; html.style.setProperty('--vh', innerHeight / 100 + 'px'); } }
  setVh(); addEventListener('resize', setVh);
  document.addEventListener('DOMContentLoaded', function () {
    var sub = document.querySelector('.hero .sub[data-lines]');
    if (!sub) return;
    var lines = JSON.parse(sub.getAttribute('data-lines')), i = 0;
    sub.innerHTML = lines[0];
    setInterval(function () { i = (i + 1) % lines.length; sub.innerHTML = lines[i]; }, 4200);
  });
})();
