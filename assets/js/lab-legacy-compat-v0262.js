(function () {
  'use strict';

  var cfg = window.SCLabCompatibilityV0262Config || { version: '0.26.2', aliases: {} };
  var aliases = cfg.aliases || {};
  var root = null;
  var activeModule = 'overview';
  var errors = [];
  var initializedObjects = [];

  function slug(value) {
    return String(value || '')
      .trim()
      .toLowerCase()
      .replace(/&/g, ' and ')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function canonical(value) {
    var key = slug(value);
    return aliases[key] || key;
  }

  function getRoot() {
    return document.querySelector('[data-sc-lab-app], .sc-lab-app, .sc-lab, #sc-lab-app') || document.body;
  }

  function queryModule() {
    var params = new URLSearchParams(window.location.search);
    return canonical(params.get('sc_lab_module') || params.get('lab_module') || params.get('module') || window.location.hash.slice(1) || 'overview');
  }

  function candidateIds(moduleName) {
    var id = canonical(moduleName);
    var candidates = [id];
    if (id === 'astronomy-lab') {
      candidates.push('astronomy-laboratory', 'astrophysics', 'astronomy');
    } else if (id === 'astronomy') {
      candidates.push('space-observations', 'space-telescopes', 'space', 'astronomy-releases');
    } else if (id === 'marine') {
      candidates.push('marine-biology', 'marine-biodiversity', 'ocean-biology');
    }
    return candidates.filter(function (item, index, list) { return list.indexOf(item) === index; });
  }

  function panelSelectors(id) {
    var escaped = window.CSS && window.CSS.escape ? window.CSS.escape(id) : id.replace(/[^a-z0-9_-]/gi, '');
    return [
      '[data-sc-lab-panel="' + escaped + '"]',
      '[data-panel="' + escaped + '"]',
      '[data-module-panel="' + escaped + '"]',
      '#sc-lab-panel-' + escaped,
      '#sc-lab-' + escaped,
      '#lab-' + escaped,
      '#panel-' + escaped,
      'section[id="' + escaped + '"]'
    ];
  }

  function findPanel(moduleName) {
    var ids = candidateIds(moduleName);
    for (var i = 0; i < ids.length; i += 1) {
      var selectors = panelSelectors(ids[i]);
      for (var j = 0; j < selectors.length; j += 1) {
        var found = root.querySelector(selectors[j]);
        if (found) return found;
      }
    }

    var headings = root.querySelectorAll('h2, h3, [data-panel-title], .sc-lab-panel-title');
    var expected = candidateIds(moduleName);
    for (var k = 0; k < headings.length; k += 1) {
      var text = slug(headings[k].textContent);
      if (expected.some(function (id) { return text === id || text.indexOf(id) !== -1; })) {
        return headings[k].closest('[data-sc-lab-panel], [data-panel], .sc-lab-panel, .sc-lab__panel, section, article');
      }
    }
    return null;
  }

  function allPanels() {
    var selectors = '[data-sc-lab-panel], [data-panel].sc-lab-panel, [data-module-panel], .sc-lab__panel, .sc-lab-panel';
    return Array.prototype.slice.call(root.querySelectorAll(selectors));
  }

  function navTarget(element) {
    var raw = element.getAttribute('data-sc-lab-target') ||
      element.getAttribute('data-panel-target') ||
      element.getAttribute('data-module') ||
      element.getAttribute('data-target-panel') || '';
    if (raw) return canonical(raw);

    var href = element.getAttribute('href') || '';
    if (href) {
      try {
        var url = new URL(href, window.location.href);
        var fromQuery = url.searchParams.get('sc_lab_module') || url.searchParams.get('lab_module') || url.searchParams.get('module');
        if (fromQuery) return canonical(fromQuery);
        if (url.hash) return canonical(url.hash.slice(1));
      } catch (err) {
        // Ignore malformed optional navigation URLs.
      }
    }
    return canonical(element.textContent);
  }

  function updateNavigation(moduleName) {
    var controls = root.querySelectorAll('[data-sc-lab-target], [data-panel-target], [data-module], [data-target-panel], a[href*="sc_lab_module="], a[href^="#"], button');
    Array.prototype.forEach.call(controls, function (control) {
      var target = navTarget(control);
      if (!target) return;
      var active = target === moduleName || (moduleName === 'astronomy-lab' && target === 'astronomy-laboratory');
      control.classList.toggle('is-active', active);
      control.setAttribute('aria-current', active ? 'page' : 'false');
    });
  }

  function dispatchReady(moduleName, panel) {
    var detail = { module: moduleName, panel: panel, version: cfg.version, compatibility: true };
    ['sc-lab:module-ready', 'sc:lab:module-ready', 'sc_lab_module_ready', 'sc-lab-v0262-ready'].forEach(function (name) {
      document.dispatchEvent(new CustomEvent(name, { detail: detail }));
      window.dispatchEvent(new CustomEvent(name, { detail: detail }));
    });
  }

  function callInitializer(target, moduleName, panel) {
    if (!target || initializedObjects.indexOf(target) !== -1) return;
    var methods = ['mount', 'init', 'bootstrap', 'start'];
    for (var i = 0; i < methods.length; i += 1) {
      if (typeof target[methods[i]] === 'function') {
        try {
          target[methods[i]](panel, { module: moduleName, compatibility: true });
          initializedObjects.push(target);
        } catch (err) {
          errors.push('Initializer ' + methods[i] + ' failed for ' + moduleName + ': ' + err.message);
        }
        return;
      }
    }
  }

  function runLegacyInitializers(moduleName, panel) {
    var pascal = moduleName.split('-').map(function (part) {
      return part.charAt(0).toUpperCase() + part.slice(1);
    }).join('');
    var names = [
      'SCLab' + pascal,
      'SCLab' + (moduleName === 'marine' ? 'MarineBiology' : pascal),
      'SCLab' + (moduleName === 'astronomy-lab' ? 'Astronomy' : pascal)
    ];
    names.forEach(function (name) { callInitializer(window[name], moduleName, panel); });
    if (window.SCLabModules) callInitializer(window.SCLabModules[moduleName], moduleName, panel);
    if (window.SCLab && window.SCLab.modules) callInitializer(window.SCLab.modules[moduleName], moduleName, panel);
  }

  function setUrl(moduleName, push) {
    var url = new URL(window.location.href);
    url.searchParams.set('sc_lab_module', moduleName);
    url.searchParams.set('sc_lab_legacy', '1');
    url.hash = '';
    window.history[push ? 'pushState' : 'replaceState']({ scLabModule: moduleName }, '', url.toString());
  }

  function showError(message) {
    errors.push(message);
    var existing = document.getElementById('sc-lab-v0262-runtime-error');
    if (!existing) {
      existing = document.createElement('div');
      existing.id = 'sc-lab-v0262-runtime-error';
      existing.className = 'sc-lab-v0262-runtime-error';
      existing.setAttribute('role', 'alert');
      root.insertBefore(existing, root.firstChild);
    }
    existing.innerHTML = '<strong>Laboratory compatibility warning</strong><p>' + String(message).replace(/[&<>]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
    }) + '</p>';
  }

  function activate(moduleName, options) {
    options = options || {};
    var requested = canonical(moduleName || 'overview');
    var panel = findPanel(requested);

    if (!panel) {
      var current = queryModule();
      if (options.reload !== false && current !== requested) {
        var url = new URL(window.location.href);
        url.searchParams.set('sc_lab_module', requested);
        url.searchParams.set('sc_lab_legacy', '1');
        window.location.assign(url.toString());
        return false;
      }
      showError('The “' + requested + '” laboratory panel was not present in the rendered markup. The compatibility layer kept the rest of the Lab available and recorded this diagnostic.');
      return false;
    }

    var panels = allPanels();
    panels.forEach(function (candidate) {
      var isTarget = candidate === panel;
      candidate.hidden = !isTarget;
      candidate.classList.toggle('is-active', isTarget);
      candidate.setAttribute('aria-hidden', isTarget ? 'false' : 'true');
    });
    panel.hidden = false;
    panel.removeAttribute('inert');
    panel.classList.add('is-active');
    panel.setAttribute('aria-hidden', 'false');

    activeModule = requested;
    updateNavigation(requested);
    if (options.updateUrl !== false) setUrl(requested, options.pushState === true);
    dispatchReady(requested, panel);
    window.setTimeout(function () { runLegacyInitializers(requested, panel); }, 0);
    return true;
  }

  function bindNavigation() {
    root.addEventListener('click', function (event) {
      var control = event.target.closest('[data-sc-lab-target], [data-panel-target], [data-module], [data-target-panel], a[href*="sc_lab_module="], a[href^="#"]');
      if (!control || !root.contains(control)) return;
      var target = navTarget(control);
      if (!target || target.length > 80) return;
      var known = findPanel(target) || Object.prototype.hasOwnProperty.call(aliases, slug(control.textContent));
      if (!known && !control.hasAttribute('data-sc-lab-target') && !control.hasAttribute('data-panel-target') && !control.hasAttribute('data-module')) return;
      event.preventDefault();
      activate(target, { pushState: true });
    });

    window.addEventListener('popstate', function () {
      activate(queryModule(), { updateUrl: false, reload: false });
    });
  }

  function boot() {
    root = getRoot();
    root.classList.add('sc-lab-v0262-compatible');
    bindNavigation();
    var requested = queryModule();
    if (!activate(requested, { updateUrl: false, reload: false }) && requested !== 'overview') {
      activate('overview', { updateUrl: false, reload: false });
    }
  }

  window.SCLabCompatibilityV0262 = {
    version: cfg.version,
    activate: activate,
    canonical: canonical,
    status: function () {
      return {
        version: cfg.version,
        activeModule: activeModule,
        legacyMode: true,
        panelCount: root ? allPanels().length : 0,
        activePanelFound: !!(root && findPanel(activeModule)),
        errors: errors.slice()
      };
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
}());
