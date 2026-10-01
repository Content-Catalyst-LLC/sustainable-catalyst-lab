(function (w, d) {
  'use strict';

  const VERSION = '0.163.1.3';
  const CFG = () => w.SCLabFrontDoorPolishV016313 || {};
  const STORAGE_KEY = 'sc-lab-v016313-frontdoor-panel-state';

  const PANELS = [
    { id: 'uncertainty', selector: '.sc-lab-v015210-analysis', head: '.sc-lab-v015210-analysis-head', label: 'Uncertainty & sensitivity' },
    { id: 'linked', selector: '.sc-lab-v015211-linked', head: '.sc-lab-v015211-head', label: 'Linked views & selection' },
    { id: 'scene', selector: '.sc-lab-v015212-persistence', head: '.sc-lab-v015212-head', label: 'Scene, provenance & handoff' },
    { id: 'project', selector: '.sc-lab-v01530-workspace', head: '.sc-lab-v01530-head', label: 'Project 4D workspace' }
  ];

  function readState() {
    try {
      const value = JSON.parse(w.sessionStorage.getItem(STORAGE_KEY) || '{}');
      return value && typeof value === 'object' ? value : {};
    } catch (_) { return {}; }
  }

  function writeState(state) {
    try { w.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (_) {}
  }

  function defaultCollapsed(id) {
    const configured = Array.isArray(CFG().collapsedByDefault) ? CFG().collapsedByDefault : ['uncertainty', 'linked', 'scene', 'project'];
    return configured.includes(id);
  }

  function commonAncestor(nodes, boundary) {
    if (!nodes.length) return null;
    let node = nodes[0].parentElement;
    while (node && node !== boundary && node !== d.body) {
      if (nodes.every(item => node.contains(item))) return node;
      node = node.parentElement;
    }
    return null;
  }

  function setCollapsed(panel, id, collapsed, state) {
    panel.classList.toggle('is-v016313-collapsed', collapsed);
    panel.dataset.v016313Collapsed = collapsed ? '1' : '0';
    const button = panel.querySelector('[data-v016313-panel-toggle]');
    if (button) {
      button.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      button.querySelector('[data-v016313-toggle-label]').textContent = collapsed ? 'Show' : 'Hide';
      button.querySelector('[data-v016313-toggle-icon]').textContent = collapsed ? '+' : '−';
    }
    state[id] = collapsed;
    writeState(state);
  }

  function decoratePanel(root, def, state) {
    const panel = root.querySelector(def.selector) || d.querySelector(def.selector);
    if (!panel || panel.dataset.v016313PanelBound === '1') return false;
    const head = panel.querySelector(def.head);
    if (!head) return false;

    panel.dataset.v016313Panel = def.id;
    panel.dataset.v016313PanelBound = '1';
    panel.classList.add('sc-lab-v016313-advanced-panel');
    head.dataset.v016313PanelHead = def.id;
    head.classList.add('sc-lab-v016313-panel-head');

    const tools = d.createElement('div');
    tools.className = 'sc-lab-v016313-panel-tools';
    tools.innerHTML = '<button type="button" class="sc-lab-v016313-panel-toggle" data-v016313-panel-toggle aria-label="Toggle ' + def.label + '"><span data-v016313-toggle-label>Show</span><span aria-hidden="true" data-v016313-toggle-icon>+</span></button>';
    head.appendChild(tools);

    const collapsed = Object.prototype.hasOwnProperty.call(state, def.id) ? !!state[def.id] : defaultCollapsed(def.id);
    setCollapsed(panel, def.id, collapsed, state);

    tools.querySelector('button').addEventListener('click', function () {
      const next = !panel.classList.contains('is-v016313-collapsed');
      setCollapsed(panel, def.id, next, state);
      try { w.dispatchEvent(new Event('resize')); } catch (_) {}
    });
    return true;
  }

  function markPrimarySurface(root) {
    const explorer = root.querySelector('.sc-lab-v015209-explorer');
    if (explorer) explorer.classList.add('sc-lab-v016313-primary-panel');

    const canvasWrap = root.querySelector('.sc-lab-v0710-canvas-wrap');
    if (canvasWrap) canvasWrap.classList.add('sc-lab-v016313-canvas-wrap');

    const metrics = Array.from(root.querySelectorAll('[data-v0710-metric]'));
    const metricsRoot = commonAncestor(metrics, root);
    if (metricsRoot) metricsRoot.classList.add('sc-lab-v016313-metrics-strip');

    const boundary = root.querySelector('[data-v015207-boundary]');
    if (boundary) boundary.classList.add('sc-lab-v016313-method-note');
  }

  function compactFrontDoor(root) {
    if (!root || root.dataset.v016313Polished === '1') return false;
    root.dataset.v016313Polished = '1';
    root.classList.add('sc-lab-v016313-frontdoor');
    markPrimarySurface(root);
    const state = readState();
    PANELS.forEach(def => decoratePanel(root, def, state));
    return true;
  }

  function boot() {
    Array.from(d.querySelectorAll('[data-v0710-visualizer]')).forEach(compactFrontDoor);
  }

  let scheduled = false;
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    w.requestAnimationFrame(function () { scheduled = false; boot(); });
  }

  const observer = new MutationObserver(schedule);
  observer.observe(d.documentElement, { childList: true, subtree: true });
  d.addEventListener('sc-lab:safe-module-opened', schedule);
  d.addEventListener('sc-lab:front-door-retained', schedule);
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', schedule, { once: true });
  else schedule();

  w.SCLabFrontDoorPolishV016313Runtime = Object.freeze({
    version: VERSION,
    boot: schedule,
    panels: PANELS.map(panel => ({ id: panel.id, label: panel.label }))
  });
})(window, document);
