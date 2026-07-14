(function (W, D) {
  'use strict';
  if (W.__SCLabRuntimeV0263) return;
  W.__SCLabRuntimeV0263 = true;

  const config = W.SCLabRuntimeConfigV0263 || {};
  const errors = [];
  const events = [];
  let active = String(config.module || 'overview');

  function root() { return D.querySelector('[data-sc-lab-runtime="0.26.3"]'); }
  function labRoot() { return root()?.querySelector('.sc-lab-app') || D.querySelector('.sc-lab-app'); }
  function now() { return new Date().toISOString(); }
  function text(error) { return error instanceof Error ? `${error.name}: ${error.message}` : String(error || 'Unknown error'); }
  function recordError(scope, error, metadata) {
    const item = { at: now(), scope: String(scope || 'runtime'), message: text(error), stack: error?.stack || '', metadata: metadata || {} };
    errors.push(item);
    if (errors.length > 100) errors.shift();
    const app = labRoot();
    if (app) {
      app.dataset.scLabLastError = item.message;
      app.dataset.scLabRuntimeState = 'degraded';
    }
    try { console.error('[Sustainable Catalyst Lab v0.26.3]', item.scope, error, item.metadata); } catch (_) {}
    D.dispatchEvent(new CustomEvent('sc-lab:runtime-error', { detail: item }));
    return item;
  }
  function recordEvent(name, detail) {
    events.push({ at: now(), name, detail: detail || {} });
    if (events.length > 100) events.shift();
  }
  function heap() {
    const p = W.performance;
    return p?.memory ? { usedJSHeapSize: p.memory.usedJSHeapSize, totalJSHeapSize: p.memory.totalJSHeapSize, jsHeapSizeLimit: p.memory.jsHeapSizeLimit } : null;
  }
  function dependencies() {
    const Lab = W.SCLab || {};
    const names = ['util','Projects','Feeds','Calculators','PhysicsLab','BiologyLab','AstronomyLab','MaterialsLab','EarthLab','EnergyLab','ElectricalEmbedded','MechanicalThermalLab','Workspace'];
    return Object.fromEntries(names.map(name => [name, !!Lab[name]]));
  }
  function status() {
    const wrapper = root();
    const app = labRoot();
    return {
      version: '0.26.3',
      pluginVersion: config.pluginVersion || W.SCLabConfig?.version || null,
      mode: 'isolated-module-calculator-repair',
      activeModule: active,
      appReady: app?.dataset.scLabAppReady === '1',
      appFailed: app?.dataset.scLabAppFailed === '1',
      runtimeState: app?.dataset.scLabRuntimeState || 'starting',
      panelCount: wrapper?.querySelectorAll('[data-lab-module]').length || 0,
      nodeCount: wrapper?.querySelectorAll('*').length || 0,
      dependencies: dependencies(),
      errors: errors.slice(-20),
      events: events.slice(-20),
      heap: heap(),
      duplicateGuard: true,
      fullPageTeardownNavigation: true
    };
  }
  function destination(module) {
    const url = new URL(W.location.href);
    url.searchParams.set('sc_lab_module', module);
    url.searchParams.delete('sc_lab_safe');
    return url.toString();
  }
  function navigate(module) {
    module = /^[a-z0-9][a-z0-9-]{0,79}$/.test(String(module || '')) ? String(module) : 'overview';
    recordEvent('navigate', { from: active, to: module });
    D.dispatchEvent(new CustomEvent('sc-lab:module-unmounting', { detail: { module: active, nextModule: module, version: '0.26.3' } }));
    W.location.assign(destination(module));
  }
  function diagnostics() {
    const output = root()?.querySelector('[data-sc-lab-runtime-diagnostics]');
    if (!output) return;
    output.hidden = !output.hidden;
    output.textContent = JSON.stringify(status(), null, 2);
  }
  function click(event) {
    const wrapper = root();
    if (!wrapper) return;
    const action = event.target.closest('[data-sc-lab-runtime-action]');
    if (action && wrapper.contains(action)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      const value = action.dataset.scLabRuntimeAction;
      if (value === 'overview') navigate('overview');
      else if (value === 'reload') W.location.reload();
      else diagnostics();
      return;
    }
    const nav = event.target.closest('[data-lab-module-button],[data-open-module]');
    if (nav && wrapper.contains(nav)) {
      const module = nav.dataset.labModuleButton || nav.dataset.openModule;
      if (module && !wrapper.querySelector(`[data-lab-module="${CSS.escape(module)}"]`)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        navigate(module);
      }
    }
  }
  function fallbackMount() {
    const app = labRoot();
    if (!app || app.dataset.scLabAppReady === '1') return;
    const Lab = W.SCLab || {};
    const projects = app._scLabProjects || (typeof Lab.Projects === 'function' ? new Lab.Projects() : null);
    const map = {
      physics: ['PhysicsLab', '[data-physics-tool]'],
      biology: ['BiologyLab', '[data-biology-tool-grid]'],
      astronomy: ['AstronomyLab', '[data-astronomy-tool-grid]'],
      materials: ['MaterialsLab', '[data-materials-tool-grid]'],
      'earth-systems': ['EarthLab', '[data-earth-tool-grid]'],
      'energy-engineering': ['EnergyLab', '[data-energy-tool-grid]'],
      'electrical-embedded': ['ElectricalEmbedded', '[data-electrical-grid]'],
      'mechanical-thermal': ['MechanicalThermalLab', '[data-mechanical-thermal-root]'],
      'civil-infrastructure': ['CivilInfrastructureLab', '[data-civil-infrastructure-root]']
    };
    const entry = map[active];
    if (!entry || !projects) return;
    const [name, selector] = entry;
    const controller = Lab[name];
    const target = app.querySelector(selector);
    if (!target || !controller || typeof controller.init !== 'function') return;
    if (target.dataset.scLabV0263FallbackMounted === '1') return;
    try {
      controller.init(app, projects);
      target.dataset.scLabV0263FallbackMounted = '1';
      app.dataset.scLabRuntimeState = 'recovered';
      recordEvent('fallback-mount', { module: active, controller: name });
    } catch (error) {
      recordError(`fallback:${active}`, error, { controller: name });
    }
  }
  function boot() {
    const wrapper = root();
    const app = labRoot();
    if (!wrapper || wrapper.dataset.scLabRuntimeBooted === '1') return;
    wrapper.dataset.scLabRuntimeBooted = '1';
    active = wrapper.dataset.scLabActiveModule || app?.dataset.initialModule || active;
    if (app) {
      app.dataset.scLabRuntimeVersion = '0.26.3';
      app.dataset.scLabRuntimeState = 'starting';
    }
    D.addEventListener('click', click, true);
    W.addEventListener('error', event => {
      const source = String(event.filename || '');
      if (source.includes('sc-lab') || source === '') recordError('window-error', event.error || event.message, { source, line: event.lineno, column: event.colno });
    });
    W.addEventListener('unhandledrejection', event => recordError('unhandled-rejection', event.reason));
    D.addEventListener('sc-lab:app-ready', event => {
      if (app) app.dataset.scLabRuntimeState = 'ready';
      recordEvent('app-ready', event.detail);
    });
    D.addEventListener('sc-lab:app-error', event => {
      recordError('app-bootstrap', event.detail?.error || 'Application bootstrap failed', event.detail || {});
      W.setTimeout(fallbackMount, 0);
    });
    W.setTimeout(() => {
      if (app?.dataset.scLabAppReady !== '1') fallbackMount();
      const current = status();
      if (current.nodeCount > Number(config.warningBudget || 5000)) console.warn('[Sustainable Catalyst Lab v0.26.3] DOM warning budget exceeded', current);
      if (current.nodeCount > Number(config.nodeBudget || 6500)) wrapper.classList.add('sc-lab-over-budget-v0263');
    }, 50);
    recordEvent('runtime-boot', { module: active });
  }

  W.SCLabRuntimeV0263 = { status, recordError, recordEvent, navigate, diagnostics, fallbackMount };
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})(window, document);
