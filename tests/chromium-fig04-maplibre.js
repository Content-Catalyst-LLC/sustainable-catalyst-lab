// SC-FIG-04 Chromium harness: draws the synthetic Wexford view through the generic renderer and exercises
// layer selection, legend, time steps, comparison, integrity and Earth-observation refusals.
(async function () {
  'use strict';
  var log = [], failures = [], DIR = 'fixtures/fig04-wexford/';
  var integrity = decodeURIComponent((location.hash.match(/integrity=([^&]+)/) || [])[1] || '');
  var WORKER = '../assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js';
  var violations = [];
  document.addEventListener('securitypolicyviolation', function (e) { violations.push(e.violatedDirective + ' ' + e.blockedURI); });
  function check(cond, msg) { log.push((cond ? 'ok   ' : 'FAIL ') + msg); if (!cond) { failures.push(msg); } document.getElementById('cert-log').textContent = log.join('\n'); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  async function until(fn, ms) { for (var t = 0; t < (ms || 30000); t += 100) { if (fn()) { return true; } await wait(100); } return false; }
  async function text(path) { return (await fetch(path)).text(); }
  function file(name, t) { return { name: name, bytes: new TextEncoder().encode(t) }; }
  var api = window.SCLabFigureBundleRenderer;
  var F = window.SCLabPlotlyPreviewFIG02A, C = window.SCLabMapLibreFIG03A, G = window.SCLabMapLibreFIG04;
  try {
    check(!!(F && C && G && window.maplibregl), 'modules and MapLibre loaded');
    check(G.libraryErrors().length === 0, 'MapLibre 5.24.0 CSP build recognised: ' + G.libraryErrors().join());
    var bundleText = await text(DIR + 'wexford.bundle.json'), viewText = await text(DIR + 'wexford.map-view.json');
    var view = JSON.parse(viewText), bundle = JSON.parse(bundleText);
    check(!!api, 'generic renderer API found');

    // 1. A worker whose pinned hash is wrong is never started; the map is reported unavailable, tables stay.
    var bad = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r0 = await api.render(bad, [file('b.json', bundleText), file('v.json', viewText)], undefined,
      { maplibre: { workerUrl: WORKER, workerIntegrity: 'sha384-' + 'A'.repeat(64) } });
    var slot0 = bad.querySelector('[data-view-state]');
    check(slot0 && slot0.getAttribute('data-map-state') === 'unavailable' && /do not match the pinned SHA-384/.test(bad.textContent), 'wrong worker hash: worker not started, map unavailable');
    check(bad.querySelectorAll('table').length === 2 && bad.querySelector('.sc-lab-fig04-legend'), 'legend and tables still shown without the map');
    bad.remove();

    // 2. Verified render.
    var out = document.getElementById('main-out').appendChild(document.createElement('div'));
    out.id = 'wexford';
    var res = await api.render(out, [file('wexford.bundle.json', bundleText), file('wexford.map-view.json', viewText)], undefined,
      { maplibre: { workerUrl: WORKER, workerIntegrity: integrity } });
    var slot = out.querySelector('[data-view-state]');
    check(res.state === 'rendered' && slot.getAttribute('data-view-state') === 'rendered-maplibre', 'bundle verified and view rendered-maplibre');
    check(slot.getAttribute('data-map-state') === 'ready', 'map loaded (data-map-state ready): ' + slot.getAttribute('data-map-state') + ' ' + out.textContent.slice(0, 200));
    var canvas = slot.querySelector('canvas.maplibregl-canvas');
    check(!!canvas && canvas.width > 100, 'WebGL canvas drawn');
    check(slot.querySelector('[role=region][aria-label^="Interactive map"]'), 'map region labelled with the alt text');
    var maps = Array.prototype.slice.call(slot.querySelectorAll('.maplibregl-map'));
    check(maps.length === 1, 'one map before comparison');

    // Legend.
    var legend = slot.querySelector('.sc-lab-fig04-legend');
    var classes = Array.prototype.map.call(legend.querySelectorAll('[data-legend-layer="field-soc"] li'), function (li) { return li.textContent; });
    check(classes.join('|') === '< 26 g kg-1|26 to < 29 g kg-1|29 to < 32 g kg-1|≥ 32 g kg-1|not reported', 'graduated legend with units: ' + classes.join('|'));
    check(/not interpolated values/.test(legend.querySelector('[data-legend-layer="nitrate-heat"]').textContent), 'heat-map legend states it is a density, not interpolated values');
    check(legend.querySelectorAll('.sc-lab-fig04-swatch').length === 5 + 5 + 1, 'legend swatches drawn through CSSOM (strict CSP)');
    check(/modelled/.test(legend.textContent), 'legend states the evidence class');

    // Time controls.
    var steps = C.timeSteps(view);
    check(slot.getAttribute('data-time-step') === steps[3], 'starts on the latest quarter');
    slot.querySelector('[data-time-prev]').click(); await wait(300);
    check(slot.getAttribute('data-time-step') === steps[2] && /3 of 4/.test(slot.querySelector('[data-time-output]').textContent), 'previous moves one quarter back');
    var range = slot.querySelector('[data-time-range]');
    range.value = '0'; range.dispatchEvent(new Event('input')); await wait(300);
    check(slot.getAttribute('data-time-step') === steps[0] && slot.querySelector('[data-time-prev]').disabled, 'slider jumps to the first quarter; previous disabled');
    check(range.getAttribute('aria-valuetext') === steps[0], 'slider announces the step');

    window.__fig04 = {};

    // Layer selection.
    var toggle = slot.querySelector('[data-layer-toggle="nitrate-heat"]');
    toggle.click(); await wait(200);
    check(slot.getAttribute('data-layers-visible') === 'field-soc,nitrate-sites', 'unchecking the heat map hides it: ' + slot.getAttribute('data-layers-visible'));
    toggle.click(); await wait(200);
    check(slot.getAttribute('data-layers-visible') === 'field-soc,nitrate-heat,nitrate-sites', 'checking it again shows it');

    // Comparison.
    var cmp = slot.querySelector('[data-compare-toggle]');
    cmp.click();
    check(await until(function () { return slot.getAttribute('data-compare-map') === 'ready'; }, 30000), 'comparison map loaded');
    check(slot.querySelectorAll('.maplibregl-map').length === 2 && slot.querySelector('.sc-lab-fig04-maps').getAttribute('data-split') === 'two', 'two maps side by side');
    check(range.disabled && cmp.getAttribute('aria-pressed') === 'true', 'time slider disabled while comparing');
    var ctab = slot.querySelector('[data-comparison-table] table');
    check(ctab && ctab.querySelectorAll('tbody tr').length === 6 && /independence assumed/.test(ctab.textContent), 'comparison table: six fields with propagated uncertainty');
    await wait(800);
    window.__fig04.ready = true;
    // The driver takes a screenshot here, then sets __fig04.continue.
    await until(function () { return window.__fig04.continue; }, 60000);
    cmp.click(); await wait(300);
    check(slot.querySelectorAll('.maplibregl-map').length === 1 && !range.disabled, 'comparison off restores one map and the time slider');

    // Calculations and table.
    check(/g kg-1 yr-1 \(standard error\)/.test(slot.querySelector('.sc-lab-fig04-calculations').textContent), 'calculation result with unit and standard error');
    var dataTable = slot.querySelector('details:not([data-comparison-table]) table');
    check(dataTable.querySelectorAll('tbody tr').length === 56 && /± standard error/.test(dataTable.textContent), 'accessible table: 56 objects with uncertainty');
    check(slot.getAttribute('data-map-requests') === '0', 'MapLibre requested no resource (no tiles, glyphs, sprites)');
    check(/No basemap or imagery/.test(slot.querySelector('[data-map-attribution]').textContent), 'attribution names sources and no basemap');

    // 3. Integrity: an edited object, re-hashed into the bundle, is refused by the SI digest.
    var tampered = JSON.parse(viewText); tampered.objects[2].properties.soc = 50;
    var tText = JSON.stringify(tampered), tb = JSON.parse(bundleText);
    tb.artifacts[0].sha256 = await F.sha256Hex(F.canonical(F.parseLexical(tText)));
    tb.rendering.visualizationSpecSha256 = tb.artifacts[0].sha256;
    var tOut = document.getElementById('main-out').appendChild(document.createElement('div'));
    var r2 = await api.render(tOut, [file('b.json', JSON.stringify(tb)), file('v.json', tText)]);
    check(r2.state === 'refused' && /Site Intelligence digest/.test(tOut.textContent) && !tOut.querySelector('canvas'), 'edited SI object refused; nothing drawn');
    // Bytes that do not match the bundle artifact are not drawn.
    var r3 = await api.render(tOut, [file('b.json', bundleText), file('v.json', tText)]);
    check(r3.state !== 'rendered', 'view bytes not matching the bundle are not drawn: ' + r3.state);

    // 4. Earth observation: a Sentinel-2 layer is refused (no provider approved, nothing fetched).
    var eo = JSON.parse(viewText);
    eo.rasterLayers = [{ id: 's2', provider: 'copernicus-sentinel-2-l2a', tiles: [location.origin + '/tiles/{z}/{x}/{y}.png'], attribution: 'Contains modified Copernicus Sentinel data',
      provenance: { productId: 'x', acquiredAt: 'x', processingBaseline: 'x', tileManifestSha256: 'a'.repeat(64) } }];
    var eText = JSON.stringify(eo), eb = JSON.parse(bundleText);
    eb.artifacts[0].sha256 = await F.sha256Hex(F.canonical(F.parseLexical(eText)));
    eb.rendering.visualizationSpecSha256 = eb.artifacts[0].sha256;
    var r4 = await api.render(tOut, [file('b.json', JSON.stringify(eb)), file('v.json', eText)]);
    check(r4.state === 'refused' && /not approved/.test(tOut.textContent), 'Sentinel-2 raster layer refused (no approved provider)');
    // 5. Restricted source licence refused.
    var rb = JSON.parse(bundleText); rb.sourceRefs[1].licenceStatus = 'restricted';
    var r5 = await api.render(tOut, [file('b.json', JSON.stringify(rb)), file('v.json', viewText)]);
    check(r5.state === 'refused' && /not verified-for-use/.test(tOut.textContent), 'restricted source licence refused');
    tOut.remove();

    var res2 = performance.getEntriesByType('resource').map(function (e) { return e.name; });
    var foreign = res2.filter(function (u) { return !(u.indexOf(location.origin) === 0 || /^(blob|data):/.test(u)); });
    check(!foreign.length, 'every resource is same-origin: ' + foreign.join(' '));
    check(!res2.some(function (u) { return /tiles\//.test(u); }), 'no tile request was made');
    check(!violations.length, 'no CSP violations: ' + violations.join('; '));
  } catch (e) {
    check(false, 'exception: ' + (e && e.stack || JSON.stringify(e)));
  }
  document.body.setAttribute('data-cert', failures.length ? 'fail' : 'pass');
  window.__fig04 = window.__fig04 || {};
  window.__fig04.log = log;
}());
