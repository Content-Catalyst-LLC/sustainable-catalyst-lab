(function (W, D) {
  'use strict';
  if (W.__SCLabIntegrityV02632) return;
  W.__SCLabIntegrityV02632 = true;

  const config = W.SCLabIntegrityConfigV02632 || {};
  const errors = [];
  let server = null;
  let checkedAt = null;

  function root() {
    return D.querySelector('[data-sc-lab-release="0.26.3.2"]') || D.querySelector('[data-sc-lab-runtime="0.26.3.1"]');
  }
  function app() { return root()?.querySelector('.sc-lab-app') || D.querySelector('.sc-lab-app'); }
  function now() { return new Date().toISOString(); }
  function loadedAssets() {
    return [...D.querySelectorAll('script[src],link[rel="stylesheet"][href]')]
      .map(node => node.src || node.href)
      .filter(url => /sustainable-catalyst-lab|sc-lab/i.test(url || ''))
      .map(url => {
        try {
          const parsed = new URL(url, W.location.href);
          return { path: parsed.pathname, version: parsed.searchParams.get('ver') };
        } catch (_) { return { path: String(url), version: null }; }
      });
  }
  function clientVersions() {
    const panel = typeof W.SCLabRuntimeV02631?.status === 'function' ? W.SCLabRuntimeV02631.status() : null;
    return {
      integrity: '0.26.3.2',
      configuredPlugin: config.pluginVersion || null,
      appConfig: W.SCLabConfig?.version || null,
      panelRuntime: panel?.version || config.panelRuntimeVersion || null,
      panelPlugin: panel?.pluginVersion || null
    };
  }
  function status() {
    const r = root();
    const a = app();
    const versions = clientVersions();
    const clientConsistent = versions.integrity === versions.configuredPlugin && versions.integrity === versions.appConfig;
    return {
      version: '0.26.3.2',
      mode: 'installation-version-asset-integrity',
      clientConsistent,
      versions,
      releaseMarker: r?.dataset.scLabRelease || null,
      integrityMarker: r?.dataset.scLabIntegrityVersion || null,
      appReady: a?.dataset.scLabAppReady === '1',
      serverCheckedAt: checkedAt,
      server,
      loadedAssets: loadedAssets(),
      errors: errors.slice(-20),
      duplicateGuard: true
    };
  }
  function record(error) {
    const item = { at: now(), message: error instanceof Error ? `${error.name}: ${error.message}` : String(error) };
    errors.push(item); if (errors.length > 50) errors.shift();
    return item;
  }
  async function refresh() {
    if (!config.healthUrl) return status();
    try {
      const response = await fetch(config.healthUrl, { credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error(`Integrity endpoint returned HTTP ${response.status}`);
      server = await response.json();
      checkedAt = now();
      const r = root();
      if (r) {
        r.dataset.scLabIntegrityState = server?.state || (server?.ok ? 'verified' : 'degraded');
        r.dataset.scLabIntegrityChecked = checkedAt;
      }
      D.dispatchEvent(new CustomEvent('sc-lab:integrity-ready', { detail: status() }));
    } catch (error) {
      record(error);
      const r = root(); if (r) r.dataset.scLabIntegrityState = 'endpoint-unavailable';
    }
    return status();
  }
  function diagnostics() {
    const output = root()?.querySelector('[data-sc-lab-runtime-diagnostics]');
    if (!output) return status();
    output.hidden = false;
    output.textContent = JSON.stringify(status(), null, 2);
    return status();
  }
  function boot() {
    const r = root();
    const a = app();
    if (r) {
      r.dataset.scLabRelease = '0.26.3.2';
      r.dataset.scLabIntegrityVersion = '0.26.3.2';
      r.dataset.scLabIntegrityState = 'checking';
    }
    if (a) a.dataset.scLabReleaseVersion = '0.26.3.2';
    D.addEventListener('click', event => {
      const action = event.target.closest('[data-sc-lab-runtime-action="diagnostics"]');
      if (!action) return;
      W.setTimeout(diagnostics, 0);
    }, true);
    refresh();
  }

  W.SCLabIntegrityV02632 = { status, refresh, diagnostics };
  W.SCLabRuntimeV02632 = W.SCLabIntegrityV02632;
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot, { once: true }); else boot();
})(window, document);
