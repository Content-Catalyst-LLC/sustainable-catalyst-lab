(function (w, d) {
  'use strict';

  const VERSION = '0.152.0.5';
  const aliases = Object.freeze({
    climate: 'climate-maps',
    evidence: 'evidence-decisions',
    marine: 'marine-biology',
    'astronomy-observations': 'space-telescopes'
  });

  function canonical(value) {
    const raw = String(value || 'overview').trim();
    return aliases[raw] || raw || 'overview';
  }

  function all(root, selector) {
    return root && root.querySelectorAll ? Array.from(root.querySelectorAll(selector)) : [];
  }

  function findPanel(root, id) {
    return all(root, '[data-lab-module]').find(function (panel) {
      return panel.dataset && panel.dataset.labModule === id;
    }) || null;
  }

  function markDeferred(panel) {
    if (!panel) return;
    const module = panel.dataset ? panel.dataset.labModule : '';
    const selectors = {
      'graph-studio': '[data-gs-v0470-status]',
      'model-studio': '[data-ms-v0460-status]',
      experiments: '[data-exp-v0300-status]'
    };
    const selector = selectors[module];
    if (!selector) return;
    const status = panel.querySelector(selector);
    if (status) {
      status.textContent = 'Lab safe boot is active. Navigation is available; advanced module execution is deferred while the production runtime is stabilized.';
      status.dataset.tone = 'ready';
    }
  }

  function setActiveButtons(root, id) {
    all(root, '[data-lab-module-button]').forEach(function (button) {
      button.classList.toggle('is-active', button.dataset.labModuleButton === id);
      button.setAttribute('aria-current', button.dataset.labModuleButton === id ? 'page' : 'false');
    });
    all(root, '[data-open-module]').forEach(function (button) {
      const on = canonical(button.dataset.openModule) === id;
      button.classList.toggle('is-active', on);
      if (button.hasAttribute('data-v0481-workspace') || button.hasAttribute('data-v0483-primary')) {
        button.setAttribute('aria-current', on ? 'page' : 'false');
      }
    });
  }

  function openModule(root, requested, updateUrl) {
    const id = canonical(requested);
    const panel = findPanel(root, id) || findPanel(root, 'overview');
    if (!panel) return false;
    const selected = panel.dataset.labModule || 'overview';

    all(root, '[data-lab-module]').forEach(function (item) {
      const active = item === panel;
      item.hidden = !active;
      item.setAttribute('aria-hidden', active ? 'false' : 'true');
    });

    root.dataset.activeModule = selected;
    root.dataset.scLabRuntimeState = 'safe-ready';
    root.dataset.scLabSafeBoot = VERSION;
    setActiveButtons(root, selected);
    markDeferred(panel);

    const nav = root.querySelector('[data-lab-nav]');
    const navToggle = root.querySelector('[data-lab-nav-toggle]');
    if (nav) nav.classList.remove('is-open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');

    if (updateUrl && w.history && w.history.replaceState) {
      try {
        const url = new URL(w.location.href);
        if (selected === 'overview') url.searchParams.delete('sc_lab_module');
        else url.searchParams.set('sc_lab_module', selected);
        w.history.replaceState({}, '', url.toString());
      } catch (_) {}
    }

    try {
      root.dispatchEvent(new CustomEvent('sc-lab:safe-module-opened', { detail: { module: selected, version: VERSION } }));
    } catch (_) {}
    return true;
  }

  function wire(root) {
    if (!root || root.dataset.scLabSafeBootWired === '1') return;
    root.dataset.scLabSafeBootWired = '1';
    root.dataset.scLabRuntimeState = 'safe-initializing';

    const version = root.querySelector('.sc-lab-version');
    if (version) version.textContent = 'v' + VERSION;

    root.addEventListener('click', function (event) {
      const open = event.target.closest('[data-open-module], [data-lab-module-button]');
      if (open && root.contains(open)) {
        event.preventDefault();
        const id = open.dataset.openModule || open.dataset.labModuleButton;
        openModule(root, id, true);
        return;
      }

      const navToggle = event.target.closest('[data-lab-nav-toggle]');
      if (navToggle && root.contains(navToggle)) {
        event.preventDefault();
        const nav = root.querySelector('[data-lab-nav]');
        if (nav) {
          const next = !nav.classList.contains('is-open');
          nav.classList.toggle('is-open', next);
          navToggle.setAttribute('aria-expanded', next ? 'true' : 'false');
        }
        return;
      }

      const toolsToggle = event.target.closest('[data-v0483-tools-toggle]');
      if (toolsToggle && root.contains(toolsToggle)) {
        event.preventDefault();
        const tools = root.querySelector('[data-v0483-tools]');
        if (tools) {
          tools.hidden = !tools.hidden;
          toolsToggle.setAttribute('aria-expanded', tools.hidden ? 'false' : 'true');
        }
        return;
      }

      const toolsClose = event.target.closest('[data-v0483-tools-close]');
      if (toolsClose && root.contains(toolsClose)) {
        const tools = root.querySelector('[data-v0483-tools]');
        if (tools) tools.hidden = true;
      }
    });

    const search = root.querySelector('[data-v0483-tools-search]');
    if (search) {
      search.addEventListener('input', function () {
        const q = String(search.value || '').trim().toLowerCase();
        all(root, '[data-v0483-tools-groups] [data-lab-module-button]').forEach(function (button) {
          button.hidden = !!q && !String(button.textContent || '').toLowerCase().includes(q);
        });
      });
    }

    d.addEventListener('keydown', function (event) {
      if ((event.metaKey || event.ctrlKey) && String(event.key).toLowerCase() === 'k') {
        const input = root.querySelector('[data-lab-command-input]');
        if (input) { event.preventDefault(); input.focus(); }
      }
    });

    let initial = root.dataset.initialModule || 'overview';
    try { initial = new URL(w.location.href).searchParams.get('sc_lab_module') || initial; } catch (_) {}
    openModule(root, initial, false);
  }

  function boot() {
    all(d, '.sc-lab-app').forEach(wire);
  }

  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();

  w.SCLabSafeBootV015205Runtime = Object.freeze({ version: VERSION, boot: boot });
})(window, document);
