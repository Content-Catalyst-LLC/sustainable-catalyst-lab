(function (w, d) {
  'use strict';

  const VERSION = '0.163.1.2';
  const FEATURE_VERSION = '0.163.1';
  const CFG = () => w.SCLabUnifiedWorkspaceShellV016312 || {};
  const STORAGE_KEY = 'sc-lab-v016312-active-workspace';
  const RAIL_KEY = 'sc-lab-v016312-rail-collapsed';
  let signalRefreshRequested = false;

  // v0.163.1.2 intentionally excludes [data-v0710-visualizer]. The 4D
  // visualization is a persistent front-door experience, not a specialist
  // module to be moved into or hidden by the progressive shell.
  const MODULES = [
    { id: 'notebook', code: 'NB', label: 'Notebook & Protocol', group: 'Research', selectors: ['[data-v01540-workspace]', '.sc-lab-v01540-workspace'], description: 'Reproducible protocols, notebooks, compute references and manifests.' },
    { id: 'batch', code: 'BX', label: 'Batch Experiments', group: 'Research', selectors: ['[data-v01550-workspace]', '.sc-lab-v01550-workspace'], description: 'Sweeps, ensembles, deterministic trials and explicit execution handoffs.' },
    { id: 'compute', code: 'HP', label: 'Compute & HPC', group: 'Compute', selectors: ['[data-v01560-workspace]', '.sc-lab-v01560-workspace'], description: 'Distributed, accelerated and scheduler-neutral execution planning.' },
    { id: 'cross-study', code: 'XS', label: 'Cross-Study', group: 'Evidence', selectors: ['[data-v01570-workspace]', '.sc-lab-v01570'], description: 'Cross-study replication and descriptive meta-experiment synthesis.' },
    { id: 'replication', code: 'RN', label: 'Replication Network', group: 'Evidence', selectors: ['[data-v01580-workspace]', '.sc-lab-v01580'], description: 'Independent replication nodes, plans, receipts and human review.' },
    { id: 'review', code: 'RV', label: 'Scientific Review', group: 'Evidence', selectors: ['[data-v01590-workspace]', '.sc-lab-v01590'], description: 'Validation dossiers, findings, sign-off, dissent and publication handoff.' },
    { id: 'research-os', code: 'OS', label: 'Research OS', group: 'Operations', selectors: ['[data-v01600-workspace]', '.sc-lab-v01600'], description: 'Human-controlled research lifecycle, packages and project command center.' },
    { id: 'programs', code: 'PG', label: 'Programs', group: 'Operations', selectors: ['[data-v01610-workspace]', '.sc-lab-v01610'], description: 'Research programs, portfolios, objectives and milestones.' },
    { id: 'resources', code: 'RS', label: 'Resources', group: 'Operations', selectors: ['[data-v01620-workspace]', '.sc-lab-v01620'], description: 'Cross-project dependencies, shared resources and planning scenarios.' },
    { id: 'governance', code: 'GV', label: 'Governance', group: 'Operations', selectors: ['[data-v01630-workspace]', '.sc-lab-v01630'], description: 'Institutional review bodies, federation, decisions and sign-off evidence.' }
  ];

  const q = (root, sel) => root && root.querySelector ? root.querySelector(sel) : null;
  const qa = (root, sel) => root && root.querySelectorAll ? Array.from(root.querySelectorAll(sel)) : [];
  const moduleById = id => MODULES.find(m => m.id === id) || null;

  function shell() {
    return d.querySelector('[data-sc-lab-unified-shell-v016312]') || d.querySelector('[data-sc-lab-unified-shell]');
  }

  function restoreFrontDoorVisualization() {
    const visualizer = d.querySelector('[data-v0710-visualizer]');
    if (!visualizer) return false;
    visualizer.hidden = false;
    visualizer.removeAttribute('aria-hidden');
    visualizer.removeAttribute('data-sc-lab-shell-module');
    visualizer.classList.remove('sc-lab-v016311-managed', 'sc-lab-v016312-managed', 'is-active');
    visualizer.style.removeProperty('display');
    visualizer.style.removeProperty('visibility');
    visualizer.style.removeProperty('opacity');
    visualizer.setAttribute('data-sc-lab-frontdoor-four-d', 'persistent');
    return true;
  }

  function signalContainer() { return d.querySelector('[data-overview-signals]'); }

  function ensureScientificSignalsVisible() {
    const target = signalContainer();
    if (!target) return false;
    target.hidden = false;
    target.removeAttribute('aria-hidden');
    target.style.removeProperty('display');
    target.style.removeProperty('visibility');
    target.style.removeProperty('opacity');
    target.setAttribute('data-sc-lab-signals-retained', '1');

    let node = target.parentElement;
    let depth = 0;
    while (node && depth < 6 && !node.classList.contains('sc-lab-app')) {
      if (node.tagName === 'DETAILS') node.open = true;
      node.hidden = false;
      if (node.getAttribute('aria-hidden') === 'true') node.setAttribute('aria-hidden', 'false');
      if (node.getAttribute('data-collapsed') === 'true') node.setAttribute('data-collapsed', 'false');
      node.classList.add('sc-lab-v016312-signals-visible');
      node.style.removeProperty('display');
      node.style.removeProperty('max-height');
      node.style.removeProperty('visibility');
      node.style.removeProperty('opacity');
      node = node.parentElement;
      depth += 1;
    }

    const refresh = d.querySelector('[data-overview-refresh]');
    if (refresh) {
      refresh.hidden = false;
      refresh.removeAttribute('aria-hidden');
      refresh.style.removeProperty('display');
      if (!signalRefreshRequested && CFG().scientificSignalsAutoRefresh !== false) {
        signalRefreshRequested = true;
        setTimeout(() => {
          try { refresh.click(); } catch (_) {}
        }, 250);
      }
    }
    return true;
  }

  function resolveModule(m) {
    for (const selector of m.selectors) {
      const node = d.querySelector(selector);
      if (node) return node;
    }
    return null;
  }

  function captureBoundary(node) {
    if (!node || node.hasAttribute('data-sc-lab-shell-boundary-captured-v016312')) return;
    const candidates = qa(node, '.boundary, [class*="-boundary"]');
    const text = candidates.map(x => (x.textContent || '').trim()).filter(Boolean).join(' ');
    candidates.forEach(x => { x.hidden = true; x.setAttribute('data-sc-lab-shell-boundary-hidden', ''); });
    if (text) node.setAttribute('data-sc-lab-shell-boundary', text);
    node.setAttribute('data-sc-lab-shell-boundary-captured-v016312', '1');
  }

  function registerModules(root) {
    const stage = q(root, '[data-sc-lab-shell-stage]');
    if (!stage) return 0;
    let available = 0;
    MODULES.forEach(m => {
      const node = resolveModule(m);
      qa(root, `[data-sc-lab-shell-open="${m.id}"]`).forEach(btn => { btn.disabled = !node; });
      if (!node || node === root || node.contains(root)) return;
      available += 1;
      node.setAttribute('data-sc-lab-shell-module', m.id);
      node.classList.add('sc-lab-v016312-managed');
      captureBoundary(node);
      if (node.parentNode !== stage) stage.appendChild(node);
    });
    root.setAttribute('data-sc-lab-shell-bound', '1');
    d.documentElement.classList.add('sc-lab-v016312-bound');
    return available;
  }

  function activeBoundary(root, id) {
    const copy = q(root, '[data-sc-lab-shell-governance-copy]');
    if (!copy) return;
    if (id === 'overview') {
      copy.textContent = 'Module-specific scientific boundaries appear here when a specialist workspace is open. The 4D front door and Scientific signals remain overview surfaces.';
      return;
    }
    const node = q(root, `[data-sc-lab-shell-module="${id}"]`);
    const text = node ? node.getAttribute('data-sc-lab-shell-boundary') : '';
    copy.textContent = text || 'This workspace retains its existing scientific, provenance, authorization and execution boundaries.';
  }

  function activate(root, id, options) {
    const opts = options || {};
    const overview = q(root, '[data-sc-lab-shell-overview]');
    const modules = qa(root, '[data-sc-lab-shell-module]');
    let exists = id === 'overview';
    modules.forEach(node => {
      const active = node.getAttribute('data-sc-lab-shell-module') === id;
      node.hidden = !active;
      node.classList.toggle('is-active', active);
      node.setAttribute('aria-hidden', active ? 'false' : 'true');
      if (active) exists = true;
    });
    if (!exists) id = 'overview';
    if (overview) overview.hidden = id !== 'overview';
    qa(root, '[data-sc-lab-shell-open]').forEach(btn => btn.setAttribute('aria-selected', btn.getAttribute('data-sc-lab-shell-open') === id ? 'true' : 'false'));
    root.setAttribute('data-active-workspace', id);
    const m = moduleById(id);
    const status = q(root, '[data-sc-lab-shell-status]');
    if (status) status.textContent = `${m ? m.label : 'Overview'} · ${modules.length} specialist workspaces available`;
    activeBoundary(root, id);
    try { w.sessionStorage.setItem(STORAGE_KEY, id); } catch (_) {}
    try { d.dispatchEvent(new CustomEvent('sc-lab:workspace-shell-change', { detail: { workspace: id, version: VERSION, featureVersion: FEATURE_VERSION } })); } catch (_) {}
    if (opts.focus) {
      const target = id === 'overview' ? overview : q(root, `[data-sc-lab-shell-module="${id}"]`);
      if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function filterNav(root, value) {
    const term = String(value || '').trim().toLowerCase();
    qa(root, '.sc-lab-v016312-nav-button[data-search]').forEach(btn => {
      btn.hidden = !!term && !String(btn.getAttribute('data-search') || '').includes(term);
    });
    qa(root, '.sc-lab-v016312-nav-group').forEach(group => {
      group.hidden = !qa(group, '.sc-lab-v016312-nav-button').some(btn => !btn.hidden);
    });
  }

  function bindShell(root) {
    if (!root || root.getAttribute('data-bound-v016312') === '1') return;
    root.setAttribute('data-bound-v016312', '1');
    root.addEventListener('click', ev => {
      const front = ev.target.closest('[data-sc-lab-frontdoor-scroll]');
      if (front) {
        const visualizer = d.querySelector('[data-v0710-visualizer]');
        if (visualizer && visualizer.scrollIntoView) visualizer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
      const opener = ev.target.closest('[data-sc-lab-shell-open]');
      if (opener && !opener.disabled) {
        activate(root, opener.getAttribute('data-sc-lab-shell-open'), { focus: opener.closest('.sc-lab-v016312-overview-grid') !== null });
        return;
      }
      const collapse = ev.target.closest('[data-sc-lab-shell-collapse]');
      if (collapse) {
        const collapsed = !root.classList.contains('is-rail-collapsed');
        root.classList.toggle('is-rail-collapsed', collapsed);
        collapse.textContent = collapsed ? '⇥' : '⇤';
        collapse.setAttribute('aria-label', collapsed ? 'Expand workspace rail' : 'Collapse workspace rail');
        try { w.sessionStorage.setItem(RAIL_KEY, collapsed ? '1' : '0'); } catch (_) {}
      }
    });
    const search = q(root, '[data-sc-lab-shell-search]');
    if (search) {
      search.addEventListener('input', () => filterNav(root, search.value));
      search.addEventListener('keydown', ev => {
        if (ev.key === 'Escape') { search.value = ''; filterNav(root, ''); search.blur(); }
      });
    }
    try {
      if (w.sessionStorage.getItem(RAIL_KEY) === '1') {
        root.classList.add('is-rail-collapsed');
        const collapse = q(root, '[data-sc-lab-shell-collapse]');
        if (collapse) collapse.textContent = '⇥';
      }
    } catch (_) {}
  }

  function boot() {
    restoreFrontDoorVisualization();
    ensureScientificSignalsVisible();
    const root = shell();
    if (!root) return;
    bindShell(root);
    const count = registerModules(root);
    let selected = CFG().defaultWorkspace || 'overview';
    try { selected = w.sessionStorage.getItem(STORAGE_KEY) || selected; } catch (_) {}
    if (selected !== 'overview' && !q(root, `[data-sc-lab-shell-module="${selected}"]`)) selected = 'overview';
    activate(root, selected);
    const status = q(root, '[data-sc-lab-shell-status]');
    if (status) status.textContent = `${moduleById(selected)?.label || 'Overview'} · ${count} specialist workspaces available`;
  }

  let scheduled = false;
  function scheduleBoot() {
    if (scheduled) return;
    scheduled = true;
    const run = () => { scheduled = false; boot(); };
    if (w.requestAnimationFrame) w.requestAnimationFrame(run); else setTimeout(run, 0);
  }

  const observer = new MutationObserver(records => {
    if (records.some(r => r.addedNodes && r.addedNodes.length)) scheduleBoot();
  });
  observer.observe(d.documentElement, { childList: true, subtree: true });
  d.addEventListener('sc-lab:safe-module-opened', scheduleBoot);
  d.addEventListener('sc-lab:workspace-module-ready', scheduleBoot);
  d.addEventListener('sc-lab:observe-feed-ready', scheduleBoot);
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', scheduleBoot, { once: true }); else scheduleBoot();

  w.SCLabUnifiedWorkspaceShellV016312Runtime = Object.freeze({
    version: VERSION,
    featureVersion: FEATURE_VERSION,
    boot: scheduleBoot,
    restoreFrontDoorVisualization,
    ensureScientificSignalsVisible,
    resolveModule,
    modules: MODULES.map(m => ({ id: m.id, label: m.label, group: m.group, selectors: m.selectors.slice() }))
  });
})(window, document);
