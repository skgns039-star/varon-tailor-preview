/* contact form: type → fields, consent detail, required check. Sending destination [확인 필요] (form has no action; nothing is sent). */
(function () {
  var form = document.getElementById('form'); if (!form) return;
  var radios = form.querySelectorAll('input[name=type]');
  function show() {
    var t = (form.querySelector('input[name=type]:checked') || {}).value || '';
    form.querySelectorAll('[data-show]').forEach(function (el) { var off = t ? el.getAttribute('data-show').split(' ').indexOf(t) < 0 : el.getAttribute('data-show').indexOf('consult') < 0; el.classList.toggle('is-off', off); el.querySelectorAll('input,select').forEach(function (i) { i.disabled = off; }); });
  }
  function fromHash() {
    var h = location.hash.slice(1), r = form.querySelector('input[name=type][value="' + h + '"]');
    if (r) { r.checked = true; show(); }
  }
  radios.forEach(function (r) { r.addEventListener('change', show); });
  addEventListener('hashchange', fromHash); fromHash(); show();
  var tg = form.querySelector('.ct-toggle'), det = document.getElementById('consent-detail');
  tg.addEventListener('click', function () { var o = tg.getAttribute('aria-expanded') === 'true'; tg.setAttribute('aria-expanded', String(!o)); det.hidden = o; tg.textContent = o ? '내용 보기' : '접기'; });
  form.addEventListener('submit', function (e) {
    e.preventDefault(); var ok = true;
    form.querySelectorAll('[required]').forEach(function (f) {
      var hp = form.querySelector('[data-error="' + f.name + '"]'); if (!hp) return;
      var v = f.type === 'radio' ? !!form.querySelector('input[name=' + f.name + ']:checked') : f.type === 'checkbox' ? f.checked : f.value.trim() !== '' && f.validity.valid;
      f.setAttribute('aria-invalid', String(!v)); hp.textContent = v ? '' : '필수 항목을 확인해 주세요.'; ok = ok && v;
    });
    form.querySelector('.ct-status').textContent = ok ? '입력 내용을 확인했습니다. 문의 접수 방법 [확인 필요]' : '';
  });
})();
