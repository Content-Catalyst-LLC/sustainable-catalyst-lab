(function (W, D) {
  'use strict';
  const VERSION = '0.82.1';
  const C = W.SCLabReleaseConsoleConfigV0821 || {};

  function esc(value) {
    return String(value == null ? '—' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }
  function restBase() { return String(C.restBase || W.SCLabConfig?.restBase || '/wp-json/sc-lab/v1/').replace(/\/$/, '') + '/'; }
  async function json(path) {
    const response = await fetch(restBase() + String(path).replace(/^\//, ''), { credentials: 'same-origin', cache: 'no-store' });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.message || body.detail || `HTTP ${response.status}`);
    return body;
  }
  function resolveReleaseVersion(runtime, fallback) {
    return runtime?.releaseVersion || runtime?.versions?.release || fallback || null;
  }
  function buildView(runtime, compute, visualization, fallback) {
    const release = resolveReleaseVersion(runtime, fallback);
    const versions = runtime?.versions || {};
    const components = runtime?.componentVersions || {};
    const verified = !!runtime?.ok && runtime?.state === 'verified' && runtime?.releaseVersionConsistent === true && runtime?.releaseConsoleVersionConsistent === true;
    return {
      release,
      verified,
      environment: W.location?.hostname === 'sustainablecatalyst.com' ? 'Production' : 'Runtime',
      components: [
        ['Lab Platform', release],
        ['WordPress Integration', versions.pluginHeader || components.wordpressIntegration],
        ['Release Manifest', versions.manifestRelease || components.releaseManifest],
        ['Visualization Engine', visualization?.engineVersion || components.visualizationEngine],
        ['Python Compute Core', compute?.version || null],
        ['Queue Gateway', components.queueGateway || null],
        ['Platform Compatibility', components.platformCompatibility || versions.platformCompatibility || null]
      ],
      integrity: [
        ['Release identity consistent', runtime?.releaseVersionConsistent === true],
        ['Release Console current', runtime?.releaseConsoleVersionConsistent === true],
        ['Manifest verified', runtime?.manifest?.verification?.ok === true],
        ['Runtime routes verified', runtime?.routeIntegrityVerified === true],
        ['WordPress installation canonical', runtime?.identity?.basenameMatches === true && runtime?.identity?.folderMatches === true],
        ['Compute backend online', compute?.ok === true && compute?.status === 'ready']
      ]
    };
  }
  function render(root, view) {
    root.dataset.scLabReleaseConsoleVersion = VERSION;
    root.dataset.scLabPublicRelease = view.release || 'unknown';
    const releaseNode = root.querySelector('[data-sc-lab-console-release]');
    const stateNode = root.querySelector('[data-sc-lab-console-state]');
    const componentsNode = root.querySelector('[data-sc-lab-console-components]');
    const integrityNode = root.querySelector('[data-sc-lab-console-integrity]');
    if (releaseNode) releaseNode.textContent = `v${view.release || 'unknown'}`;
    if (stateNode) { stateNode.textContent = `${view.environment} · ${view.verified ? 'Verified' : 'Integrity review required'}`; stateNode.dataset.state = view.verified ? 'verified' : 'review'; }
    if (componentsNode) componentsNode.innerHTML = view.components.map(([label, value]) => `<div class="sc-lab-release-console__component"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join('');
    if (integrityNode) integrityNode.innerHTML = view.integrity.map(([label, ok]) => `<div class="sc-lab-release-console__check" data-state="${ok ? 'pass' : 'fail'}"><span aria-hidden="true">${ok ? '✓' : '!'}</span><strong>${esc(label)}</strong></div>`).join('');
  }
  async function refresh(root) {
    if (!root) return;
    root.dataset.state = 'loading';
    const [runtimeResult, computeResult, visualizationResult] = await Promise.allSettled([
      json('runtime/health'), json('compute/status'), json('visualization/v0830/health')
    ]);
    const runtime = runtimeResult.status === 'fulfilled' ? runtimeResult.value : {};
    const compute = computeResult.status === 'fulfilled' ? computeResult.value : {};
    const visualization = visualizationResult.status === 'fulfilled' ? visualizationResult.value : {};
    render(root, buildView(runtime, compute, visualization, C.releaseVersion || W.SCLabConfig?.version || null));
    root.dataset.state = runtimeResult.status === 'fulfilled' ? 'ready' : 'degraded';
  }
  function init() {
    const roots = [...D.querySelectorAll('[data-sc-lab-release-console]')];
    roots.forEach((root) => refresh(root).catch(() => { root.dataset.state = 'degraded'; }));
    D.addEventListener('click', (event) => {
      if (!event.target.closest('[data-status-refresh]')) return;
      roots.forEach((root) => refresh(root).catch(() => { root.dataset.state = 'degraded'; }));
    });
  }

  W.SCLabReleaseConsoleV0821 = { version: VERSION, resolveReleaseVersion, buildView };
  if (D?.readyState === 'loading') D.addEventListener('DOMContentLoaded', init); else if (D?.querySelectorAll) init();
})(typeof window !== 'undefined' ? window : globalThis, typeof document !== 'undefined' ? document : null);
