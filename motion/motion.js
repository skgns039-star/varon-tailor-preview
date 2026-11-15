/* motion.js — elevato.co.kr 모션 동일 재현(측정값·근거는 MOTION_SPEC.md). 2026-11-16 위젯 담당.
   순서: <link vendor/lenis.css> <link vendor/swiper-bundle.min.css> <link motion.css>
         <script vendor/lenis.min.js> <script vendor/swiper-bundle.min.js> <script motion.js>  (모두 defer 가능)
   라이브러리: Lenis 1.3.27(MIT) · Swiper 11.1.1(MIT). jQuery 없음.
   끄기: <html data-m-smooth="off"> 이면 Lenis를 쓰지 않는다. */
(function () {
  'use strict';
  var d = document, html = d.documentElement, w = window;
  var RM = w.matchMedia('(prefers-reduced-motion: reduce)');
  var PC = function () { return w.innerWidth >= 1200; };          // elevato: Lenis ≥1200, CSS 분기 ≤1200
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var M = w.Motion = w.Motion || {};

  /* 1) 페이지 진입 덮개(없으면 만든다) */
  function pageIn() {
    var ov = $('[data-m-pagein]');
    if (!ov) { ov = d.createElement('div'); ov.setAttribute('data-m-pagein', ''); ov.setAttribute('aria-hidden', 'true'); d.body.appendChild(ov); }
    ov.classList.add('is-in');
  }

  /* 2) Lenis: duration 1.5 · easing min(1, 1.001 - 2^(-10t)) · syncTouch · ≥1200px만, 미만이면 destroy */
  var lenis = null, rafId = null;
  function createLenis() {
    if (lenis || !w.Lenis || html.getAttribute('data-m-smooth') === 'off') return;
    lenis = new w.Lenis({ duration: 1.5, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }, smoothWheel: true, syncTouch: true });
    var raf = function (time) { lenis.raf(time); rafId = requestAnimationFrame(raf); };
    rafId = requestAnimationFrame(raf);
    M.lenis = lenis;
  }
  function destroyLenis() { if (lenis) { lenis.destroy(); lenis = null; M.lenis = null; } if (rafId) { cancelAnimationFrame(rafId); rafId = null; } }
  function smoothResize() { (PC() && !RM.matches) ? createLenis() : destroyLenis(); }

  /* 3) 헤더: 스크롤 방향 클래스(delta 5px, 헤더 높이 이후) + 흰 글자 구간 + 높이 변수 */
  function header() {
    var h = $('[data-m-header]'); if (!h) return;
    var last = 0, ticking = false;
    var setH = function () {
      var nav = $('[data-m-header-bar]', h) || h;
      html.style.setProperty('--m-header-h', nav.getBoundingClientRect().height + 'px');   // zoom 반영 실측(D264)
    };
    var dir = function () {
      var st = w.scrollY, hh = h.offsetHeight;
      if (Math.abs(last - st) <= 5) return;
      if (st > last && st > hh) { html.classList.add('m-scroll-down'); html.classList.remove('m-scroll-up', 'm-search-open'); }
      else if (st + w.innerHeight < html.scrollHeight) { html.classList.add('m-scroll-up'); html.classList.remove('m-scroll-down'); }
      last = st;
    };
    var invert = function () {
      var on = $$('[data-m-header-white]').some(function (el) {
        var top = el.getBoundingClientRect().top + w.scrollY;
        return w.scrollY >= top && w.scrollY < top + el.offsetHeight;
      });
      html.classList.toggle('m-header-invert', on);
    };
    w.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(function () { dir(); ticking = false; }); ticking = true; }
      invert();
    }, { passive: true });
    w.addEventListener('resize', function () { setH(); invert(); });
    setH(); invert();
  }

  /* 4) PC 메가 메뉴: 즉시 표시, 배경판 높이 = 헤더 + 패널 + 40 */
  function mega() {
    var h = $('[data-m-header]'), bg = $('[data-m-mega-bg]'); if (!h || !bg) return;
    var items = $$('[data-m-mega-item]', h);
    var off = function () {
      html.classList.remove('m-mega-active');
      $$('[data-m-mega-panel].is-show', h).forEach(function (p) { p.classList.remove('is-show'); });
      bg.style.setProperty('--m-mega-h', '100%');
    };
    items.forEach(function (it) {
      it.addEventListener('mouseenter', function () {
        if (!PC()) return;
        html.classList.remove('m-search-open');
        var panel = $('[data-m-mega-panel]', it);
        if (!panel) return off();
        $$('[data-m-mega-panel].is-show', h).forEach(function (p) { if (p !== panel) p.classList.remove('is-show'); });
        html.classList.add('m-mega-active'); panel.classList.add('is-show');
        setTimeout(function () { bg.style.setProperty('--m-mega-h', (h.offsetHeight + panel.offsetHeight + 40) + 'px'); }, 20);   // elevato setTimeout 20
      });
    });
    h.addEventListener('mouseleave', off);
    $$('[data-m-mega-off]', h).forEach(function (a) { a.addEventListener('mouseenter', off); });   // elevato .mynav a
    M.megaOff = off;
  }

  /* 5) 검색 열기/닫기 */
  function search() {
    $$('[data-m-search-toggle]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault(); if (M.megaOff) M.megaOff();
        var open = html.classList.toggle('m-search-open'); html.classList.remove('m-menu-open');
        var inp = $('[data-m-search] input'); if (inp) open ? inp.focus() : inp.blur();
      });
    });
  }

  /* 6) 높이 접기·펼치기 = elevato jQuery 3.6.0 slideDown/slideUp. 그 사이트는 jquery.easing이 swing을 easeOutQuad로 바꿔 둠(실측). 기본 400ms */
  /* jQuery처럼 height와 위아래 padding·margin을 함께 0 ↔ 원래 값으로 움직인다(padding이 있는 칸이 첫 프레임에 튀지 않게) */
  var BOX = ['height', 'paddingTop', 'paddingBottom', 'marginTop', 'marginBottom'];
  function boxOf(el) { var cs = getComputedStyle(el), o = {}; BOX.forEach(function (k) { o[k] = cs[k]; }); return o; }
  function zeroBox() { var o = {}; BOX.forEach(function (k) { o[k] = '0px'; }); return o; }
  function slide(el, open, ms, delay) {
    var reduce = RM.matches, wasOpen = el.classList.contains('is-open');
    var cur = el._mAnim ? boxOf(el) : (wasOpen ? null : zeroBox());   // 움직이는 중이면 지금 모습에서 이어 간다
    if (el._mAnim) { el._mAnim.cancel(); el._mAnim = null; }
    if (!open && !wasOpen) return;
    el.classList.add('is-open');
    var full = boxOf(el);                                              // 다 펼친 원래 값
    if (!cur) cur = full;
    var kf = [cur, open ? full : zeroBox()];
    if (reduce) { kf[0] = Object.assign({ opacity: open ? 0 : 1 }, kf[0]); kf[1] = Object.assign({ opacity: open ? 1 : 0 }, kf[1]); }  // 줄이기: 0.2s 선형 디졸브(높이도 0.2s라 아래 내용이 한 프레임에 튀지 않음, D69)
    var a = el.animate(kf, { duration: reduce ? 200 : ms, delay: reduce ? 0 : (delay || 0), easing: reduce ? 'linear' : 'cubic-bezier(.25,.46,.45,.94)', fill: 'both' });
    el._mAnim = a;
    a.onfinish = function () { a.cancel(); el._mAnim = null; if (!open) el.classList.remove('is-open'); };
  }
  M.slide = slide;
  /* data-m-acc="footer|menu|detail" 묶음 안의 [data-m-acc-head] → 같은 항목의 [data-m-acc-panel]
     footer: ≤1200만, 400ms / menu: 펼침 delay 100 + 300ms, 형제 즉시 300ms 닫힘 / detail: 400ms */
  function accordions() {
    $$('[data-m-acc]').forEach(function (group) {
      var kind = group.getAttribute('data-m-acc');
      $$('[data-m-acc-head]', group).forEach(function (head) {
        head.addEventListener('click', function (e) {
          if (kind === 'footer' && w.innerWidth > 1200) return;
          var item = head.closest('[data-m-acc-item]') || head.parentNode;
          var panel = $('[data-m-acc-panel]', item); if (!panel) return;
          e.preventDefault();
          var open = !panel.classList.contains('is-open');
          var ms = kind === 'menu' ? 300 : 400, dl = kind === 'menu' ? 100 : 0;
          $$('[data-m-acc-item]', group).forEach(function (o) {
            if (o === item) return; var p = $('[data-m-acc-panel]', o);
            if (p && p.classList.contains('is-open') && open) slide(p, false, ms, 0);
            o.classList.remove('is-active');
          });
          slide(panel, open, ms, open ? dl : (kind === 'menu' ? 100 : 0));
          item.classList.toggle('is-active', open);
        });
      });
    });
    var fix = function () { if (w.innerWidth > 1200) $$('[data-m-acc="footer"] [data-m-acc-item]').forEach(function (i) { i.classList.remove('is-active'); }); };
    w.addEventListener('resize', fix);
  }

  /* 7) 모바일 메뉴 */
  function mobileMenu() {
    var close = function () {
      html.classList.remove('m-menu-open', 'm-no-scroll');
      $$('[data-m-menu] [data-m-acc-panel].is-open').forEach(function (p) { p.classList.remove('is-open'); });
      $$('[data-m-menu] [data-m-acc-item].is-active').forEach(function (i) { i.classList.remove('is-active'); });
    };
    $$('[data-m-menu-toggle], [data-m-menu-bg]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault();
        if (html.classList.contains('m-menu-open')) close();
        else { html.classList.add('m-menu-open', 'm-no-scroll'); html.classList.remove('m-search-open'); }
        b.setAttribute && b.hasAttribute('data-m-menu-toggle') && b.setAttribute('aria-expanded', html.classList.contains('m-menu-open'));
      });
    });
    M.menuClose = close;
  }

  /* 8) 맨 위로 */
  function toTop() {
    var b = $('[data-m-totop]'); if (!b) return;
    var t = function () { b.classList.toggle('is-show', w.scrollY > 300); };
    w.addEventListener('scroll', t, { passive: true }); t();
    b.addEventListener('click', function (e) { e.preventDefault(); w.scrollTo({ top: 0, behavior: RM.matches ? 'auto' : 'smooth' }); });
  }

  /* 9) 슬라이더(Swiper 11.1.1). data-m-slider="free"(메인 상품) | "detail"(상세 사진) */
  function sliders() {
    if (!w.Swiper) return;
    $$('[data-m-slider]').forEach(function (el) {
      var kind = el.getAttribute('data-m-slider'), root = el.closest('[data-m-slider-wrap]') || el.parentNode;
      var base = { slidesPerView: 'auto', spaceBetween: 0, speed: RM.matches ? 200 : 500, grabCursor: true, loop: false, observer: true, observeParents: true,
        navigation: { nextEl: $('[data-m-next]', root), prevEl: $('[data-m-prev]', root) } };
      if (kind === 'free') base.freeMode = { enabled: true, sticky: true };
      if (kind === 'detail') { base.effect = 'slide'; base.watchSlidesProgress = true; base.pagination = { el: $('[data-m-dots]', root), clickable: true }; }
      el.classList.add('swiper');   // Swiper 11 CSS는 .swiper 기준
      el._mSwiper = new w.Swiper(el, base);
    });
  }

  /* 10) 상세: 정보 칸 sticky, 아래 감시 요소가 보이면 칸 안을 끝까지 부드럽게 스크롤 */
  function stickyWatch() {
    var s = $('[data-m-sticky]'), watch = $('[data-m-sticky-watch]'); if (!s || !watch || !w.IntersectionObserver) return;
    new IntersectionObserver(function (en) {
      s.scrollTo({ top: en[0].isIntersecting ? s.scrollHeight : 0, behavior: RM.matches ? 'auto' : 'smooth' });
    }, { threshold: 0 }).observe(watch);
  }

  /* 11) 영상: autoplay muted loop playsinline 보장(숨은 쪽은 재생 안 함) */
  function videos() {
    $$('[data-m-video] video').forEach(function (v) {
      v.muted = true; v.loop = true; v.playsInline = true; v.autoplay = true;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
    });
    var sync = function () {
      $$('[data-m-video] video').forEach(function (v) {
        if (v.offsetParent) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause();
      });
    };
    w.addEventListener('resize', sync); sync();
  }

  function init() {
    pageIn(); smoothResize(); header(); mega(); search(); accordions(); mobileMenu(); toTop(); sliders(); stickyWatch(); videos();
    w.addEventListener('resize', smoothResize);
    if (RM.addEventListener) RM.addEventListener('change', smoothResize);
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', init); else init();
})();
