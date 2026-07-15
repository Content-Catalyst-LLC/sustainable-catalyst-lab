(function (W, D) {
  'use strict';
  if (W.__SCLabFunctionalValidationV0264) return;
  W.__SCLabFunctionalValidationV0264 = true;

  const VERSION = '0.26.4';
  const config = W.SCLabFunctionalValidationConfigV0264 || {};
  const errors = W.__SCLabFunctionalErrorsV0264 || [];
  W.__SCLabFunctionalErrorsV0264 = errors;
  let lastResult = null;

  function now() { return new Date().toISOString(); }
  function text(value) { return String(value == null ? '' : value).replace(/\s+/g, ' ').trim(); }
  function recordError(kind, error, metadata) {
    const item = { at: now(), kind, message: text(error?.message || error), metadata: metadata || {} };
    errors.push(item); if (errors.length > 100) errors.shift(); return item;
  }
  W.addEventListener('error', event => {
    const source = String(event.filename || '');
    if (!source || /sc-lab|sustainable-catalyst-lab/i.test(source)) recordError('window-error', event.error || event.message, { source, line: event.lineno, column: event.colno });
  });
  W.addEventListener('unhandledrejection', event => recordError('unhandled-rejection', event.reason));

  function getPath(path) {
    return String(path || '').split('.').filter(Boolean).reduce((value, key) => value == null ? null : value[key], W);
  }
  function activeModule() {
    const wrapper = D.querySelector('[data-sc-lab-active-module]');
    const app = D.querySelector('.sc-lab-app');
    return wrapper?.dataset.scLabActiveModule || app?.dataset.initialModule || config.requestedModule || 'overview';
  }
  function registry() { return Array.isArray(config.registry) ? config.registry : []; }
  function specFor(module) { return registry().find(item => item.module === module) || null; }
  function signature(element) {
    if (!element) return '';
    if (element instanceof HTMLImageElement) return `${element.currentSrc || element.src}|${element.complete}|${element.naturalWidth}`;
    return `${text(element.textContent)}|${element.innerHTML.length}|${element.childElementCount}`;
  }
  function wait(ms) { return new Promise(resolve => W.setTimeout(resolve, ms)); }
  async function waitFor(test, timeoutMs, interval) {
    const started = Date.now(); let last = null;
    while (Date.now() - started < timeoutMs) {
      try { last = test(); if (last) return last; } catch (_) {}
      await wait(interval || 100);
    }
    return last;
  }
  function classifyDiagnostic(value) {
    const s = text(value).toLowerCase();
    if (/disabled|backend required|not configured/.test(s)) return 'backend_required';
    if (/source unavailable|unavailable|failed to fetch|network|timed out|timeout|http [45]/.test(s)) return 'external_source_unavailable';
    if (/error:|invalid input|calculation failed|analysis error/.test(s)) return 'calculation_failed';
    return null;
  }
  function controllerState(spec) {
    if (!spec.controllerPaths?.length) return { required: false, ready: true, found: null };
    for (const path of spec.controllerPaths) { if (getPath(path)) return { required: true, ready: true, found: path }; }
    return { required: true, ready: false, found: null };
  }
  function panelRoot(spec) { return D.querySelector(spec.panelSelector) || D.querySelector(`[data-module-panel="${CSS.escape(spec.module)}"]`); }

  async function inspect(module, options) {
    const spec = specFor(module); const startedAt = now(); const started = performance.now(); const errorStart = errors.length;
    if (!spec) return { module, status: 'unknown_module', startedAt, finishedAt: now(), errors: errors.slice(errorStart) };
    const panel = await waitFor(() => panelRoot(spec), Math.min(6000, Number(spec.timeoutMs || 8000)), 80);
    if (!panel) return finish(spec, startedAt, started, { panel: false, controller: false, action: false, result: false, status: 'panel_missing', message: 'The requested panel was not rendered.' }, errorStart);

    const controller = await waitFor(() => {
      const state = controllerState(spec); return state.ready ? state : null;
    }, spec.controllerPaths?.length ? 5000 : 50, 80) || controllerState(spec);
    if (!controller.ready) return finish(spec, startedAt, started, { panel: true, controller: false, action: false, result: false, status: 'controller_missing', message: `Expected controller not found: ${(spec.controllerPaths || []).join(' or ')}` }, errorStart);

    if (spec.actionMode === 'structural' || !spec.actionSelector) {
      const meaningful = text(panel.textContent).length > 24 || panel.querySelectorAll('*').length > 3;
      return finish(spec, startedAt, started, { panel: true, controller: true, action: null, result: meaningful, status: meaningful ? 'functional' : 'empty_panel', message: meaningful ? 'Panel rendered with meaningful content.' : 'Panel rendered without meaningful content.' }, errorStart);
    }

    const action = await waitFor(() => panel.querySelector(spec.actionSelector), 6000, 80);
    if (!action) return finish(spec, startedAt, started, { panel: true, controller: true, action: false, result: false, status: 'action_missing', message: `Primary action not found: ${spec.actionSelector}` }, errorStart);
    const output = spec.outputSelector ? await waitFor(() => panel.querySelector(spec.outputSelector), 3000, 80) : null;
    if (spec.outputSelector && !output) return finish(spec, startedAt, started, { panel: true, controller: true, action: true, result: false, status: 'output_missing', message: `Expected result target not found: ${spec.outputSelector}` }, errorStart);

    const before = signature(output);
    try { action.click(); } catch (error) { recordError('action-click', error, { module, selector: spec.actionSelector }); }
    let changed = false;
    if (spec.actionMode === 'feed') {
      changed = await waitFor(() => {
        const api = W.SCLabObserveFeedsV02634?.status?.();
        const outputText = signature(output);
        return (api && api.ready && !api.loading && api.mode) ? { api, outputText } : (outputText !== before && outputText.length > 5 ? { api: null, outputText } : null);
      }, Number(spec.timeoutMs || 24000), 150);
    } else if (spec.actionMode === 'image-src') {
      changed = await waitFor(() => {
        const sig = signature(output); return sig && sig !== before && !/\|false\|0$/.test(sig) ? sig : null;
      }, Number(spec.timeoutMs || 16000), 150);
    } else {
      changed = await waitFor(() => {
        const sig = signature(output); return sig !== before && text(output?.textContent || output?.innerHTML).length > 1 ? sig : null;
      }, Number(spec.timeoutMs || 10000), 100);
    }

    const current = signature(output); const diagnostic = classifyDiagnostic(`${current} ${W.SCLabObserveFeedsV02634?.status?.().mode || ''}`);
    if (diagnostic === 'backend_required') return finish(spec, startedAt, started, { panel: true, controller: true, action: true, result: false, status: 'backend_required', message: 'The interface is active but requires a configured backend or enabled feature.' }, errorStart);
    if (diagnostic === 'external_source_unavailable') return finish(spec, startedAt, started, { panel: true, controller: true, action: true, result: false, status: 'external_source_unavailable', message: 'The controller and action worked, but the external scientific source was unavailable.' }, errorStart);
    if (diagnostic === 'calculation_failed') return finish(spec, startedAt, started, { panel: true, controller: true, action: true, result: false, status: 'calculation_failed', message: text(output?.textContent || output?.innerHTML).slice(0, 500) }, errorStart);
    return finish(spec, startedAt, started, { panel: true, controller: true, action: true, result: !!changed, status: changed ? 'functional' : 'result_not_observed', message: changed ? 'Primary action produced a result.' : 'The primary action ran, but no result change was observed before timeout.' }, errorStart);
  }

  function finish(spec, startedAt, started, values, errorStart) {
    const runtimeErrors = errors.slice(errorStart);
    let status = values.status;
    if (status === 'functional' && runtimeErrors.length) status = 'functional_with_errors';
    const result = Object.assign({
      schema: 'sc-lab-functional-result/1.0', version: VERSION, release: config.release || W.SCLabConfig?.version || null,
      module: spec.module, label: spec.label, group: spec.group, priority: !!spec.priority, startedAt, finishedAt: now(), durationMs: Math.round(performance.now() - started),
      controllerPath: controllerState(spec).found, errors: runtimeErrors, url: W.location.href
    }, values, { status });
    lastResult = result;
    D.documentElement.dataset.scLabFunctionalStatus = result.status;
    D.dispatchEvent(new CustomEvent('sc-lab:functional-result', { detail: result }));
    try { if (W.parent && W.parent !== W) W.parent.postMessage({ type: 'sc-lab-functional-result-v0264', result }, W.location.origin); } catch (_) {}
    return result;
  }

  async function runCurrent() { return inspect(activeModule(), { auto: true }); }
  function status() { return { version: VERSION, release: config.release || null, activeModule: activeModule(), registryCount: registry().length, errors: errors.slice(-20), lastResult }; }
  W.SCLabFunctionalValidationV0264 = { VERSION, registry, inspect, runCurrent, status, recordError };
  if (config.autoRun) {
    const boot = () => W.setTimeout(() => runCurrent().catch(error => recordError('runner', error)), 250);
    if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot, { once: true }); else boot();
  }
})(window, document);
