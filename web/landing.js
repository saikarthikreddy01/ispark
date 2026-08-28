(function () {
  'use strict';

  var triggers = Array.prototype.slice.call(document.querySelectorAll('[data-landing-target]'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('[data-landing-panel]'));
  var content = document.getElementById('landing-content');

  function openPanel(name, options) {
    options = options || {};
    var target = document.querySelector('[data-landing-panel="' + name + '"]');
    if (!target) return;

    panels.forEach(function (panel) {
      var selected = panel === target;
      panel.hidden = !selected;
      panel.classList.toggle('is-open', selected);
    });

    triggers.forEach(function (trigger) {
      var selected = trigger.dataset.landingTarget === name;
      trigger.classList.toggle('active', selected);
      trigger.setAttribute('aria-selected', String(selected));
    });

    if (content) content.removeAttribute('data-empty');
    if (options.updateHash !== false && history.replaceState) history.replaceState(null, '', '#' + name);

    window.setTimeout(function () {
      window.dispatchEvent(new Event('resize'));
      if (options.scroll !== false) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      if (options.focus) target.focus({ preventScroll: true });
    }, 30);
  }

  triggers.forEach(function (trigger) {
    trigger.addEventListener('click', function () { openPanel(trigger.dataset.landingTarget, { focus: true }); });
  });

  window.addEventListener('hashchange', function () {
    var name = location.hash.replace('#', '');
    if (name) openPanel(name, { updateHash: false });
  });

  var initial = location.hash.replace('#', '');
  if (initial && document.querySelector('[data-landing-panel="' + initial + '"]')) {
    openPanel(initial, { updateHash: false, scroll: false });
  } else if (content) {
    content.setAttribute('data-empty', 'true');
  }
})();
