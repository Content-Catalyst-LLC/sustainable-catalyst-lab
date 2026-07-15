(function (W, D) {
  'use strict';
  if (W.__SCLabRuntimeV02631) return;
  W.__SCLabRuntimeV02631 = true;

  const config = W.SCLabRuntimeConfigV02631 || {};
  const defaultAliases = {
    marine: 'marine-biology', 'marine-science': 'marine-biology', 'ocean-biology': 'marine-biology',
    climate: 'climate-maps', 'climate-map': 'climate-maps',
    'astronomy-observations': 'space-telescopes', 'space-observations': 'space-telescopes', space: 'space-telescopes',
    evidence: 'evidence-decisions', decisions: 'evidence-decisions',
    earth: 'earth-systems', energy: 'energy-engineering', electrical: 'electrical-embedded',
    mechanical: 'mechanical-thermal', civil: 'civil-infrastructure', reports: 'report-studio',
    report: 'report-studio', visualization: 'visualization-studio', code: 'code-studio',
    workspace: 'workspace-data', sources: 'source-registry', datasets: 'dataset-inspector', status: 'system-status'
  };
  const aliases = Object.freeze({ ...defaultAliases, ...(config.aliases || {}) });
  const errors = [];
  const events = [];
  let active = resolveModule(config.module || 'overview');
  let warningObserver = null;

  function root() { return D.querySelector('[data-sc-lab-runtime="0.26.3.1"]'); }
  function labRoot() { return root()?.querySelector('.sc-lab-app') || D.querySelector('.sc-lab-app'); }
  function now() { return new Date().toISOString(); }
  function key(value) { return String(value || '').trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, ''); }
  function resolveModule(value) {
    let module = key(value) || 'overview';
    const seen = new Set();
    while (aliases[module] && !seen.has(module)) { seen.add(module); module = key(aliases[module]) || 'overview'; }
    return module;
  }
  function manifest() {
    const node = root()?.querySelector('[data-sc-lab-module-manifest]');
    try {
      const data = node ? JSON.parse(node.textContent || '{}') : {};
      return { modules: Array.isArray(data.modules) ? data.modules.map(key) : [], aliases: { ...aliases, ...(data.aliases || {}) } };
    } catch (error) {
      recordError('module-manifest', error);
      return { modules: [], aliases };
    }
  }
  function classifyModule(value) {
    const requested = key(value) || 'overview';
    const canonical = resolveModule(requested);
    const known = manifest().modules.includes(canonical);
    return { requested, canonical, known, resolution: requested !== canonical && known ? 'alias' : known ? 'canonical' : 'missing' };
  }
  function text(error) { return error instanceof Error ? `${error.name}: ${error.message}` : String(error || 'Unknown error'); }
  function recordError(scope, error, metadata) {
    const item = { at: now(), scope: String(scope || 'runtime'), message: text(error), stack: error?.stack || '', metadata: metadata || {} };
    errors.push(item);
    if (errors.length > 100) errors.shift();
    const app = labRoot();
    if (app) { app.dataset.scLabLastError = item.message; app.dataset.scLabRuntimeState = 'degraded'; }
    try { console.error('[Sustainable Catalyst Lab v0.26.3.1]', item.scope, error, item.metadata); } catch (_) {}
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
    const names = ['util','Projects','Feeds','Calculators','PhysicsLab','BiologyLab','AstronomyLab','MaterialsLab','EarthLab','EnergyLab','ElectricalEmbedded','MechanicalThermalLab','MicrobiologyLaboratory','ObserveDomainV02633','Workspace'];
    return Object.fromEntries(names.map(name => [name, !!Lab[name]]));
  }
  function status() {
    const wrapper = root();
    const app = labRoot();
    const requested = wrapper?.dataset.scLabRequestedModule || config.requestedModule || active;
    return {
      version: '0.26.3.1', pluginVersion: config.pluginVersion || W.SCLabConfig?.version || null,
      mode: 'canonical-panel-alias-routing', activeModule: active, requestedModule: requested,
      moduleResolution: classifyModule(requested), appReady: app?.dataset.scLabAppReady === '1',
      appFailed: app?.dataset.scLabAppFailed === '1', runtimeState: app?.dataset.scLabRuntimeState || 'starting',
      panelCount: wrapper?.querySelectorAll('[data-lab-module]').length || 0,
      knownPanelCount: manifest().modules.length, aliases, nodeCount: wrapper?.querySelectorAll('*').length || 0,
      dependencies: dependencies(), errors: errors.slice(-20), events: events.slice(-20), heap: heap(),
      duplicateGuard: true, fullPageTeardownNavigation: true, falseAliasWarningSuppression: true
    };
  }
  function destination(module) {
    const canonical = resolveModule(module);
    const url = new URL(W.location.href);
    url.searchParams.set('sc_lab_module', canonical);
    url.searchParams.delete('sc_lab_safe');
    return url.toString();
  }
  function navigate(module) {
    const resolution = classifyModule(module);
    const next = resolution.known ? resolution.canonical : 'overview';
    recordEvent('navigate', { from: active, to: next, requested: resolution.requested, resolution: resolution.resolution });
    D.dispatchEvent(new CustomEvent('sc-lab:module-unmounting', { detail: { module: active, nextModule: next, requestedModule: resolution.requested, version: '0.26.3.1' } }));
    W.location.assign(destination(next));
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
      event.preventDefault(); event.stopImmediatePropagation();
      const value = action.dataset.scLabRuntimeAction;
      if (value === 'overview') navigate('overview'); else if (value === 'reload') W.location.reload(); else diagnostics();
      return;
    }
    const nav = event.target.closest('[data-lab-module-button],[data-open-module]');
    if (nav && wrapper.contains(nav)) {
      const requested = nav.dataset.labModuleButton || nav.dataset.openModule;
      const canonical = resolveModule(requested);
      if (requested) {
        nav.dataset.scLabCanonicalModule = canonical;
        if (!wrapper.querySelector(`[data-lab-module="${CSS.escape(canonical)}"]`)) {
          event.preventDefault(); event.stopImmediatePropagation(); navigate(canonical);
        }
      }
    }
  }
  function isFalseAliasWarning(element) {
    if (!element || element.nodeType !== 1) return null;
    const content = String(element.textContent || '').replace(/\s+/g, ' ').trim();
    if (!content || content.length > 700 || !/Laboratory compatibility warning/i.test(content) || !/was not present in the rendered markup/i.test(content)) return null;
    const match = content.match(/[“"']([a-z0-9-]+)[”"']/i);
    if (!match) return null;
    const result = classifyModule(match[1]);
    return result.resolution === 'alias' && result.known ? result : null;
  }
  function suppressFalseAliasWarnings(scope) {
    const wrapper = root();
    if (!wrapper) return 0;
    const candidates = scope?.nodeType === 1 ? [scope, ...scope.querySelectorAll?.('aside,section,article,div,p') || []] : [...wrapper.querySelectorAll('aside,section,article,div,p')];
    let count = 0;
    candidates.forEach(element => {
      const result = isFalseAliasWarning(element);
      if (!result || element.dataset.scLabAliasWarningSuppressed === '1') return;
      element.dataset.scLabAliasWarningSuppressed = '1';
      element.hidden = true;
      element.setAttribute('aria-hidden', 'true');
      recordEvent('false-alias-warning-suppressed', result);
      count += 1;
    });
    return count;
  }
  function fallbackMount() {
    const app = labRoot();
    if (!app) return;
    const Lab = W.SCLab || {};
    const projects = app._scLabProjects || (typeof Lab.Projects === 'function' ? new Lab.Projects() : null);
    const map = {
      physics: ['PhysicsLab', '[data-physics-tool]'], biology: ['BiologyLab', '[data-biology-tool-grid]'],
      astronomy: ['AstronomyLab', '[data-astronomy-tool-grid]'], materials: ['MaterialsLab', '[data-materials-tool-grid]'],
      'earth-systems': ['EarthLab', '[data-earth-tool-grid]'], 'energy-engineering': ['EnergyLab', '[data-energy-tool-grid]'],
      'electrical-embedded': ['ElectricalEmbedded', '[data-electrical-grid]'], 'mechanical-thermal': ['MechanicalThermalLab', '[data-mechanical-thermal-root]'],
      'civil-infrastructure': ['CivilInfrastructureLab', '[data-civil-infrastructure-root]'],
      'microbiology-laboratory': ['MicrobiologyLaboratory', '[data-microbiology-laboratory-root]']
    };
    const entry = map[active];
    if (!entry || !projects) return;
    const [name, selector] = entry;
    const controller = Lab[name];
    const target = app.querySelector(selector);
    if (!target || !controller || typeof controller.init !== 'function' || target.dataset.scLabV02631FallbackMounted === '1') return;
    if (target.dataset.scLabControllerReady === '1' || target.dataset.scMicrobiologyInitialized) return;
    try {
      controller.init(app, projects);
      target.dataset.scLabV02631FallbackMounted = '1';
      app.dataset.scLabRuntimeState = 'recovered';
      recordEvent('fallback-mount', { module: active, controller: name });
    } catch (error) { recordError(`fallback:${active}`, error, { controller: name }); }
  }
  function canonicalizeMarkup() {
    const wrapper = root();
    if (!wrapper) return;
    wrapper.querySelectorAll('[data-lab-module-button],[data-open-module]').forEach(element => {
      const requested = element.dataset.labModuleButton || element.dataset.openModule;
      if (!requested) return;
      const canonical = resolveModule(requested);
      element.dataset.scLabCanonicalModule = canonical;
      if (element.dataset.labModuleButton) element.dataset.labModuleButton = canonical;
      if (element.dataset.openModule) element.dataset.openModule = canonical;
    });
  }
  function boot() {
    const wrapper = root();
    const app = labRoot();
    if (!wrapper || wrapper.dataset.scLabRuntimeBooted === '1') return;
    wrapper.dataset.scLabRuntimeBooted = '1';
    active = resolveModule(wrapper.dataset.scLabActiveModule || app?.dataset.initialModule || active);
    if (app) { app.dataset.scLabRuntimeVersion = '0.26.3.1'; app.dataset.scLabRuntimeState = 'starting'; }
    canonicalizeMarkup();
    suppressFalseAliasWarnings(wrapper);
    warningObserver = new MutationObserver(records => records.forEach(record => record.addedNodes.forEach(node => { if (node.nodeType === 1) suppressFalseAliasWarnings(node); })));
    warningObserver.observe(wrapper, { childList: true, subtree: true });
    W.setTimeout(() => { warningObserver?.disconnect(); warningObserver = null; }, 10000);
    D.addEventListener('click', click, true);
    W.addEventListener('error', event => {
      const source = String(event.filename || '');
      if (source.includes('sc-lab') || source === '') recordError('window-error', event.error || event.message, { source, line: event.lineno, column: event.colno });
    });
    W.addEventListener('unhandledrejection', event => recordError('unhandled-rejection', event.reason));
    D.addEventListener('sc-lab:app-ready', event => { if (app) app.dataset.scLabRuntimeState = 'ready'; recordEvent('app-ready', event.detail); });
    D.addEventListener('sc-lab:app-error', event => { recordError('app-bootstrap', event.detail?.error || 'Application bootstrap failed', event.detail || {}); W.setTimeout(fallbackMount, 0); });
    W.setTimeout(() => {
      fallbackMount();
      const current = status();
      if (current.nodeCount > Number(config.warningBudget || 5000)) console.warn('[Sustainable Catalyst Lab v0.26.3.1] DOM warning budget exceeded', current);
      if (current.nodeCount > Number(config.nodeBudget || 6500)) wrapper.classList.add('sc-lab-over-budget-v02631');
    }, 50);
    recordEvent('runtime-boot', { module: active, requested: config.requestedModule || active, resolution: classifyModule(config.requestedModule || active) });
  }

  W.SCLabRuntimeV02631 = { status, recordError, recordEvent, resolveModule, classifyModule, navigate, diagnostics, fallbackMount, suppressFalseAliasWarnings };
  W.SCLabResolveModuleV02631 = resolveModule;
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot, { once: true }); else boot();
})(window, document);
