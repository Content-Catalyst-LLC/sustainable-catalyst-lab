(function () {
  'use strict';

  if (window.__SCLabRuntimeStabilityV0254) {
    return;
  }
  window.__SCLabRuntimeStabilityV0254 = true;

  var config = window.SCLabRuntimeV0254 || {};
  var state = {
    activeModule: String(config.defaultModule || 'overview'),
    controller: null,
    requestId: 0,
    mountedAt: Date.now(),
    lastError: null
  };

  function validSlug(value) {
    return /^[a-z0-9][a-z0-9-]{0,79}$/.test(String(value || ''));
  }

  function shell() {
    return document.querySelector('[data-sc-lab-runtime-shell="0.25.4"]');
  }

  function host(root) {
    return root ? root.querySelector('[data-sc-lab-lazy-host]') : null;
  }

  function currentPanel(root) {
    return root ? root.querySelector('[data-module-panel]') : null;
  }

  function setBusy(root, busy, message) {
    if (!root) {
      return;
    }
    root.setAttribute('aria-busy', busy ? 'true' : 'false');
    var status = root.querySelector('[data-sc-lab-runtime-bar] .sc-lab-runtime-status-v0254');
    if (status && message) {
      status.textContent = message;
    }
  }

  function updateMeta(root, module) {
    if (!root) {
      return;
    }
    root.setAttribute('data-sc-lab-active-module', module);
    var meta = root.querySelector('[data-sc-lab-runtime-meta]');
    if (meta) {
      meta.textContent = 'v0.25.4 · ' + module;
    }

    root.querySelectorAll('[data-lab-module]').forEach(function (button) {
      var selected = button.getAttribute('data-lab-module') === module;
      button.classList.toggle('is-active', selected);
      if (selected) {
        button.setAttribute('aria-current', 'page');
      } else {
        button.removeAttribute('aria-current');
      }
    });
  }

  function moduleFromLocation() {
    try {
      var value = new URL(window.location.href).searchParams.get('sc_lab_module');
      return validSlug(value) ? value : 'overview';
    } catch (error) {
      return 'overview';
    }
  }

  function writeLocation(module, replace) {
    if (!window.history || !window.history.pushState) {
      return;
    }
    var url = new URL(window.location.href);
    url.searchParams.set('sc_lab_module', module);
    url.searchParams.delete('sc_lab_safe');
    var method = replace ? 'replaceState' : 'pushState';
    window.history[method]({ scLabModule: module }, '', url.toString());
  }

  function loadingPanel(module) {
    return '<section class="sc-lab-runtime-loading-v0254" data-module-panel="' + module + '" data-sc-lab-loading="1" role="status" aria-live="polite">' +
      '<span class="sc-lab-runtime-spinner-v0254" aria-hidden="true"></span>' +
      '<div><strong>Loading laboratory</strong><p>Preparing only the selected module.</p></div>' +
      '</section>';
  }

  function errorPanel(module, message) {
    var safeMessage = String(message || 'The selected laboratory could not be loaded.')
      .replace(/[&<>"']/g, function (character) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character];
      });
    return '<section class="sc-lab-runtime-error-v0254" data-module-panel="' + module + '" role="alert">' +
      '<p class="sc-lab-runtime-status-v0254">Module recovery</p>' +
      '<h3>Laboratory did not load</h3><p>' + safeMessage + '</p>' +
      '<button type="button" data-sc-lab-runtime-action="reload">Try again</button> ' +
      '<button type="button" data-sc-lab-runtime-action="overview">Return to overview</button>' +
      '</section>';
  }

  function announceLifecycle(name, detail) {
    document.dispatchEvent(new CustomEvent(name, { detail: detail || {} }));
  }

  async function loadModule(module, options) {
    options = options || {};
    module = validSlug(module) ? module : 'overview';

    var root = shell();
    var panelHost = host(root);
    if (!root || !panelHost) {
      return;
    }

    if (state.controller) {
      state.controller.abort();
    }

    state.controller = new AbortController();
    state.requestId += 1;
    var requestId = state.requestId;
    var previous = currentPanel(root);

    announceLifecycle('sc:lab:module-unmounting', {
      module: state.activeModule,
      nextModule: module,
      panel: previous
    });

    panelHost.querySelectorAll('[data-module-panel]').forEach(function (node) {
      node.remove();
    });
    panelHost.insertAdjacentHTML('beforeend', loadingPanel(module));
    setBusy(root, true, 'Loading ' + module.replace(/-/g, ' ') + '…');

    try {
      var endpoint = String(config.restBase || '/wp-json/sc-lab/v1/runtime/v0254').replace(/\/$/, '') + '/module/' + encodeURIComponent(module);
      var headers = { Accept: 'application/json' };
      if (config.nonce) {
        headers['X-WP-Nonce'] = config.nonce;
      }

      var response = await fetch(endpoint, {
        method: 'GET',
        credentials: 'same-origin',
        headers: headers,
        signal: state.controller.signal,
        cache: 'no-store'
      });
      var data = await response.json();
      if (!response.ok || !data || !data.ok || !data.html) {
        throw new Error((data && data.message) || 'The server returned an incomplete module response.');
      }
      if (requestId !== state.requestId) {
        return;
      }
      if (Number(data.bytes || 0) > Number(config.panelBudget || 900000)) {
        throw new Error('The selected module exceeded the safe panel-size budget.');
      }

      panelHost.querySelectorAll('[data-module-panel]').forEach(function (node) {
        node.remove();
      });
      panelHost.insertAdjacentHTML('beforeend', data.html);
      panelHost.querySelectorAll('[data-module-panel]').forEach(function (node, index) {
        if (index > 0) {
          node.remove();
        }
      });

      state.activeModule = module;
      state.lastError = null;
      updateMeta(root, module);
      setBusy(root, false, 'Stable runtime active · one laboratory loaded at a time');

      if (!options.fromHistory) {
        writeLocation(module, Boolean(options.replaceHistory));
      }

      var mounted = currentPanel(root);
      announceLifecycle('sc:lab:module-mounted', {
        module: module,
        panel: mounted,
        bytes: Number(data.bytes || 0),
        nodeCount: Number(data.nodeCount || 0),
        version: '0.25.4'
      });

      window.requestAnimationFrame(function () {
        window.dispatchEvent(new Event('resize'));
        if (options.focus !== false && mounted) {
          var heading = mounted.querySelector('h1, h2, h3, [tabindex="-1"]');
          if (heading) {
            heading.setAttribute('tabindex', '-1');
            heading.focus({ preventScroll: true });
          }
        }
      });
    } catch (error) {
      if (error && error.name === 'AbortError') {
        return;
      }
      state.lastError = error instanceof Error ? error.message : String(error);
      panelHost.querySelectorAll('[data-module-panel]').forEach(function (node) {
        node.remove();
      });
      panelHost.insertAdjacentHTML('beforeend', errorPanel(module, state.lastError));
      setBusy(root, false, 'Module load failed · recovery controls available');
    }
  }

  function handleClick(event) {
    var root = shell();
    if (!root) {
      return;
    }

    var action = event.target.closest('[data-sc-lab-runtime-action]');
    if (action && root.contains(action)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      var value = action.getAttribute('data-sc-lab-runtime-action');
      if (value === 'overview') {
        loadModule('overview');
      } else if (value === 'reload') {
        loadModule(state.activeModule, { replaceHistory: true });
      } else if (value === 'safe') {
        try {
          sessionStorage.removeItem('scLabLastModuleV0254');
        } catch (ignore) {}
        loadModule('overview', { replaceHistory: true });
      }
      return;
    }

    var nav = event.target.closest('[data-lab-module]');
    if (nav && root.contains(nav)) {
      var module = nav.getAttribute('data-lab-module');
      if (validSlug(module)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        loadModule(module);
      }
    }
  }

  function auditInitialBudget(root) {
    var count = root.querySelectorAll('*').length;
    root.setAttribute('data-sc-lab-initial-node-count', String(count));
    if (count > Number(config.nodeBudget || 12000) && window.console) {
      console.warn('[Sustainable Catalyst Lab v0.25.4] Initial DOM budget exceeded:', count);
    }
  }

  function boot() {
    var root = shell();
    if (!root || root.getAttribute('data-sc-lab-runtime-booted') === '1') {
      return;
    }
    root.setAttribute('data-sc-lab-runtime-booted', '1');
    state.activeModule = root.getAttribute('data-sc-lab-active-module') || state.activeModule;
    updateMeta(root, state.activeModule);
    auditInitialBudget(root);

    document.addEventListener('click', handleClick, true);
    window.addEventListener('popstate', function () {
      var module = moduleFromLocation();
      if (module !== state.activeModule) {
        loadModule(module, { fromHistory: true, focus: false });
      }
    });

    announceLifecycle('sc:lab:runtime-ready', {
      version: '0.25.4',
      module: state.activeModule,
      mode: 'single-panel-lazy-runtime'
    });
  }

  window.SCLabRuntimeV0254API = {
    load: loadModule,
    status: function () {
      var root = shell();
      return {
        version: '0.25.4',
        mode: 'single-panel-lazy-runtime',
        activeModule: state.activeModule,
        busy: Boolean(root && root.getAttribute('aria-busy') === 'true'),
        requestId: state.requestId,
        lastError: state.lastError,
        duplicateGuard: true,
        mountedAt: state.mountedAt,
        panelCount: root ? root.querySelectorAll('[data-module-panel]').length : 0,
        nodeCount: root ? root.querySelectorAll('*').length : 0
      };
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
}());
