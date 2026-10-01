(function (w, d) {
  'use strict';

  const VERSION = '0.163.1';
  const CFG = () => w.SCLabUnifiedWorkspaceShellV01631 || {};
  const STORAGE_KEY = 'sc-lab-v01631-active-workspace';
  const RAIL_KEY = 'sc-lab-v01631-rail-collapsed';

  const MODULES = [
    { id: 'four-d', code: '4D', label: '4D Workspace', group: 'Research', selector: '[data-v01530-workspace], .sc-lab-v01530-workspace', description: 'Multidimensional modeling, linked views, scenes and project assets.' },
    { id: 'notebook', code: 'NB', label: 'Notebook & Protocol', group: 'Research', selector: '[data-v01540-workspace], .sc-lab-v01540-workspace', description: 'Reproducible protocols, notebooks, compute references and manifests.' },
    { id: 'batch', code: 'BX', label: 'Batch Experiments', group: 'Research', selector: '[data-v01550-workspace], .sc-lab-v01550-workspace', description: 'Sweeps, ensembles, deterministic trials and explicit execution handoffs.' },
    { id: 'compute', code: 'HP', label: 'Compute & HPC', group: 'Compute', selector: '[data-v01560-workspace], .sc-lab-v01560-workspace', description: 'Distributed, accelerated and scheduler-neutral execution planning.' },
    { id: 'cross-study', code: 'XS', label: 'Cross-Study', group: 'Evidence', selector: '[data-v01570-workspace], .sc-lab-v01570', description: 'Cross-study replication and descriptive meta-experiment synthesis.' },
    { id: 'replication', code: 'RN', label: 'Replication Network', group: 'Evidence', selector: '[data-v01580-workspace], .sc-lab-v01580', description: 'Independent replication nodes, plans, receipts and human review.' },
    { id: 'review', code: 'RV', label: 'Scientific Review', group: 'Evidence', selector: '[data-v01590-workspace], .sc-lab-v01590', description: 'Validation dossiers, findings, sign-off, dissent and publication handoff.' },
    { id: 'research-os', code: 'OS', label: 'Research OS', group: 'Operations', selector: '[data-v01600-workspace], .sc-lab-v01600', description: 'Human-controlled research lifecycle, packages and project command center.' },
    { id: 'programs', code: 'PG', label: 'Programs', group: 'Operations', selector: '[data-v01610-workspace], .sc-lab-v01610', description: 'Research programs, portfolios, objectives and milestones.' },
    { id: 'resources', code: 'RS', label: 'Resources', group: 'Operations', selector: '[data-v01620-workspace], .sc-lab-v01620', description: 'Cross-project dependencies, shared resources and planning scenarios.' },
    { id: 'governance', code: 'GV', label: 'Governance', group: 'Operations', selector: '[data-v01630-workspace], .sc-lab-v01630', description: 'Institutional review bodies, federation, decisions and sign-off evidence.' }
  ];

  const q = (root, sel) => root.querySelector(sel);
  const qa = (root, sel) => Array.from(root.querySelectorAll(sel));

  function moduleById(id) { return MODULES.find(m => m.id === id) || null; }
  function firstWorkspace() {
    const nodes = MODULES.map(m => d.querySelector(m.selector)).filter(Boolean);
    if (!nodes.length) return null;
    return nodes.sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_PRECEDING) ? 1 : -1)[0];
  }

  function shellMarkup() {
    const grouped = ['Research', 'Compute', 'Evidence', 'Operations'].map(group => {
      const buttons = MODULES.filter(m => m.group === group).map(m =>
        `<button type="button" class="sc-lab-v01631-nav-button" data-sc-lab-shell-open="${m.id}" data-search="${(m.label + ' ' + m.group + ' ' + m.description).toLowerCase()}" aria-selected="false"><span class="sc-lab-v01631-code">${m.code}</span><span class="sc-lab-v01631-nav-copy"><strong>${m.label}</strong><small>${m.description}</small></span></button>`
      ).join('');
      return `<div class="sc-lab-v01631-nav-group" data-group="${group.toLowerCase()}"><h4>${group}</h4>${buttons}</div>`;
    }).join('');

    const cards = [
      ['four-d', '4D Workspace', 'Model, inspect and preserve multidimensional scientific scenes.'],
      ['notebook', 'Notebook & Protocol', 'Define reproducible methods and computational records.'],
      ['compute', 'Compute & HPC', 'Plan distributed and accelerated scientific execution.'],
      ['replication', 'Replication', 'Coordinate cross-study and independent reproduction work.'],
      ['review', 'Review', 'Inspect evidence, findings, sign-off and publication readiness.'],
      ['research-os', 'Research OS', 'Coordinate the human-controlled project lifecycle.'],
      ['programs', 'Programs', 'Coordinate multiple projects and research portfolios.'],
      ['governance', 'Governance', 'Manage institutional review and federated oversight.']
    ].map(([id, title, body]) => `<button type="button" class="sc-lab-v01631-overview-card" data-sc-lab-shell-open="${id}"><span>${title}</span><small>${body}</small><b>Open workspace →</b></button>`).join('');

    return `
      <header class="sc-lab-v01631-topbar">
        <div>
          <p class="sc-lab-v01631-eyebrow">LAB / ${VERSION} · UNIFIED WORKSPACE SHELL</p>
          <h3>Scientific workspaces, one active context at a time.</h3>
          <p>Navigate specialist Lab modules without rendering the entire research operating surface as one long page.</p>
        </div>
        <div class="sc-lab-v01631-topbar-tools">
          <label>Find workspace<input type="search" data-sc-lab-shell-search placeholder="Search workspaces…" autocomplete="off"></label>
          <span data-sc-lab-shell-status>Overview · 0 available</span>
        </div>
      </header>
      <div class="sc-lab-v01631-layout">
        <aside class="sc-lab-v01631-rail" aria-label="Lab workspace navigation">
          <div class="sc-lab-v01631-rail-head">
            <button type="button" class="sc-lab-v01631-nav-button sc-lab-v01631-overview-button" data-sc-lab-shell-open="overview" data-search="overview home start recent work figures signals" aria-selected="true"><span class="sc-lab-v01631-code">OV</span><span class="sc-lab-v01631-nav-copy"><strong>Overview</strong><small>Start here and open only the workspace you need.</small></span></button>
            <button type="button" class="sc-lab-v01631-collapse" data-sc-lab-shell-collapse aria-label="Collapse workspace rail" title="Collapse workspace rail">⇤</button>
          </div>
          <nav data-sc-lab-shell-nav>${grouped}</nav>
        </aside>
        <main class="sc-lab-v01631-main">
          <section class="sc-lab-v01631-overview" data-sc-lab-shell-overview>
            <div class="sc-lab-v01631-overview-head">
              <div><p class="sc-lab-v01631-eyebrow">LAB / OVERVIEW</p><h4>Choose the research surface for the task at hand.</h4></div>
              <span>Progressive navigation · specialist state preserved</span>
            </div>
            <div class="sc-lab-v01631-overview-grid">${cards}</div>
          </section>
          <div class="sc-lab-v01631-stage" data-sc-lab-shell-stage aria-live="polite"></div>
          <details class="sc-lab-v01631-governance" data-sc-lab-shell-governance>
            <summary>Methods &amp; governance</summary>
            <div data-sc-lab-shell-governance-copy>Module-specific scientific boundaries appear here when a workspace is open.</div>
          </details>
        </main>
      </div>`;
  }

  function ensureShell() {
    let shell = d.querySelector('[data-sc-lab-unified-shell]');
    if (shell) return shell;
    const first = firstWorkspace();
    if (!first) return null;
    shell = d.createElement('section');
    shell.className = 'sc-lab-v01631-shell';
    shell.setAttribute('data-sc-lab-unified-shell', '');
    shell.innerHTML = shellMarkup();
    first.parentNode.insertBefore(shell, first);
    bindShell(shell);
    return shell;
  }

  function captureBoundary(node) {
    const candidates = qa(node, '.boundary, [class*="-boundary"]');
    const text = candidates.map(x => (x.textContent || '').trim()).filter(Boolean).join(' ');
    candidates.forEach(x => { x.hidden = true; x.setAttribute('data-sc-lab-shell-boundary-hidden', ''); });
    if (text) node.setAttribute('data-sc-lab-shell-boundary', text);
  }

  function registerModules(shell) {
    if (!shell) return 0;
    const stage = q(shell, '[data-sc-lab-shell-stage]');
    let available = 0;
    MODULES.forEach(m => {
      const node = d.querySelector(m.selector);
      const button = q(shell, `[data-sc-lab-shell-open="${m.id}"]`);
      if (!node) {
        if (button) button.disabled = true;
        return;
      }
      available += 1;
      if (button) button.disabled = false;
      if (!node.hasAttribute('data-sc-lab-shell-module')) {
        node.setAttribute('data-sc-lab-shell-module', m.id);
        node.classList.add('sc-lab-v01631-managed');
        captureBoundary(node);
        stage.appendChild(node);
      } else if (node.parentNode !== stage) {
        stage.appendChild(node);
      }
    });
    return available;
  }

  function activeBoundary(shell, id) {
    const copy = q(shell, '[data-sc-lab-shell-governance-copy]');
    if (id === 'overview') {
      copy.textContent = 'Module-specific scientific boundaries appear here when a workspace is open. Existing Lab governance, provenance and human-authorization rules remain unchanged.';
      return;
    }
    const node = q(shell, `[data-sc-lab-shell-module="${id}"]`);
    const text = node ? node.getAttribute('data-sc-lab-shell-boundary') : '';
    copy.textContent = text || 'This workspace retains its existing scientific, provenance, authorization and execution boundaries.';
  }

  function activate(shell, id, options) {
    const opts = options || {};
    if (id !== 'overview' && !moduleById(id)) id = 'overview';
    const overview = q(shell, '[data-sc-lab-shell-overview]');
    const modules = qa(shell, '[data-sc-lab-shell-module]');
    let exists = id === 'overview';
    modules.forEach(node => {
      const active = node.getAttribute('data-sc-lab-shell-module') === id;
      node.hidden = !active;
      node.classList.toggle('is-active', active);
      if (active) exists = true;
    });
    if (!exists) id = 'overview';
    overview.hidden = id !== 'overview';
    qa(shell, '[data-sc-lab-shell-open]').forEach(btn => btn.setAttribute('aria-selected', btn.getAttribute('data-sc-lab-shell-open') === id ? 'true' : 'false'));
    shell.setAttribute('data-active-workspace', id);
    const available = modules.length;
    const m = moduleById(id);
    q(shell, '[data-sc-lab-shell-status]').textContent = `${m ? m.label : 'Overview'} · ${available} available`;
    activeBoundary(shell, id);
    try { w.sessionStorage.setItem(STORAGE_KEY, id); } catch (_) {}
    d.dispatchEvent(new CustomEvent('sc-lab:workspace-shell-change', { detail: { workspace: id, version: VERSION } }));
    if (opts.focus) {
      const target = id === 'overview' ? overview : q(shell, `[data-sc-lab-shell-module="${id}"]`);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function filterNav(shell, value) {
    const term = String(value || '').trim().toLowerCase();
    qa(shell, '.sc-lab-v01631-nav-button[data-search]').forEach(btn => {
      const visible = !term || String(btn.getAttribute('data-search') || '').includes(term);
      btn.hidden = !visible;
    });
    qa(shell, '.sc-lab-v01631-nav-group').forEach(group => {
      group.hidden = !qa(group, '.sc-lab-v01631-nav-button').some(btn => !btn.hidden);
    });
  }

  function bindShell(shell) {
    if (shell.getAttribute('data-bound') === '1') return;
    shell.setAttribute('data-bound', '1');
    shell.addEventListener('click', ev => {
      const opener = ev.target.closest('[data-sc-lab-shell-open]');
      if (opener && !opener.disabled) {
        activate(shell, opener.getAttribute('data-sc-lab-shell-open'), { focus: opener.closest('.sc-lab-v01631-overview-grid') !== null });
        return;
      }
      const collapse = ev.target.closest('[data-sc-lab-shell-collapse]');
      if (collapse) {
        const collapsed = !shell.classList.contains('is-rail-collapsed');
        shell.classList.toggle('is-rail-collapsed', collapsed);
        collapse.textContent = collapsed ? '⇥' : '⇤';
        collapse.setAttribute('aria-label', collapsed ? 'Expand workspace rail' : 'Collapse workspace rail');
        try { w.sessionStorage.setItem(RAIL_KEY, collapsed ? '1' : '0'); } catch (_) {}
      }
    });
    const search = q(shell, '[data-sc-lab-shell-search]');
    search.addEventListener('input', () => filterNav(shell, search.value));
    search.addEventListener('keydown', ev => {
      if (ev.key === 'Escape') { search.value = ''; filterNav(shell, ''); search.blur(); }
    });
    try {
      if (w.sessionStorage.getItem(RAIL_KEY) === '1') {
        shell.classList.add('is-rail-collapsed');
        q(shell, '[data-sc-lab-shell-collapse]').textContent = '⇥';
      }
    } catch (_) {}
  }

  function boot() {
    const shell = ensureShell();
    if (!shell) return;
    const count = registerModules(shell);
    let selected = CFG().defaultWorkspace || 'overview';
    try { selected = w.sessionStorage.getItem(STORAGE_KEY) || selected; } catch (_) {}
    if (selected !== 'overview' && !q(shell, `[data-sc-lab-shell-module="${selected}"]`)) selected = 'overview';
    activate(shell, selected);
    q(shell, '[data-sc-lab-shell-status]').textContent = `${moduleById(selected)?.label || 'Overview'} · ${count} available`;
  }

  let scheduled = false;
  function scheduleBoot() {
    if (scheduled) return;
    scheduled = true;
    w.requestAnimationFrame(() => { scheduled = false; boot(); });
  }

  const observer = new MutationObserver(scheduleBoot);
  observer.observe(d.documentElement, { childList: true, subtree: true });
  d.addEventListener('sc-lab:safe-module-opened', scheduleBoot);
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', scheduleBoot, { once: true }); else scheduleBoot();

  w.SCLabUnifiedWorkspaceShellV01631Runtime = Object.freeze({ version: VERSION, boot: scheduleBoot, modules: MODULES.map(m => ({ id: m.id, label: m.label, group: m.group })) });
})(window, document);
